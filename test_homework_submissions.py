"""
Script to test the homework submissions page.
"""
import requests
import sys
from bs4 import BeautifulSoup

# Base URL
BASE_URL = 'http://127.0.0.1:5007'

def login(session, username, password):
    """Log in to the application"""
    # Get the login page to get the CSRF token
    response = session.get(f'{BASE_URL}/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    # Log in
    login_data = {
        'csrf_token': csrf_token,
        'username': username,
        'password': password
    }
    response = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=True)

    print(f"Login response URL: {response.url}")
    print(f"Login response status code: {response.status_code}")

    # Check if we're redirected to the dashboard
    if '/dashboard' in response.url:
        print(f"Successfully logged in as {username}")
        return True
    else:
        print(f"Failed to log in as {username}")
        print(f"Response text: {response.text[:500]}...")  # Print first 500 chars of response
        return False

def check_homework_submissions(session, homework_id):
    """Check the homework submissions page"""
    response = session.get(f'{BASE_URL}/teacher/homeworks/{homework_id}/submissions')

    if response.status_code == 200:
        print(f"Successfully accessed homework submissions page for homework ID {homework_id}")

        # Check if the page contains the assigned date
        soup = BeautifulSoup(response.text, 'html.parser')
        assigned_date = soup.find(string=lambda text: 'Assigned Date' in text if text else False)

        if assigned_date:
            parent = assigned_date.parent
            print(f"Assigned Date: {parent.get_text()}")
        else:
            print("Could not find assigned date on the page")

        return True
    else:
        print(f"Failed to access homework submissions page for homework ID {homework_id}")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Main function to test the homework submissions page"""
    # Create a session
    session = requests.Session()

    # Log in as Rajkumar
    if not login(session, 'rajkumar', 'teacher123'):
        return

    # Check homework submissions for homework ID 1
    check_homework_submissions(session, 1)

if __name__ == "__main__":
    main()
