import cv2
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from insightface_engine import InsightFaceEngine

# Paths to the generated images
GROUP_A_PATH = "/Users/peeyushdhawan/.gemini/antigravity/brain/aa9bea6d-a248-4080-b6c0-1231581e13a8/group_photo_a_1764417296837.png"
GROUP_B_PATH = "/Users/peeyushdhawan/.gemini/antigravity/brain/aa9bea6d-a248-4080-b6c0-1231581e13a8/group_photo_b_1764417319858.png"

OUTPUT_GROUP_A = "test_group_a.jpg"
OUTPUT_GROUP_B = "test_group_b.jpg"

def save_face(img, face, filename):
    bbox = face['bbox']
    x1, y1, x2, y2 = [int(b) for b in bbox]
    h, w, _ = img.shape
    pad_x = int((x2 - x1) * 0.2)
    pad_y = int((y2 - y1) * 0.2)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)
    face_img = img[y1:y2, x1:x2]
    cv2.imwrite(filename, face_img)
    print(f"Saved {filename}")

def main():
    print("Initializing engine...")
    engine = InsightFaceEngine()
    engine.prepare()

    # Process Group A
    if os.path.exists(GROUP_A_PATH):
        print(f"Processing {GROUP_A_PATH}...")
        img_a = cv2.imread(GROUP_A_PATH)
        faces_a = engine.get_faces(img_a)
        print(f"Found {len(faces_a)} faces in Group A.")
        
        # Save full group image
        cv2.imwrite(OUTPUT_GROUP_A, img_a)
        
        # Save first 2 faces as students
        if len(faces_a) >= 2:
            save_face(img_a, faces_a[0], "ref_student_1.jpg")
            save_face(img_a, faces_a[1], "ref_student_2.jpg")
        else:
            print("Not enough faces in Group A to extract 2 students.")
    else:
        print(f"Error: {GROUP_A_PATH} not found.")

    # Process Group B
    if os.path.exists(GROUP_B_PATH):
        print(f"Processing {GROUP_B_PATH}...")
        img_b = cv2.imread(GROUP_B_PATH)
        faces_b = engine.get_faces(img_b)
        print(f"Found {len(faces_b)} faces in Group B.")
        
        # Save full group image
        cv2.imwrite(OUTPUT_GROUP_B, img_b)
        
        # Save first face as student 3
        if len(faces_b) >= 1:
            save_face(img_b, faces_b[0], "ref_student_3.jpg")
        else:
            print("Not enough faces in Group B to extract student.")
    else:
        print(f"Error: {GROUP_B_PATH} not found.")

    print("Done.")

if __name__ == "__main__":
    main()
