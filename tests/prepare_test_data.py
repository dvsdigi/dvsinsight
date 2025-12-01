import cv2
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from insightface_engine import InsightFaceEngine

# Path to the generated image
GENERATED_IMAGE_PATH = "/Users/peeyushdhawan/.gemini/antigravity/brain/aa9bea6d-a248-4080-b6c0-1231581e13a8/test_event_photo_1764415631588.png"
OUTPUT_STUDENT = "test_student.jpg"
OUTPUT_EVENT = "test_event.jpg"

def main():
    if not os.path.exists(GENERATED_IMAGE_PATH):
        print(f"Error: {GENERATED_IMAGE_PATH} not found.")
        return

    print("Initializing engine...")
    engine = InsightFaceEngine()
    engine.prepare()

    print(f"Reading {GENERATED_IMAGE_PATH}...")
    img = cv2.imread(GENERATED_IMAGE_PATH)
    if img is None:
        print("Failed to read image.")
        return

    print("Detecting faces...")
    faces = engine.get_faces(img)
    print(f"Found {len(faces)} faces.")

    if len(faces) == 0:
        print("No faces found!")
        return

    # Use the first face
    face = faces[0]
    bbox = face['bbox']
    x1, y1, x2, y2 = [int(b) for b in bbox]
    
    # Add some padding
    h, w, _ = img.shape
    pad_x = int((x2 - x1) * 0.2)
    pad_y = int((y2 - y1) * 0.2)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)

    face_img = img[y1:y2, x1:x2]
    
    print(f"Saving {OUTPUT_STUDENT}...")
    cv2.imwrite(OUTPUT_STUDENT, face_img)
    
    print(f"Saving {OUTPUT_EVENT}...")
    cv2.imwrite(OUTPUT_EVENT, img)
    print("Done.")

if __name__ == "__main__":
    main()
