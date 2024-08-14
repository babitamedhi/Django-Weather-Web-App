from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import datetime
from .models import user_details
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Contact

@login_required  # Ensure user is logged in
def contact(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        description = request.POST.get('description')
        
        # Get the logged-in user's email
        email = request.user.email
        
        # Save contact query with the logged-in user's email
        contact_query = Contact(name=fullname, email=email, description=description)
        contact_query.save()
        
        from_email = settings.EMAIL_HOST_USER
        
        try:
            # Use Django's email connection
            connection = get_connection()
            connection.open()
            
            # Email to site admin
            email_message = EmailMessage(
                subject=f'Website Email from {fullname}', 
                body=f'Email from: {email}\nUser Query: {description}',
                from_email=from_email,
                to=['violinamedhi2001@gmail.com'],
                connection=connection
            )
            
            # Email to user
            email_user = EmailMessage(
                subject='ABC Company',
                body=f'Hello {fullname}\nThanks for contacting us. We will resolve your query ASAP.\nThank you',
                from_email=from_email,
                to=[email],
                connection=connection
            )
            
            # Send messages
            connection.send_messages([email_message, email_user])
            connection.close()
            
            messages.info(request, "Thanks for contacting us.")
            return redirect('/contact')
        
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending email: {e}")
            
            messages.error(request, f"Error sending email: {e}")
            return redirect('/contact')
    
    return render(request, 'contact.html')


def index(request):
    return render(request, 'index.html')


def weather(request):
    result = None
    forecast = None

    if 'city' in request.GET:
        city = request.GET.get('city')
        api_key = settings.OPENWEATHERMAP_API_KEY
        weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'
        
        weather_response = requests.get(weather_url)
        forecast_response = requests.get(forecast_url)
        
        if weather_response.status_code == 200 and forecast_response.status_code == 200:
            weather_data = weather_response.json()
            forecast_data = forecast_response.json()
            
            current_time = datetime.datetime.fromtimestamp(weather_data['dt'])
            sunrise_time = datetime.datetime.fromtimestamp(weather_data['sys']['sunrise'])
            sunset_time = datetime.datetime.fromtimestamp(weather_data['sys']['sunset'])
            
            result = {
                'region': weather_data['name'],
                'temp_now': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'temp_max': weather_data['main']['temp_max'],
                'temp_min': weather_data['main']['temp_min'],
                'wind_speed': weather_data['wind']['speed'],
                'wind_deg': weather_data['wind']['deg'],
                'description': weather_data['weather'][0]['description'],
                'pressure': weather_data['main']['pressure'],
                'visibility': weather_data['visibility'],
                'feels_like': weather_data['main']['feels_like'],
                'sunrise': sunrise_time.strftime("%H:%M:%S"),
                'sunset': sunset_time.strftime("%H:%M:%S"),
                'datetime': current_time.strftime("%Y-%m-%d %H:%M:%S"),
                'icon_url': f"http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@2x.png",
            }
            
            forecast_list = forecast_data['list']
            forecast = []
            # Collect daily forecast data
            for item in forecast_list:
                date = datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                temp_max = item['main']['temp_max']
                temp_min = item['main']['temp_min']
                weather_icon = item['weather'][0]['icon']
                weather_description = item['weather'][0]['description']

                # Check if the forecast for this date has already been added
                if not any(d['date'] == date for d in forecast):
                    forecast.append({
                        'date': date,
                        'temp_max': temp_max,
                        'temp_min': temp_min,
                        'icon_url': f"http://openweathermap.org/img/wn/{weather_icon}@2x.png",
                        'description': weather_description.capitalize()  # Weather description for the day
                    })

    return render(request, 'weather.html', {'result': result, 'forecast': forecast})
    

def signUp(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect('/signUp')

        if user_details.objects.filter(username=username).exists():
            messages.error(request, "Username is taken")
            return redirect('/signUp')

        if user_details.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken")
            return redirect('/signUp')

        myuser = user_details.objects.create_user(username=username, email=email, password=pass1)
        myuser.firstname = firstname
        myuser.lastname = lastname
        myuser.save()
        messages.success(request, "Signup successful")
        return redirect('/login')

    return render(request, 'auth/signUp.html')

def handlelogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pass1']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, 'Welcome to my Website')
            return redirect('/')
        else:
            messages.warning(request, "Invalid credentials")
            return redirect('/login')
    return render(request, 'auth/login.html')


def handlelogout(request):
    logout(request)
    messages.success(request, "Logout successful")
    return redirect('/login')

def search(request):
    query = request.GET['search']
    if len(query) > 80:
        allPosts = handlelogin.objects.none()
    else:
        allPostsTitle = handlelogin.objects.filter(title__icontains=query)
        allPostsContent = handlelogin.objects.filter(content__icontains=query)
        allPosts = allPostsTitle.union(allPostsContent)
    if allPosts.count() == 0:
        messages.warning(request, "No search results found")
    params = {'allPosts': allPosts, 'query': query}        

    return render(request, 'search.html', params)
def create_user(self, username, email, password=None):
    if not username:
        raise ValueError("Users must have a username")
    if not email:
        raise ValueError("Users must have an email address")

    user = self.model(
        username=username,
        email=self.normalize_email(email),
    )
    user.set_password(password)  # This hashes the password
    user.save(using=self._db)
    return user
