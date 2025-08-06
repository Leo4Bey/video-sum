from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import ChatSession, Message
from django.contrib import messages
from django.http import JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
from google import genai
import re
from django.shortcuts import get_object_or_404

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client()

def create_title(text):
    text = f"{text[:30]}..."
    return text

@login_required
def chat_view(request, chat_id):
    chat_session_obj = get_object_or_404(ChatSession, id=chat_id, user=request.user)

    if request.method == 'POST':
        message = request.POST.get('deneme')
        print(f"Gelen mesaj: {message}")

        try:
            chat_session = client.chats.create(
                model="gemini-2.5-flash",
                history=[]
            )
            gemini_response = chat_session.send_message(f"{chat_session_obj.transcript_text} metnine göre bu soruya cevap ver: {message} eğer sorunun cevabı metinde yoksa kendin cevap ver")
            gemini_reply = gemini_response.text

            Message.objects.create(
                chat_session=chat_session_obj,
                sender='user',
                content=message
            )

            Message.objects.create(
                chat_session=chat_session_obj,
                sender='bot',
                content=gemini_reply
            )

        except Exception as e:
            print(f"An error occurred calling Gemini: {e}")
            return JsonResponse({
                'status': 'error',
                'bot_reply': 'Üzgünüm, şu anda yanıt oluşturulamadı.'
            }, status=500)

        return JsonResponse({
            'status': 'success',
            'bot_reply': gemini_reply
        })
    
    history = Message.objects.filter(
        chat_session=chat_session_obj
    ).order_by('timestamp')

    user_chats = ChatSession.objects.filter(user_id=request.user.id).order_by('-created_at')
    current_chat = ChatSession.objects.get(id=chat_id)

    return render(request, 'chat.html', {
        'reply': '',
        'history': history,
        'user_chats': user_chats,
        'current_chat': current_chat
    })


def get_transcript(video_id):
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=["tr"], preserve_formatting=False)

    full_text = " ".join([snippet.text.strip() for snippet in transcript])

    # Temizlik
    clean_text = full_text.replace("  ", " ").replace("\n", " ").strip()
    clean_text = clean_text.replace("[Müzik]", "").strip()

    return clean_text


YOUTUBE_URL_REGEX = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})'

@login_required
def home_view(request):
    if request.method == 'POST':
        video_url = request.POST.get('deneme')
        print(f"Gelen video URL: {video_url}")
        
        match = re.search(YOUTUBE_URL_REGEX, video_url)
        if match:
            video_id = match.group(1)
            print(f"Geçerli YouTube videosu. Video ID: {video_id}")
            try:
                transcript = get_transcript(video_id)
                chat_title = create_title(transcript)
                chat = ChatSession.objects.create(
                    user=request.user,
                    video_id=video_id,
                    transcript_text=transcript,
                    title=chat_title
                )

                return redirect(f'/chat/{chat.id}')
            
            except Exception as e:
                messages.error(request, f'Video özetleme hatası: {str(e)}')
                print(f"Hata: {str(e)}")


        else:
            messages.error(request, 'Geçersiz YouTube video URL')
            print("Hata: YouTube video ID bulunamadı")

    user_chats = ChatSession.objects.filter(user_id=request.user.id).order_by('-created_at')

    return render(request, 'index.html', {'user_chats': user_chats})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('your_name')
        password = request.POST.get('your_pass')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"Authenticated user: {user.username}")
            login(request, user)
            return redirect('home')
        else:
            print("Authentication failed")
            messages.error(request, 'Hatalı kullanıcı adı ya da şifre')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


#todo: oturum açıldığında kullanıcının sohbetleri gösterilecek oradan istediği sohbeti seçip konuşmaya devam edebilecek
#todo: kullanıcı yine aynı sayfadan yeni bir sohbet başlatabilcek yeni sohbette kaynak için youtube video linki istenicek