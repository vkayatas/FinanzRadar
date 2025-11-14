import cv2
import numpy as np
from ultralytics import YOLO

# ---- CONFIG ----
ROOT_DIR = "/home/vkayata/dev/app_prototyping/utility_functions/shot_tracer/"
FILE_NAME = "shot1_cut"
VIDEO_PATH = ROOT_DIR + f"input/{FILE_NAME}.mp4"
OUTPUT_PATH = ROOT_DIR + f"output/{FILE_NAME}_input.mp4"
USE_PARABOLA_FIT = True
USE_HSV_FALLBACK = True

# ---- YOLO Setup ----
model = YOLO("yolov8s.pt")

# ---- HSV fallback config ----
LOWER_COLOR = np.array([20, 100, 100])
UPPER_COLOR = np.array([40, 255, 255])
kernel = np.ones((3,3), np.uint8)

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

# ---- Kalman Filter Setup ----
kalman = cv2.KalmanFilter(4,2)
kalman.transitionMatrix = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]], np.float32)
kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32)*0.03
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32)*0.5

# ---- User Feedback: Select initial ball ----
ret, first_frame = cap.read()
if not ret:
    raise IOError("Cannot read first frame for user selection")

init_point = []
def select_ball(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        init_point.append((x, y))

cv2.imshow("Select Ball", first_frame)
cv2.setMouseCallback("Select Ball", select_ball)
print("Click on the ball in the first frame and press any key...")
cv2.waitKey(0)
cv2.destroyWindow("Select Ball")

if init_point:
    x0, y0 = init_point[0]
    kalman.statePre = np.array([[x0],[y0],[0],[0]], np.float32)

# Reset capture to first frame
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    pred = kalman.predict()
    px, py = int(pred[0]), int(pred[1])
    cx, cy = px, py

    # ---- YOLO Detection ----
    results = model(frame, verbose=False)[0]
    detected = False
    conf_weight = 1.0

    for box in results.boxes:
        cls = int(box.cls[0])
        score = float(box.conf[0])
        if cls == 32:
            x1,y1,x2,y2 = box.xyxy[0].cpu().numpy().astype(int)
            x, y = (x1+x2)//2, (y1+y2)//2
            meas = np.array([[np.float32(x)], [np.float32(y)]])
            # Weight Kalman correction by confidence
            est = kalman.correct(meas * score)
            cx, cy = int(est[0]), int(est[1])
            detected = True
            conf_weight = score
            break

    # ---- Optional HSV fallback ----
    if USE_HSV_FALLBACK and not detected:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            (x,y), radius = cv2.minEnclosingCircle(c)
            if radius > 2:
                meas = np.array([[np.float32(x)], [np.float32(y)]])
                est = kalman.correct(meas * 0.5)
                cx, cy = int(est[0]), int(est[1])

    trajectory.append((cx, cy))

    # ---- Draw trajectory with color-coded points ----
    color = (0,255,0) if detected else (0,255,255)  # green = YOLO, yellow = fallback
    cv2.circle(frame, (cx, cy), 4, color, -1)
    if len(trajectory) > 1:
        cv2.polylines(frame, [np.array(trajectory,np.int32)], False, (0,0,255), 2)

    out.write(frame)
    cv2.imshow("Golf Shot Tracer", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('m'):
        # Manual correction: user clicks the ball
        point = []
        cv2.imshow("Manual Correct", frame)
        cv2.setMouseCallback("Manual Correct", lambda e,x,y,f,p: point.append((x,y)) if e==cv2.EVENT_LBUTTONDOWN else None)
        cv2.waitKey(0)
        cv2.destroyWindow("Manual Correct")
        if point:
            meas = np.array([[np.float32(point[0][0])], [np.float32(point[0][1])]])
            est = kalman.correct(meas)
            cx, cy = int(est[0]), int(est[1])
            trajectory[-1] = (cx, cy)

cap.release()
out.release()
cv2.destroyAllWindows()

# ---- Optional Parabola Fit ----
if USE_PARABOLA_FIT and len(trajectory) > 5:
    pts = np.array(trajectory)
    x, y = pts[:,0], pts[:,1]
    coeffs = np.polyfit(x, y, 2)
    poly = np.poly1d(coeffs)

    parabola_img = np.zeros((height,width,3), dtype=np.uint8)
    x_new = np.linspace(x.min(), x.max(), num=200)
    y_new = poly(x_new)

    for i in range(len(x_new)-1):
        pt1 = (int(x_new[i]), int(y_new[i]))
        pt2 = (int(x_new[i+1]), int(y_new[i+1]))
        cv2.line(parabola_img, pt1, pt2, (255,0,0),2)

    overlay_path = OUTPUT_PATH.replace(".mp4","_parabola.png")
    cv2.imwrite(overlay_path, parabola_img)
    print(f"📈 Parabola overlay saved to: {overlay_path}")

print(f"✅ Interactive golf shot tracer complete! Video saved to: {OUTPUT_PATH}")
