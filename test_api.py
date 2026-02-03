import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

url = os.environ.get('EXTERNAL_API_BASE_URL')
token = os.environ.get('JWT_TOKEN')
student_id = "374c655e-c331-43b4-b4fe-4bd0550e9aee"

print(f"URL: {url}")
print(f"Token length: {len(token) if token else 0}")

headers = {"Authorization": f"Bearer {token}"}
params = {"studentId": student_id}

try:
    # Use allow_redirects=False to see if it redirects
    response = requests.get(url, headers=headers, params=params, timeout=10, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    print(f"Location Header: {response.headers.get('Location')}")
    
    if response.status_code == 302 or response.status_code == 301:
        print(f"Redirected to: {response.headers.get('Location')}")
        # Follow manually
        new_url = response.headers.get('Location')
        response = requests.get(new_url, headers=headers, timeout=10)
        print(f"Followed Status Code: {response.status_code}")
        print(f"Followed URL: {response.url}")
        print(f"Response: {response.text[:200]}")
    else:
        print(f"Final URL: {response.url}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.json() if response.status_code == 200 else response.text}")
        
except Exception as e:
    print(f"Error: {e}")
