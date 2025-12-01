import requests
import os

BASE_URL = "http://localhost:8000"
STUDENT_IMG = "test_student.jpg"
EVENT_IMG = "test_event.jpg"
STUDENT_ID = "test_user_01"

def test_enroll():
    print(f"Enrolling student {STUDENT_ID}...")
    url = f"{BASE_URL}/students/enroll"
    files = {
        'file': open(STUDENT_IMG, 'rb')
    }
    data = {
        'student_id': STUDENT_ID,
        'student_name': "Test User"
    }
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Enrollment successful:", response.json())
        else:
            print("Enrollment failed:", response.text)
    except Exception as e:
        print(f"Error enrolling: {e}")

def test_upload():
    print(f"Uploading event photo...")
    url = f"{BASE_URL}/photos/upload"
    files = [
        ('files', (EVENT_IMG, open(EVENT_IMG, 'rb'), 'image/jpeg'))
    ]
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            print("Upload successful:", response.json())
            results = response.json().get('results', [])
            for res in results:
                print(f"File: {res['filename']}")
                print(f"Detected faces: {res['detected_faces']}")
                print(f"Matched students: {res['matched_students']}")
                if STUDENT_ID in res['matched_students']:
                    print("SUCCESS: Student matched!")
                else:
                    print("WARNING: Student NOT matched.")
        else:
            print("Upload failed:", response.text)
    except Exception as e:
        print(f"Error uploading: {e}")

if __name__ == "__main__":
    if not os.path.exists(STUDENT_IMG) or not os.path.exists(EVENT_IMG):
        print("Test images not found. Run prepare_test_data.py first.")
    else:
        test_enroll()
        test_upload()
