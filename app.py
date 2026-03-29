from flask import Flask, Response, jsonify, render_template
import cv2
from ultralytics import YOLO

# ================= CONFIG =================
MODEL_PATH = "best.pt"
VIDEO_PATH = "Video Project 2.mp4"   # or 0 for webcam

# ================= INIT ================= 
app = Flask(__name__)

model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(VIDEO_PATH)

latest_label = ""

# ================= VIDEO =================
def generate_frames():
    global latest_label

    while True:
        success, frame = cap.read()

        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 480))

        # FAST YOLO
        results = model(frame, imgsz=480, conf=0.4)

        if len(results[0].boxes) > 0:
            cls_id = int(results[0].boxes.cls[0])
            latest_label = model.names[cls_id]
        else:
            latest_label = ""

        annotated = results[0].plot()

        ret, buffer = cv2.imencode('.jpg', annotated)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ================= ROUTES =================
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/wastage_data')
def wastage_data():
    return jsonify({"label": latest_label})

# ================= MAIN =================
if __name__ == "__main__":
    app.run(debug=True)