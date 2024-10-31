"""
Manual test script for authentication system.
Run this script to test the authentication flow manually.
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_auth_flow():
    # Test data
    user_data = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }

    # 1. Register new user
    print("\n1. Testing Registration...")
    register_response = requests.post(
        f'{BASE_URL}/users/register/',
        json=user_data
    )
    print(f"Registration Status: {register_response.status_code}")
    print(f"Response: {register_response.json()}")

    # 2. Login to get tokens
    print("\n2. Testing Login...")
    login_response = requests.post(
        f'{BASE_URL}/users/token/',
        json={
            'email': user_data['email'],
            'password': user_data['password']
        }
    )
    print(f"Login Status: {login_response.status_code}")
    tokens = login_response.json()
    print(f"Tokens: {tokens}")

    if 'access' not in tokens:
        print("Login failed! Stopping tests.")
        return

    # Setup headers with token
    headers = {
        'Authorization': f"Bearer {tokens['access']}",
        'Content-Type': 'application/json'
    }

    # 3. Get user profile
    print("\n3. Testing Profile Retrieval...")
    profile_response = requests.get(
        f'{BASE_URL}/users/me/',
        headers=headers
    )
    print(f"Profile Status: {profile_response.status_code}")
    print(f"Profile Data: {profile_response.json()}")

    # 4. Update profile
    print("\n4. Testing Profile Update...")
    update_data = {
        'department': 'IT',
        'position': 'Developer',
        'bio': 'Test bio'
    }
    update_response = requests.patch(
        f'{BASE_URL}/users/profiles/',
        headers=headers,
        json=update_data
    )
    print(f"Update Status: {update_response.status_code}")
    print(f"Updated Data: {update_response.json()}")

if __name__ == "__main__":
    test_auth_flow()