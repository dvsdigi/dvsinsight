import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
import os
import numpy as np
import cv2

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main import app

class TestGallery(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('routers.gallery.cloudinary.uploader.upload')
    @patch('routers.gallery.collection')
    @patch('routers.gallery.get_engine')
    def test_upload_gallery_image(self, mock_get_engine, mock_collection, mock_upload):
        # Mock Engine
        mock_engine = MagicMock()
        mock_engine.get_faces.return_value = [{'embedding': [0.1, 0.2]}]
        mock_get_engine.return_value = mock_engine

        # Mock Cloudinary
        mock_upload.return_value = {
            "secure_url": "http://cloudinary.com/img.jpg",
            "public_id": "img123"
        }

        # Create dummy image
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        success, encoded_img = cv2.imencode('.jpg', dummy_img)
        
        files = {'files': ('test.jpg', encoded_img.tobytes(), 'image/jpeg')}
        
        response = self.client.post("/gallery/upload", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['status'], 'success')
        self.assertEqual(data['results'][0]['url'], "http://cloudinary.com/img.jpg")
        
        # Verify DB insert
        mock_collection.insert_one.assert_called_once()
        args, _ = mock_collection.insert_one.call_args
        self.assertEqual(args[0]['imageUrl'], "http://cloudinary.com/img.jpg")

    @patch('routers.gallery.collection')
    def test_list_gallery_images(self, mock_collection):
        # Mock DB Cursor
        mock_cursor = [
            {
                "_id": "1",
                "imageUrl": "http://img1.jpg",
                "filename": "img1.jpg",
                "schoolId": "default_school_id"
            }
        ]
        mock_collection.find.return_value = mock_cursor

        response = self.client.get("/gallery/list")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['images']), 1)
        self.assertEqual(data['images'][0]['imageUrl'], "http://img1.jpg")

if __name__ == '__main__':
    unittest.main()
