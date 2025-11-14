import cv2
import numpy as np
from ultralytics import YOLO

# ---- CONFIG ----
ROOT_DIR = "/home/vkayata/dev/app_prototyping/utility_functions/shot_tracer/"
FILE_NAME = "shot1_cut"
VIDEO_PATH = ROOT_DIR + f"input/{FILE_NAME}.mp4"
OUTPUT_PATH = ROOT_DIR + f"output/{FILE_NAME}_final_yolo_input.mp4"
USE_PARABOLA_FIT = True

# ---- YOLO Setup ----
# Use pretrained YOLOv8 small model (can later replace with fine-tuned model)
model = YOLO("yolov8s.pt")

# ---- Video Setup ----
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError(f"Error: Cannot open video file: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

trajectory = []

# ---- Kalman Filter ----
kalman = cv2.KalmanFilter(4, 2)
kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32)
kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.5

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame, verbose=False)[0]

    # Predict next state
    pred = kalman.predict()
    px, py = int(pred[0]), int(pred[1])
    cx, cy = px, py  # fallback

    # Find sports ball (COCO class 32)
    for box in results.boxes:
        cls = int(box.cls[0])
        if cls == 32:  # sports ball
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            x, y = (x1 + x2) // 2, (y1 + y2) // 2
            meas = np.array([[np.float32(x)], [np.float32(y)]])
            est = kalman.correct(meas)
            cx, cy = int(est[0]), int(est[1])
            break

    # Save trajectory
    trajectory.append((cx, cy))

    # Draw ball and trajectory
    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
    if len(trajectory) > 1:
        cv2.polylines(frame, [np.array(trajectory, np.int32)], False, (0, 0, 255), 2)

    out.write(frame)
    cv2.imshow("Golf Shot Tracer", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

# ---- Optional: Parabola Fit ----
if USE_PARABOLA_FIT and len(trajectory) > 5:
    pts = np.array(trajectory)
    x, y = pts[:, 0], pts[:, 1]
    coeffs = np.polyfit(x, y, 2)
    poly = np.poly1d(coeffs)

    parabola_img = np.zeros((height, width, 3), dtype=np.uint8)
    x_new = np.linspace(x.min(), x.max(), num=200)
    y_new = poly(x_new)

    for i in range(len(x_new) - 1):
        pt1 = (int(x_new[i]), int(y_new[i]))
        pt2 = (int(x_new[i + 1]), int(y_new[i + 1]))
        cv2.line(parabola_img, pt1, pt2, (255, 0, 0), 2)

    overlay_path = OUTPUT_PATH.replace(".mp4", "_parabola.png")
    cv2.imwrite(overlay_path, parabola_img)
    print(f"📈 Parabola overlay saved to: {overlay_path}")

print(f"✅ Processing complete! Video saved to: {OUTPUT_PATH}")
