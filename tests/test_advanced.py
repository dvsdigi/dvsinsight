import requests
import os
import time

BASE_URL = "http://localhost:8000"

# Test Data
STUDENTS = [
    {"id": "student_01", "name": "Student One", "img": "ref_student_1.jpg"},
    {"id": "student_02", "name": "Student Two", "img": "ref_student_2.jpg"},
    {"id": "student_03", "name": "Student Three", "img": "ref_student_3.jpg"}
]

GROUPS = [
    {"img": "test_group_a.jpg", "expected": ["student_01", "student_02"]},
    {"img": "test_group_b.jpg", "expected": ["student_03"]}
]

def enroll_student(student):
    print(f"Enrolling {student['name']} ({student['id']})...")
    url = f"{BASE_URL}/students/enroll"
    if not os.path.exists(student['img']):
        print(f"Error: {student['img']} not found.")
        return False
        
    files = {'file': open(student['img'], 'rb')}
    data = {'student_id': student['id'], 'student_name': student['name']}
    
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("  Success")
            return True
        else:
            print(f"  Failed: {response.text}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_group_upload(group):
    print(f"Uploading {group['img']}...")
    url = f"{BASE_URL}/photos/upload"
    if not os.path.exists(group['img']):
        print(f"Error: {group['img']} not found.")
        return

    files = [('files', (group['img'], open(group['img'], 'rb'), 'image/jpeg'))]
    
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            results = response.json().get('results', [])
            for res in results:
                print(f"  Detected faces: {res['detected_faces']}")
                matched = res['matched_students']
                print(f"  Matched: {matched}")
                
                # Verification
                missing = [s for s in group['expected'] if s not in matched]
                unexpected = [s for s in matched if s not in group['expected']]
                
                if not missing and not unexpected:
                    print("  [PASS] Perfect match!")
                else:
                    if missing: print(f"  [FAIL] Missing expected: {missing}")
                    if unexpected: print(f"  [WARN] Unexpected match: {unexpected}")
                    
        else:
            print(f"  Failed: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    print("=== Starting Advanced Test ===")
    
    # 1. Enroll all students
    for s in STUDENTS:
        enroll_student(s)
        
    print("\n=== Testing Group Photos ===")
    
    # 2. Test Group Uploads
    for g in GROUPS:
        test_group_upload(g)

if __name__ == "__main__":
    main()
