from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Chat, Message
import requests
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('chat')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def chat_view(request):
    chats = Chat.objects.filter(user=request.user)
    return render(request, 'chat/chat.html', {'chats': chats})

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            chat_id = data.get('chat_id')
            
            logger.info(f"Received message: {message}")
            logger.info(f"Chat ID: {chat_id}")
            
            if not message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            if not chat_id:
                chat = Chat.objects.create(user=request.user)
            else:
                chat = Chat.objects.get(id=chat_id, user=request.user)
            
            # Save user message
            Message.objects.create(chat=chat, content=message, is_user=True)
            
            # Get API key from environment
            api_key = os.getenv('API_KEY')
            if not api_key:
                logger.error("API key not found in environment variables")
                return JsonResponse({'error': 'API key not configured'}, status=500)
            
            # Make API request
            api_url = "https://lang.coonect.tech/api/v1/run/efd48072-166c-4352-b5d6-08e8d61c1d65?stream=false"
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': api_key
            }
            payload = {
                "input_value": message,
                "output_type": "chat",
                "input_type": "chat",
                "tweaks": {
                    "ChatInput-claUz": {},
                    "ChatOutput-CtzBH": {},
                    "ParseData-MlZqw": {},
                    "File-cZdfl": {},
                    "Prompt-Lwx1C": {},
                    "GoogleGenerativeAIModel-89crv": {},
                    "StoreMessage-mgbGC": {},
                    "Memory-d4tqq": {}
                }
            }
            
            logger.info(f"Sending request to API with payload: {json.dumps(payload)}")
            
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"API Response: {json.dumps(response_data)}")
            
            # Extract the message from the complex response structure
            try:
                # Navigate through the response structure to find the message
                outputs = response_data.get('outputs', [])
                if outputs:
                    first_output = outputs[0]
                    if 'outputs' in first_output:
                        for output in first_output['outputs']:
                            if 'results' in output and 'message' in output['results']:
                                message_data = output['results']['message']
                                if isinstance(message_data, dict) and 'text' in message_data:
                                    assistant_message = message_data['text']
                                    break
                                elif isinstance(message_data, dict) and 'data' in message_data:
                                    assistant_message = message_data['data']['text']
                                    break
                
                if not assistant_message:
                    raise ValueError("Could not find message in API response")
                
                # Save assistant response
                Message.objects.create(chat=chat, content=assistant_message, is_user=False)
                
                return JsonResponse({
                    'response': assistant_message,
                    'chat_id': chat.id
                })
                
            except (KeyError, ValueError) as e:
                logger.error(f"Error parsing API response: {str(e)}")
                return JsonResponse({
                    'error': 'Error parsing API response',
                    'details': str(e)
                }, status=500)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Chat.DoesNotExist:
            logger.error(f"Chat not found: {chat_id}")
            return JsonResponse({'error': 'Chat not found'}, status=404)
        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
