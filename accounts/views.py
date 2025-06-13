from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
import google.generativeai as genai
from dotenv import load_dotenv
from .models import Article
from django.http import HttpResponse
from django.core.files.storage import default_storage
import os
from django.utils.text import slugify
import uuid
from .models import SearchHistory
from .models import UserProfile
from functools import wraps
import requests


def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # <--- add this check
            profile = UserProfile.objects.get(user=request.user)
            if profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('unauthorized')
        return wrapper
    return decorator



load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyBkVt6OpuZIKsGOSaoTxWOERqHA8403wP8"))
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")


@login_required
def workflow_view(request):
    return render(request, 'workflow.html')


def home_view(request):
    return render(request, 'home.html')

def landing_page_view(request):
    return render(request, 'main_home.html') 


def signup_view(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not recaptcha_response:
            return render(request, 'signup.html', {'error': 'Please complete the reCAPTCHA.'})

        data = {
            'secret': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            return render(request, 'signup.html', {'error': 'Invalid reCAPTCHA. Please try again.'})

        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST['role']

        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match.'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists.'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(user=user, role=role)

        return redirect('login')  # 🔁 Redirect to login page after signup

    return render(request, 'signup.html')




def login_view(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not recaptcha_response:
            return render(request, 'login.html', {'error': 'Please complete the reCAPTCHA.'})

        data = {
            'secret': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            return render(request, 'login.html', {'error': 'Invalid reCAPTCHA. Please try again.'})
        username = request.POST['username']
        password = request.POST['password']
        selected_role = request.POST['role']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role != selected_role:
                    return render(request, 'login.html', {'error': 'Role mismatch. Please select the correct role.'})
            except UserProfile.DoesNotExist:
                return render(request, 'login.html', {'error': 'No role assigned. Contact admin.'})

            login(request, user)

            if selected_role == 'Admin':
                return redirect('admin_dashboard')
            else:
                return redirect('workflow')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def generate_view(request):
    if request.method == 'POST':
        keywords = request.POST.get('keywords')
        article_type = request.POST.get('article_type')
        uploaded_file = request.FILES.get('upload_file')


        try:
            language = request.POST.get('language', 'English')  # Default to English
            #prompt = f"Write a {article_type.lower()} article in {language} about: {keywords}"
            prompt = f"Write a {article_type.lower()} article in {language} about: {keywords}. The article should be approximately 750 words long."
            response = model.generate_content(prompt)
            content = response.text.strip()
            title = f"A {article_type} article generated for the topic: {keywords}"
            title = title[:100]
            summary = " ".join(content.split()[:160]) + "..." if len(content.split()) > 160 else content
            article = Article.objects.create(
            user=request.user,
            title=title,
            keywords=keywords,  
            article_type=article_type,
            content=content,
            summary=summary
            )
            SearchHistory.objects.create(user=request.user, query=keywords, content_id=article.id)


            return render(request, 'generate_result.html', {
                'title': title,
                'article_type': article_type,
                'summary': summary,
                'content': content,
                'article': article ,
                'language': language
            })
        except Exception as e:
            return render(request, 'generate_result.html', {
            'title': f"{article_type} Article",
            'article_type': article_type,
            'summary': '',
            'content': f"Error generating content: {str(e)}",
            'article': None  # <-- Add this
        })


    return render(request, 'generate.html')


@login_required(login_url='login')
def convert_pdf(request, article_id):
    article = Article.objects.get(id=article_id, user=request.user)
    template = get_template("article_pdf.html")
    html = template.render({"article": article})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=article_{article.id}.pdf"
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation failed.")
    return response


@login_required(login_url='login')
def image_generate_view(request):
    article = None
    image_url = None
    generated_text = None
    prompt_text = ''

    if request.method == "POST":
        image_file = request.FILES.get('image')
        prompt_text = request.POST.get('prompt_text', '').strip()

        if not image_file:
            return render(request, 'generate_from_image.html', {
                'error': 'Please upload an image.'
            })

        unique_filename = f"{uuid.uuid4().hex}_{slugify(image_file.name)}"
        upload_path = f"uploads/{unique_filename}"  
        file_path = default_storage.save(upload_path, image_file)
        image_url = default_storage.url(file_path)

        try:
            image_bytes = image_file.read()
            image_file.seek(0)
            response = model.generate_content(
                contents=[
                    {
                        "inline_data": {
                            "mime_type": image_file.content_type,
                            "data": image_bytes
                        }
                    },
                    {"text": prompt_text or "Write a listicle based on this image."}
                ]
            )
            generated_text = response.text

            # Save Article object for PDF download
            title = f"Listicle generated from image"
            title = title[:250]  # enforce max length
            summary = " ".join(generated_text.split()[:160]) + "..." if len(generated_text.split()) > 160 else generated_text

            article = Article.objects.create(
                user=request.user,
                title=title,
                keywords=prompt_text,
                article_type="Listicle from Image",
                content=generated_text,
                summary=summary
            )
            SearchHistory.objects.create(user=request.user, query=prompt_text, content_id=article.id)


        except Exception as e:
            generated_text = f"Error generating content: {str(e)}"

    return render(request, 'generate_from_image.html', {
        'generated_text': generated_text,
        'image_url': image_url,
        'prompt_text': prompt_text,
        'article': article
    })

@login_required(login_url='login')
def recents(request):
    searches = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return render(request, 'recents.html', {'searches': searches})

@login_required(login_url='login')
def open_content(request, content_id):
    article = get_object_or_404(Article, pk=content_id)
    return render(request, 'article_detail.html', {'article': article})

@login_required(login_url='login')
def search_view(request):
    query = request.GET.get('q')
    article = None
    if query:
        # Your actual search logic here to get article(s)
        article = Article.objects.filter(title__icontains=query).first()

    if request.user.is_authenticated and article:
        SearchHistory.objects.create(user=request.user, query=query, content_id=article.id)

    return render(request, 'search_results.html', {'article': article, 'query': query})

def suggest_keywords(request):
    query = request.GET.get('q', '').strip()
    suggestions = []

    if query:
        # Step 1: Fetch similar past queries from SearchHistory
        previous = SearchHistory.objects.filter(
            query__icontains=query
        ).values_list('query', flat=True).distinct()[:5]
        suggestions = list(previous)

        # Step 2: Use Gemini to expand suggestions if needed
        if len(suggestions) < 5:
            try:
                prompt = f"Suggest 10 SEO-friendly keywords related to '{query}'. Return only the keywords as a comma-separated list."
                response = model.generate_content(prompt)
                ai_suggestions = response.text.strip()

                # Convert to list (assuming comma-separated)
                ai_keywords = [kw.strip() for kw in ai_suggestions.split(",") if kw.strip()]
                suggestions.extend([kw for kw in ai_keywords if kw not in suggestions])

                # Limit to 10
                suggestions = suggestions[:10]
            except Exception as e:
                suggestions.append(f"Error: {str(e)}")

    return JsonResponse({'suggestions': suggestions})


@login_required(login_url='login')
@role_required(['Admin'])
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def unauthorized_view(request):
    return render(request, 'unauthorized.html')
