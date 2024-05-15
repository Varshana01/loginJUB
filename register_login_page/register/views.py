import json
import base64
import mysql.connector
import logging

from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from .models import Users
from .serializers import ItemSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = ItemSerializer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
db_config = {
    'host': "108.167.185.72",
    'user': "petjubil_usrinte",
    'password': "Inter@ct!ve2024",
    'database': "petjubil_interactive",
}
def welcome(request):
  template = loader.get_template('index.html')
  return HttpResponse(template.render())


def create_user(username, email, password):
    try:
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor()
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, password))
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return True
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        return False

def check_user_exists(username):
    try:
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor()
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        cursor.close()
        db_connection.close()
        return result is not None
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        return False

@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data['username']
        email = data['email']
        password = data['password']
        password2 = data['password2']

        if password != password2:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)

        if check_user_exists(username):
            return JsonResponse({'error': 'Username already taken'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already in use'}, status=400)

        pasdencode = base64.b64encode(password.encode("utf-8")).decode("utf-8")
        if create_user(username, email, pasdencode):
            return JsonResponse({'success': 'User registered successfully'}, status=201)
        else:
            return JsonResponse({'error': 'User registration failed'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            pasdencode = base64.b64encode(password.encode("utf-8")).decode("utf-8")

            db_connection = mysql.connector.connect(**db_config)
            cursor = db_connection.cursor()
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, pasdencode))
            user_data = cursor.fetchone()
            cursor.close()
            db_connection.close()

            if user_data:
                return JsonResponse({'success': 'Login successful'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def test_db_connection(request):
    try:
        # Attempt to connect to the database
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor()
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()
        cursor.close()
        db_connection.close()

        # Return a success message
        return JsonResponse({'success': True, 'database': result[0]})
    except mysql.connector.Error as err:
        # Return an error message if the connection fails
        return JsonResponse({'success': False, 'error': str(err)})