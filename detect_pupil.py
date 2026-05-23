import cv2
import torch
import torch.nn as nn
import numpy as np
import time
import csv
import os
from datetime import datetime

# -------------------------------
# Model Definition (Fully Conv)
# -------------------------------
class PupilDetectionModel(nn.Module):
    def __init__(self):
        super(PupilDetectionModel, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16, 3, 1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, 1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 1, 2, stride=2),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

# -------------------------------
# Load Model
# -------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = PupilDetectionModel().to(device)

# load model weights (ensure the file exists in same folder)
try:
    _model.load_state_dict(torch.load("pupil_detection_model.pth", map_location=device))
    _model.eval()
except Exception as e:
    # If model not found or load fails, raise so caller can handle
    raise RuntimeError(f"Failed to load model: {e}")

# -------------------------------
# Eye Detection (Haar Cascade)
# -------------------------------
_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# -------------------------------
# Helpers
# -------------------------------
def preprocess_eye(eye_img):
    gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (64, 64))
    gray = gray / 255.0
    tensor = torch.tensor(gray, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    return tensor.to(device)

def get_pupil(mask, scale_factor=1.0):
    mask = mask.squeeze().detach().cpu().numpy()
    mask = (mask > 0.5).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return None, None
    largest = max(contours, key=cv2.contourArea)
    (x, y), radius = cv2.minEnclosingCircle(largest)
    return (int(x * scale_factor), int(y * scale_factor)), int(radius * scale_factor)

# Exponential smoothing helper
def smooth_signal(values, alpha=0.25):
    if len(values) < 2:
        return values[:]
    smoothed = [values[0]]
    for v in values[1:]:
        smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])
    return smoothed

# -------------------------------
# PLR / Concussion Analysis
# -------------------------------
# -------------------------------
# Robust PLR / Concussion Analysis
# -------------------------------
def filter_outliers(diams):
    """Remove extreme outliers beyond 2 standard deviations."""
    if not diams:
        return diams
    arr = np.array(diams)
    median = np.median(arr)
    std = np.std(arr)
    filtered = arr[(arr > median - 2*std) & (arr < median + 2*std)]
    return filtered.tolist() if len(filtered) > 0 else arr.tolist()

def compute_plr_metrics_filtered(diams, times):
    """Smooth and filter diameters before computing PLR metrics."""
    diams_filtered = filter_outliers(diams)
    diams_smoothed = smooth_signal(diams_filtered)
    return compute_plr_metrics(diams_smoothed, times)

def analyze_concussion_bilateral_robust(metrics_left, metrics_right):
    """Return verdict with robustness against AI errors."""
    verdict = "No Concussion Detected"
    reason = "Pupils reacted symmetrically and within expected speed/strength."
    details = {}

    # If no reliable data
    if (metrics_left is None or metrics_left["n_samples"] < 20) and \
       (metrics_right is None or metrics_right["n_samples"] < 20):
        return "Inconclusive", "Not enough reliable pupil data.", {}

    # Thresholds
    CONSTRICTION_LOW_THRESH = 12.0   # percent
    ASYMMETRY_PERCENT_THRESH = 25.0  # percent
    T75_SLOW_THRESH = 6.0            # seconds
    T75_DIFF_THRESH = 1.0            # seconds
    CONSECUTIVE_VIOLATION_FRAMES = 5 # must persist

    flags = []

    # --- Check per-eye ---
    for side, m in (("left", metrics_left), ("right", metrics_right)):
        if m is None:
            flags.append(f"{side} eye: insufficient data")
            continue

        # Weak constriction
        if m["constriction_percent"] < CONSTRICTION_LOW_THRESH:
            flags.append(f"{side} eye weak constriction ({m['constriction_percent']:.1f}%)")
        # Slow response
        if m["t75"] is not None and m["t75"] > T75_SLOW_THRESH:
            flags.append(f"{side} eye slow response (T75 {m['t75']:.2f}s)")

    # --- Bilateral metrics ---
    if metrics_left and metrics_right:
        left_c = metrics_left["constriction_percent"]
        right_c = metrics_right["constriction_percent"]
        asym = abs(left_c - right_c)
        details["asymmetry_constriction_percent"] = asym

        left_t75 = metrics_left["t75"] if metrics_left["t75"] is not None else float('inf')
        right_t75 = metrics_right["t75"] if metrics_right["t75"] is not None else float('inf')
        t75_diff = abs(left_t75 - right_t75)
        details["t75_diff_seconds"] = t75_diff

        if asym > ASYMMETRY_PERCENT_THRESH:
            flags.append(f"Asymmetric constriction ({asym:.1f}%)")
        if t75_diff > T75_DIFF_THRESH:
            flags.append(f"T75 difference between eyes ({t75_diff:.2f}s)")

        # Average constriction check
        avg_constriction = (left_c + right_c) / 2
        if avg_constriction < CONSTRICTION_LOW_THRESH:
            flags.append(f"Bilateral weak constriction ({avg_constriction:.1f}%)")

    # --- Confidence score check ---
    confidence = 0.0
    max_score = 2.0
    if metrics_left:
        confidence += min(1.0, metrics_left["n_samples"] / 60.0)
    if metrics_right:
        confidence += min(1.0, metrics_right["n_samples"] / 60.0)
    confidence_score = confidence / max_score
    details["confidence_score"] = confidence_score

    if confidence_score < 0.6:
        verdict = "Inconclusive"
        reason = "Not enough reliable pupil data."
    elif len(flags) == 0:
        verdict = "No Concussion Detected"
        reason = "Pupils reacted normally."
    else:
        verdict = "Possible Concussion"
        reason = "; ".join(flags)

    details["flags"] = flags
    details["left"] = metrics_left
    details["right"] = metrics_right

    return verdict, reason, details

def compute_plr_metrics(diams, times):
    """Compute basic PLR metrics for a single eye.
    diams: list of diameters (pixels)
    times: list of timestamps (seconds)
    Returns: dict with max, min, constriction%, t75 (sec or None).
    """
    arr = np.array(diams)
    t = np.array(times)
    if len(arr) == 0:
        return None
    max_d = float(np.max(arr))
    min_d = float(np.min(arr))
    constriction = ((max_d - min_d) / max_d) * 100 if max_d > 0 else 0.0
    baseline = arr[0] if len(arr) > 0 else max_d
    target = baseline * 0.75
    t75 = None
    for tt, d in zip(t, arr):
        if d <= target:
            t75 = float(tt - t[0])  # seconds from start
            break
    time_to_min = float(t[np.argmin(arr)] - t[0]) if len(arr) > 0 else None
    return {
        "max_diameter": max_d,
        "min_diameter": min_d,
        "constriction_percent": constriction,
        "t75": t75,
        "time_to_min": time_to_min,
        "n_samples": len(arr)
    }

def analyze_concussion_bilateral(metrics_left, metrics_right):
    """Return (verdict, one_sentence_reason, details_dict)."""
    reason = "No Concussion Detected"
    verdict = "No Concussion Detected"
    if metrics_left is None and metrics_right is None:
        return "Insufficient Data", "Could not detect pupils reliably for either eye.", {}

    # key thresholds (tunable)
    CONSTRICTION_LOW_THRESH = 12.0  # percent
    ASYMMETRY_PERCENT_THRESH = 25.0  # percent difference
    T75_SLOW_THRESH = 6.0  # seconds
    T75_DIFF_THRESH = 1.0  # seconds difference between eyes

    flags = []

    # check per-eye poor constriction
    for side, m in (("left", metrics_left), ("right", metrics_right)):
        if m is None:
            flags.append(f"{side} eye: no data")
            continue
        if m["constriction_percent"] < CONSTRICTION_LOW_THRESH:
            flags.append(f"{side} eye weak constriction ({m['constriction_percent']:.1f}%)")
        if m["t75"] is not None and m["t75"] > T75_SLOW_THRESH:
            flags.append(f"{side} eye slow (T75 {m['t75']:.2f}s)")

    details = {}
    if metrics_left is not None and metrics_right is not None:
        left_c = metrics_left["constriction_percent"]
        right_c = metrics_right["constriction_percent"]
        asym_percent = abs(left_c - right_c)
        details["asymmetry_constriction_percent"] = asym_percent
        left_t75 = metrics_left["t75"] if metrics_left["t75"] is not None else float('inf')
        right_t75 = metrics_right["t75"] if metrics_right["t75"] is not None else float('inf')
        t75_diff = abs(left_t75 - right_t75)
        details["t75_diff_seconds"] = t75_diff
        if asym_percent > ASYMMETRY_PERCENT_THRESH:
            flags.append(f"Asymmetric constriction ({asym_percent:.1f}% difference)")
        if t75_diff > T75_DIFF_THRESH:
            flags.append(f"T75 delay difference between eyes ({t75_diff:.2f}s)")

    if len(flags) == 0:
        verdict = "No Concussion Detected"
        reason = "Pupils reacted symmetrically and within expected speed/strength."
    else:
        verdict = "Possible Concussion"
        reason = flags[0] + "."

    details["left"] = metrics_left
    details["right"] = metrics_right
    details["flags"] = flags
    return verdict, reason, details

# -------------------------------
# Flash Detection Helper
# -------------------------------
class FlashDetector:
    def __init__(self, baseline_window=20, relative_thresh=0.18, absolute_thresh=20, sustain_frames=3):
        self.baseline_window = baseline_window
        self.relative_thresh = relative_thresh
        self.absolute_thresh = absolute_thresh
        self.sustain_frames = sustain_frames
        self.recent = []
        self.sustain_count = 0
        self.flash_time = None

    def update(self, frame_gray_mean, now):
        self.recent.append(frame_gray_mean)
        if len(self.recent) > self.baseline_window:
            self.recent.pop(0)
        baseline = np.mean(self.recent) if len(self.recent) > 0 else frame_gray_mean
        cond_rel = (frame_gray_mean - baseline) / (baseline + 1e-6) > self.relative_thresh
        cond_abs = (frame_gray_mean - baseline) > self.absolute_thresh
        if cond_rel or cond_abs:
            self.sustain_count += 1
        else:
            self.sustain_count = 0
        if self.sustain_count >= self.sustain_frames and self.flash_time is None:
            self.flash_time = now
            return True, baseline
        return False, baseline

# -------------------------------
# Main Dual-Eye Pupil Detection
# -------------------------------
def run_pupil_detection_dual(
    MIN_READINGS=100,         # now at least 100 samples per eye
    MAX_READINGS=300,
    STABILITY_WINDOW=15,
    STABILITY_THRESHOLD=0.02,
    camera_index=0,
    show_window=False,
    flash_detection=True,
    event_capture_seconds=5.0,
    save_csv=True,
    mask_debug=False
):
    """Dual-eye pupil detection with correct scaling, confidence, overlay, and auto-stop."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    left_diams, left_times, right_diams, right_times = [], [], [], []
    start_time = time.time()
    flash_detector = FlashDetector()
    flash_detected = False
    flash_timestamp = None
    post_flash_end = None
    MIN_RADIUS_PX = 3

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame, ending capture.")
            break

        now = time.time()
        rel_t = now - start_time
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_mean = float(np.mean(gray))

        # --- Flash detection ---
        if flash_detection and not flash_detected:
            triggered, _ = flash_detector.update(frame_mean, now)
            if triggered:
                flash_detected = True
                flash_timestamp = flash_detector.flash_time
                post_flash_end = flash_timestamp + event_capture_seconds
        elif flash_detection and flash_detected and now >= post_flash_end:
            # allow post-flash capture
            if max(len(left_diams), len(right_diams)) >= MIN_READINGS:
                break

        # --- Eye detection ---
        # --- Face detection to restrict eye region ---
        _face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = _face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        eyes_sorted = []
        for (fx, fy, fw, fh) in faces:
            # Define the region for eyes: upper half of the face
            eye_region_y = fy
            eye_region_h = int(fh * 0.5)  # top 50% of face
            eye_region_x = fx
            eye_region_w = fw

            roi_gray = gray[eye_region_y:eye_region_y + eye_region_h,
                            eye_region_x:eye_region_x + eye_region_w]

            detected_eyes = _eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.05, minNeighbors=3)
            # Adjust coordinates to original frame
            for (ex, ey, ew, eh) in detected_eyes:
                global_ex = ex + eye_region_x
                global_ey = ey + eye_region_y
                # Filter out detections that are too low (below nose)
                if global_ey > fy + int(fh * 0.55):
                    continue
                eyes_sorted.append((global_ex, global_ey, ew, eh))

        # Keep only 2 eyes (left, right)
        eyes_sorted = sorted(eyes_sorted, key=lambda r: r[0])[:2]

        for i, (ex, ey, ew, eh) in enumerate(eyes_sorted):
            if ew < 10 or eh < 10:
                continue
            eye_roi = frame[ey:ey+eh, ex:ex+ew]

            try:
                inp = preprocess_eye(eye_roi)
                with torch.no_grad():
                    mask = _model(inp)

                mask_np = mask.squeeze().cpu().numpy()
                mask_bin = (mask_np > 0.3).astype(np.uint8) * 255
                contours, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    largest = max(contours, key=cv2.contourArea)
                    (mx, my), radius = cv2.minEnclosingCircle(largest)

                    # --- Correct scaling ---
                    cx = int(ex + mx * (ew / 64))
                    cy = int(ey + my * (eh / 64))
                    radius_scaled = int(radius * (ew / 64) * 0.45)
                    center = (cx, cy)
                    radius = radius_scaled
                else:
                    center, radius = None, None

            except Exception as e:
                print(f"Eye processing error: {e}")
                center, radius = None, None

            # --- Only process if detection valid ---
            if center is not None and radius is not None and radius > MIN_RADIUS_PX:
                side = "left" if i == 0 else "right"
                diam = radius * 2

                if side == "left":
                    left_diams.append(diam)
                    left_times.append(rel_t)
                else:
                    right_diams.append(diam)
                    right_times.append(rel_t)

                if show_window:
                    cv2.circle(frame, center, radius, (0, 255, 0), 2)
                    cv2.circle(frame, center, 1, (0, 0, 255), 3)

                    if mask_debug:
                        mask_vis = cv2.resize(mask_bin, (ew, eh))
                        mask_vis = cv2.cvtColor(mask_vis, cv2.COLOR_GRAY2BGR)
                        frame[ey:ey+eh, ex:ex+ew] = cv2.addWeighted(frame[ey:ey+eh, ex:ex+ew], 0.7, mask_vis, 0.3, 0)

        # Draw rectangles around detected eyes
        if show_window:
            for ex, ey, ew, eh in eyes_sorted:
                cv2.rectangle(frame, (ex, ey), (ex+ew, ey+eh), (80, 80, 80), 1)

            # --- Overlay text ---
            status_lines = [
                f"L samples: {len(left_diams)} R samples: {len(right_diams)}",
                f"FPS est: {fps:.1f}"
            ]
            if flash_detection:
                if not flash_detected:
                    status_lines.append("Waiting for flash...")
                else:
                    status_lines.append(f"Flash detected at {flash_timestamp - start_time:.2f}s")

            for i, line in enumerate(status_lines):
                cv2.putText(frame, line, (10, 20 + i*20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)

            cv2.imshow("Pupil Detection Overlay", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # --- Stop conditions ---
        if len(left_diams) >= MIN_READINGS and len(right_diams) >= MIN_READINGS:
            break
        if max(len(left_diams), len(right_diams)) >= MAX_READINGS:
            break

    cap.release()
    if show_window:
        cv2.destroyAllWindows()

    # --- Smooth signals and compute metrics ---
    left_diams_sm = smooth_signal(left_diams)
    right_diams_sm = smooth_signal(right_diams)
    metrics_left = compute_plr_metrics_filtered(left_diams, left_times)
    metrics_right = compute_plr_metrics_filtered(right_diams, right_times)
    verdict, reason, details = analyze_concussion_bilateral_robust(metrics_left, metrics_right)

    details["raw"] = {
        "left": {"diams": left_diams_sm, "times": left_times},
        "right": {"diams": right_diams_sm, "times": right_times},
        "fps_estimated": fps
    }
    details["flash_detected"] = flash_detected
    details["flash_timestamp"] = (flash_timestamp - start_time) if flash_timestamp else None

    # --- Compute confidence score ---
    score = 0.0
    max_score = 2.0
    if metrics_left:
        score += min(1.0, metrics_left["n_samples"] / 60.0)
    if metrics_right:
        score += min(1.0, metrics_right["n_samples"] / 60.0)
    confidence_score = score / max_score
    details["confidence_score"] = confidence_score

    if save_csv:
        csv_path = save_raw_csv(details["raw"])
        details["saved_csv"] = csv_path

    return verdict, reason, details

# -------------------------------
# CSV Export
# -------------------------------
def save_raw_csv(raw, folder=".", prefix="plr_raw"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{prefix}_{timestamp}.csv"
    outpath = os.path.join(folder, fname)
    try:
        left = raw.get("left", {})
        right = raw.get("right", {})
        times = sorted(set(left.get("times", []) + right.get("times", [])))
        with open(outpath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["time_sec", "left_diameter_px", "right_diameter_px"])
            for t in times:
                ld = ""
                rd = ""
                if t in left.get("times", []):
                    idx = left["times"].index(t)
                    ld = f"{left['diams'][idx]:.6f}"
                if t in right.get("times", []):
                    idx = right["times"].index(t)
                    rd = f"{right['diams'][idx]:.6f}"
                writer.writerow([f"{t:.6f}", ld, rd])
        return outpath
    except Exception:
        return None

# -------------------------------
# Run standalone
# -------------------------------
if __name__ == "__main__":
    v, r, d = run_pupil_detection_dual(show_window=True, flash_detection=True)
    print("VERDICT:", v)
    print("REASON:", r)
    print("DETAILS:", d)
