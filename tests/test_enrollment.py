import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os
import numpy as np
import cv2

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main import app

class TestEnrollment(unittest.TestCase):
    def setUp(self):
        os.environ['EXTERNAL_API_BASE_URL'] = 'http://test-api.com'
        # Reload the module to pick up the env var change if it was read at module level
        # However, in enrollment.py it is read at module level: EXTERNAL_API_BASE_URL = ...
        # So changing os.environ here might be too late if we already imported it.
        # We need to patch the variable in the module.
        self.client = TestClient(app)

    @patch('routers.enrollment.requests.get')
    @patch('routers.enrollment.EXTERNAL_API_BASE_URL', 'http://test-api.com')
    def test_fetch_student(self, mock_get):
        # Mock external API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Mock returning a list for the filter query
        mock_response.json.return_value = [{
            "id": "123",
            "name": "Test User",
            "photoUrl": "http://example.com/photo.jpg",
            "schoolId": "SCH-001"
        }]
        mock_get.return_value = mock_response

        response = self.client.get("/enroll/fetch/123")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['student_id'], "123")
        self.assertEqual(data['student_name'], "Test User")

    @patch('routers.enrollment.collection')
    @patch('routers.enrollment.requests.get')
    @patch('routers.enrollment.get_engine')
    def test_save_student(self, mock_get_engine, mock_requests_get, mock_collection):
        # Mock Image Download
        mock_response = MagicMock()
        mock_response.status_code = 200
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        success, encoded_img = cv2.imencode('.jpg', dummy_img)
        mock_response.content = encoded_img.tobytes()
        mock_requests_get.return_value = mock_response

        # Mock Engine
        mock_engine = MagicMock()
        mock_engine.get_faces.return_value = [{'embedding': [0.1, 0.2]}]
        mock_get_engine.return_value = mock_engine

        # Mock DB
        mock_collection.update_one.return_value = MagicMock(upserted_id="new_id")

        response = self.client.post("/enroll/save", data={
            "student_id": "123",
            "student_name": "Test User",
            "photo_url": "http://example.com/photo.jpg",
            "school_id": "SCH-001"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json()['status'])
        mock_collection.update_one.assert_called_once()

if __name__ == '__main__':
    unittest.main()
