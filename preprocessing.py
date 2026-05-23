import cv2

# Load pre-trained Haar Cascade for eye detection
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def preprocess_frame(frame):
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect eyes
    eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(eyes) == 0:
        return None

    # Extract first detected eye
    x, y, w, h = eyes[0]
    eye_roi = gray[y:y + h, x:x + w]
    eye_roi = cv2.resize(eye_roi, (64, 64))  # Resize for model input
    return eye_roi
