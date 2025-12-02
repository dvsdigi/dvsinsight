import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import numpy as np

# Add app directory to path so we can import mongo_enroll
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mongo_enroll import main, download_image_from_url

class TestMongoEnroll(unittest.TestCase):

    @patch('mongo_enroll.MongoClient')
    @patch('mongo_enroll.InsightFaceEngine')
    @patch('mongo_enroll.requests.get')
    def test_main_flow(self, mock_get, mock_engine_cls, mock_mongo_cls):
        # Mock MongoDB
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_mongo_cls.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        # Mock DB Data
        mock_cursor = [
            {
                '_id': '1',
                'student_id': '101',
                'student_name': 'Test Student',
                'photo_url': 'http://example.com/photo.jpg'
            }
        ]
        mock_collection.find.return_value = mock_cursor

        # Mock Image Download
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Create a dummy small image
        import cv2
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        success, encoded_img = cv2.imencode('.jpg', dummy_img)
        mock_response.content = encoded_img.tobytes()
        mock_get.return_value = mock_response

        # Mock Engine
        mock_engine_instance = MagicMock()
        mock_engine_cls.return_value = mock_engine_instance
        
        # Mock Face Detection
        mock_face = MagicMock()
        mock_face.embedding = np.random.rand(512).astype(float) # Dummy embedding
        # The engine returns a list of dicts in our wrapper, wait, let's check wrapper
        # The wrapper returns list of dicts: {'bbox': ..., 'embedding': ...}
        # BUT, in mongo_enroll.py we are using InsightFaceEngine from insightface_engine.py
        # Let's check how mongo_enroll uses it: faces = engine.get_faces(img)
        # And get_faces returns list of dicts.
        
        mock_engine_instance.get_faces.return_value = [
            {'embedding': [0.1, 0.2, 0.3]}
        ]

        # Run main
        main()

        # Assertions
        # 1. Check DB connection
        mock_mongo_cls.assert_called_once()
        
        # 2. Check Query
        mock_collection.find.assert_called_once()
        
        # 3. Check Update
        mock_collection.update_one.assert_called_once()
        args, _ = mock_collection.update_one.call_args
        self.assertEqual(args[0], {'_id': '1'})
        self.assertIn('$set', args[1])
        self.assertIn('vector_embedding', args[1]['$set'])
        self.assertEqual(args[1]['$set']['vector_embedding'], [0.1, 0.2, 0.3])

if __name__ == '__main__':
    unittest.main()
