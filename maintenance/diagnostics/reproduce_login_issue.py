import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_subdomain_login():
    c = Client()
    # Test on eduscope.localhost:8000
    subdomain = "eduscope.localhost"
    login_url = "/login/"
    
    print(f"Testing GET {login_url} on {subdomain}...")
    response = c.get(login_url, HTTP_HOST=subdomain)
    
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        print(f"Current search_path: {cursor.fetchone()[0]}")
    
    print(f"GET Response: {response.status_code}")
    
    if response.status_code == 200:
        print("Login page loaded successfully.")
        
        # Try to login with our new test user
        username = 'testadmin'
        password = 'password123'
        print(f"Attempting login as {username}...")
        response = c.post(login_url, {
            'username': username,
            'password': password
        }, HTTP_HOST=subdomain)
        print(f"POST Response: {response.status_code}")
        
        if response.status_code == 302:
            print(f"Login SUCCESS! Redirected to: {response.url}")
        else:
            print(f"Login FAILED (Status {response.status_code})")
            print(f"Response Content Snippet: {response.content[:500].decode('utf-8', 'ignore')}")

if __name__ == "__main__":
    test_subdomain_login()
