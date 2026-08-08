import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import urllib.request
import ssl
import config

# Try importing face_recognition library (dlib-based, optional)
HAVE_FACE_RECOGNITION = False
try:
    import face_recognition
    HAVE_FACE_RECOGNITION = True
except ImportError:
    HAVE_FACE_RECOGNITION = False

# ──────────────────────────────────────────────────────────────────────────────
# Face Detector: OpenCV 5.0 uses FaceDetectorYN (YuNet DNN model)
# The CascadeClassifier was removed in OpenCV 5.0.
# We auto-download the lightweight YuNet ONNX model (~200KB) on first run.
# ──────────────────────────────────────────────────────────────────────────────

YUNET_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
YUNET_MODEL_PATH = os.path.join(config.BASE_DIR, "models", "face_detection_yunet_2023mar.onnx")

def _ensure_yunet_model():
    """Downloads the YuNet ONNX model if it is not already cached locally."""
    model_dir = os.path.dirname(YUNET_MODEL_PATH)
    os.makedirs(model_dir, exist_ok=True)
    if not os.path.exists(YUNET_MODEL_PATH):
        print(f"[face_utils] Downloading YuNet face detection model...")
    try:
        # Use unverified SSL context to avoid certificate issues
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(YUNET_MODEL_URL, context=context) as response, open(YUNET_MODEL_PATH, 'wb') as out_file:
            out_file.write(response.read())
        print(f"[face_utils] Model saved to: {YUNET_MODEL_PATH}")
    except Exception as e:
        print(f"[face_utils] WARNING: Could not download YuNet model: {e}")
        return False
    return os.path.exists(YUNET_MODEL_PATH)

# Global detector instance (lazy init, created once)
_face_detector = None

def _get_face_detector():
    """Returns (and lazily initializes) the YuNet FaceDetectorYN instance.
    Input size is set dynamically per-frame via setInputSize()."""
    global _face_detector
    if _face_detector is None:
        model_ok = _ensure_yunet_model()
        if model_ok:
            _face_detector = cv2.FaceDetectorYN_create(
                YUNET_MODEL_PATH,
                "",
                (320, 320),   # placeholder; overridden per-frame via setInputSize()
                score_threshold=0.6,
                nms_threshold=0.3,
                top_k=5000
            )
        else:
            _face_detector = None
    return _face_detector


def detect_faces(cv_frame):
    """
    Detects faces in an OpenCV BGR frame using YuNet (OpenCV 5.0+).
    Returns list of bounding boxes [(x, y, w, h), ...].
    Falls back to an empty list if the model is unavailable.
    """
    if cv_frame is None:
        return []

    h, w = cv_frame.shape[:2]
    detector = _get_face_detector()
    if detector is None:
        return []

    # Dynamically update input size for this frame resolution
    detector.setInputSize((w, h))

    _, faces = detector.detect(cv_frame)
    if faces is None:
        return []

    result = []
    for face in faces:
        # YuNet returns [x, y, w, h, ...landmarks..., score]
        x, y, fw, fh = int(face[0]), int(face[1]), int(face[2]), int(face[3])
        # Clamp to frame bounds
        x = max(0, x)
        y = max(0, y)
        fw = min(fw, w - x)
        fh = min(fh, h - y)
        if fw > 20 and fh > 20:
            result.append((x, y, fw, fh))

    return result

def get_face_encoding(cv_image, bbox=None):
    """
    Computes numerical face encoding vector for an image.
    Uses face_recognition library if available; otherwise falls back to OpenCV normalized histogram feature vector.
    """
    if cv_image is None:
        return None

    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

    if HAVE_FACE_RECOGNITION:
        try:
            if bbox is not None:
                x, y, w, h = bbox
                # face_recognition uses (top, right, bottom, left)
                face_location = [(y, x + w, y + h, x)]
                encodings = face_recognition.face_encodings(rgb_image, known_face_locations=face_location)
            else:
                encodings = face_recognition.face_encodings(rgb_image)

            if len(encodings) > 0:
                return ("dlib", encodings[0])
        except Exception as e:
            print(f"face_recognition encoding error: {e}")

    # Fallback OpenCV Feature Vector (Grayscale normalized 64x64 + Color Histogram)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    if bbox is not None:
        x, y, w, h = bbox
        face_roi = gray[y:y+h, x:x+w]
    else:
        faces = detect_faces(cv_image)
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
        else:
            face_roi = gray

    if face_roi.size == 0:
        return None

    resized = cv2.resize(face_roi, (64, 64))
    hist = cv2.calcHist([resized], [0], None, [256], [0, 256])
    cv2.normalize(hist, hist)

    # Flatten normalized 64x64 image + histogram
    norm_img = resized.astype(np.float32) / 255.0
    vec = np.hstack((norm_img.flatten(), hist.flatten()))
    return ("cv_fallback", vec)

def compare_encodings(enc1, enc2):
    """
    Compares two face encodings.
    Returns (distance, confidence_percentage).
    Lower distance = better match. Higher confidence % = better match.
    """
    if enc1 is None or enc2 is None:
        return 1.0, 0.0

    type1, vec1 = enc1
    type2, vec2 = enc2

    if type1 == "dlib" and type2 == "dlib" and HAVE_FACE_RECOGNITION:
        # Distance range roughly 0.0 to 1.0 (threshold ~ 0.6)
        dist = float(face_recognition.face_distance([vec1], vec2)[0])
        # Confidence formula: dist <= 0.6 maps to 60%-100%
        if dist > 0.6:
            conf = max(0.0, (1.0 - dist) * 100)
        else:
            conf = min(100.0, (1.0 - (dist / 1.2)) * 100)
        return dist, conf

    # Fallback vector cosine distance
    v1 = vec1.flatten()
    v2 = vec2.flatten()
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 1.0, 0.0

    cosine_sim = np.dot(v1, v2) / (norm1 * norm2)
    # Cosine sim is -1 to 1. For similar faces, sim ~ 0.7 - 1.0
    dist = max(0.0, 1.0 - cosine_sim)
    conf = max(0.0, min(100.0, cosine_sim * 100))
    return dist, conf

def cv2_to_photoimage(cv_frame, target_width=None, target_height=None):
    """Converts OpenCV BGR image frame to PIL ImageTk PhotoImage for Tkinter display."""
    rgb_frame = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)

    if target_width and target_height:
        pil_img = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    return ImageTk.PhotoImage(image=pil_img)

def load_and_resize_image(image_path, target_width, target_height):
    """Loads an image from disk and resizes it for Tkinter display."""
    if not os.path.exists(image_path):
        return None
    try:
        pil_img = Image.open(image_path)
        pil_img = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(pil_img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None
