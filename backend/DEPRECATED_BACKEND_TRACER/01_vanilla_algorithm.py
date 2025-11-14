import cv2
import numpy as np

## https://www.thecodingcouple.com/using-wsl-on-corporate-vpn/

# ---- CONFIG ----
ROOT_DIR = "/home/vkayata/dev/app_prototyping/utility_functions/shot_tracer/"
FILE_NAME = "shot1_cut"
VIDEO_PATH = ROOT_DIR + f"input/{FILE_NAME}.mp4"
OUTPUT_PATH = ROOT_DIR + f"output/{FILE_NAME}_vanilla.mp4"

# Ball detection HSV color range (tweak as needed)
LOWER_COLOR = np.array([20, 100, 100])   # Lower HSV bound (yellowish ball)
UPPER_COLOR = np.array([40, 255, 255])   # Upper HSV bound

# Enable/disable parabola fitting for trajectory smoothing
USE_PARABOLA_FIT = True

# ---- LOAD VIDEO ----
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError(f"Error: Cannot open video file: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

# Store trajectory points
trajectory = []

# Pre-allocate kernel for morphological operations
kernel = np.ones((3, 3), np.uint8)

# ---- Kalman Filter Setup ----
kalman = cv2.KalmanFilter(4, 2)  # 4 states, 2 measurements

# State: [x, y, vx, vy]
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

    # Convert to HSV and create mask
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)

    # Clean mask (remove noise)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    # Find contours (ball candidates)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Predict next state
    pred = kalman.predict()
    px, py = int(pred[0]), int(pred[1])

    if contours:
        # Select largest contour (likely ball)
        c = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(c)

        if radius > 2:  # Filter small noise
            meas = np.array([[np.float32(x)], [np.float32(y)]])
            est = kalman.correct(meas)
            cx, cy = int(est[0]), int(est[1])
        else:
            cx, cy = px, py
    else:
        # No detection → trust prediction
        cx, cy = px, py

    # Save trajectory
    trajectory.append((cx, cy))

    # Draw ball position
    cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)

    # Draw trajectory line
    if len(trajectory) > 1:
        cv2.polylines(frame, [np.array(trajectory, np.int32)], False, (0, 0, 255), 2)

    # Write processed frame
    out.write(frame)

    # Display frame (press 'q' to quit)
    cv2.imshow("Golf Shot Tracer", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

# ---- Optional: Parabola Fit ----
if USE_PARABOLA_FIT and len(trajectory) > 5:
    pts = np.array(trajectory)
    x = pts[:, 0]
    y = pts[:, 1]

    # Fit quadratic curve: y = ax^2 + bx + c
    coeffs = np.polyfit(x, y, 2)
    poly = np.poly1d(coeffs)

    # Generate smooth curve
    x_new = np.linspace(x.min(), x.max(), num=200)
    y_new = poly(x_new)

    # Create overlay with fitted parabola
    parabola_img = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(len(x_new) - 1):
        pt1 = (int(x_new[i]), int(y_new[i]))
        pt2 = (int(x_new[i+1]), int(y_new[i+1]))
        cv2.line(parabola_img, pt1, pt2, (255, 0, 0), 2)

    # Save parabola overlay as separate file
    overlay_path = OUTPUT_PATH.replace(".mp4", "_parabola.png")
    cv2.imwrite(overlay_path, parabola_img)
    print(f"📈 Parabola overlay saved to: {overlay_path}")

print(f"✅ Processing complete! Video saved to: {OUTPUT_PATH}")