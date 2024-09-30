from django.shortcuts import render

# Create your views here.
import json
import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Connect to Redis
redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0)
from django.shortcuts import render

def chat_page(request):
    return render(request, 'chat/chat.html')

from asgiref.sync import sync_to_async

@csrf_exempt
async def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sender = data['sender']
            receiver = data['receiver']
            message = data['message']

            # Create a message payload
            message_payload = json.dumps({
                'sender': sender,
                'message': message
            })
            
            await save_msg(message)
            
            # Publish message to the Redis channel for the receiver
            redis_instance.publish(f"chat_1", message_payload)
            
            return JsonResponse({"status": "Message sent successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "Error", "message": str(e)}, status=500)


from django.http import StreamingHttpResponse
from .models import ChatMessage

def stream_messages(request, channel):
    pubsub = redis_instance.pubsub()
    pubsub.subscribe("chat_1")

    def event_stream():
        for message in pubsub.listen():
            if message['type'] == 'message':
                message_data = message['data'].decode('utf-8')
                yield f"data: {message_data}\n\n"
                
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response

async def save_msg(msg):
    try:
        print(f"Saving message: {msg}", flush=True)
        chat_obj = await ChatMessage.objects.acreate(
            sender="sender",
            receiver="receiver",
            message=msg
        )
        await chat_obj.asave()
    except Exception as e:
        print(f"Error saving message: {e}")