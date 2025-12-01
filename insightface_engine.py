import numpy as np
import cv2
from insightface.app import FaceAnalysis
from typing import List, Dict

class InsightFaceEngine:
    def __init__(self, model_name='buffalo_l', providers=None, ctx_id=0):
        self.model_name = model_name
        self.providers = providers
        self.ctx_id = ctx_id
        self.app = None

    def prepare(self):
        if self.app is None:
            # FaceAnalysis will download models as needed. ctx_id=-1 uses CPU.
            self.app = FaceAnalysis(name=self.model_name, providers=self.providers)
            # ctx_id -1 for CPU; 0 for GPU (if available)
            try:
                self.app.prepare(ctx_id=self.ctx_id, det_size=(640, 640))
            except Exception as e:
                # fallback to CPU
                print(f"InsightFace prepare error: {e}, falling back to CPU")
                self.app.prepare(ctx_id=-1, det_size=(640, 640))

    def get_faces(self, bgr_image: np.ndarray) -> List[Dict]:
        """Detect faces and return list of dicts containing bbox and embedding"""
        self.prepare()
        faces = self.app.get(bgr_image)
        results = []
        for f in faces:
            results.append({
                'bbox': [int(x) for x in f.bbox.tolist()],
                'embedding': f.embedding.astype(float).tolist()
            })
        return results

    def read_image_bgr(self, path: str):
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Could not read image: {path}")
        return img
