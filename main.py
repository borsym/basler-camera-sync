from flask import Flask, render_template, Response, request
import cv2
import pypylon.pylon as py
import sys
import signal

app = Flask(__name__)

# Initialize the camera
icam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
icam.Open()


def signal_handler(sig, frame):
    global icam
    print("Ctrl+C pressed. Closing camera gracefully...")
    icam.Close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.route('/')
def index():
    camera_info = {
        'current_w': icam.Width.GetValue(),
        'current_h': icam.Height.GetValue(),
        'max_gain': icam.Gain.GetMax(),
        'min_gain': icam.Gain.GetMin(),
        "current_gain": icam.Gain.GetValue(),
        'current_exp': icam.ExposureTime.GetValue(),
        'max_exp': icam.ExposureTime.GetMax(),
        'min_exp': icam.ExposureTime.GetMin(),
        "pixel_format": icam.PixelFormat.GetValue()
    }
    return render_template('index.html', **camera_info)


def gen():
    while True:
        image = icam.GrabOne(4000)
        image = image.Array
        image = cv2.resize(image, (0, 0), fx=0.8366, fy=1, interpolation=cv2.INTER_LINEAR)
        ret, jpeg = cv2.imencode('.jpg', image)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type:image/jpeg\r\n'
               b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
               b'\r\n' + frame + b'\r\n')


@app.route('/video')
def video():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/width1', methods=['POST'])
def width():
    if request.method == 'POST':
        width = request.form.get('text_width')
        icam.StopGrabbing()
        icam.Width.SetValue(int(width))
    return index()
    # return render_template("index.html")


@app.route('/height1', methods=['POST'])
def height():
    if request.method == 'POST':
        height = request.form.get('text_height')
        icam.StopGrabbing()
        icam.Height.SetValue(int(height))
    return index()


@app.route('/reverseX', methods=['POST'])
def reverse_x():
    ss = icam.ReverseX.Value
    if request.method == 'POST':
        r = request.form.get('text_reverseX')
        icam.StopGrabbing()
        icam.ReverseX.SetValue(r == 'on')
        ss = icam.ReverseX.Value
    return index()


@app.route('/reverseY', methods=['POST'])
def reverse_y():
    ss = icam.ReverseY.Value
    if request.method == 'POST':
        r = request.form.get('text_reverseY')
        icam.StopGrabbing()
        icam.ReverseY.SetValue(r == 'on')
        ss = icam.ReverseY.Value
    return index()


@app.route('/exposure', methods=['POST'])
def exposure():
    ss = icam.ExposureTime.Value
    max_exposure = icam.ExposureTime.GetMax()
    if request.method == 'POST':
        r = int(request.form.get('text_exposure'))
        if r < max_exposure:
            icam.StopGrabbing()
            icam.ExposureTime.SetValue(r)
            ss = icam.ExposureTime.Value
    return index()


@app.route('/gain', methods=['POST'])
def gain():
    if request.method == 'POST':
        r = int(request.form.get('text_gain'))
        icam.Gain.SetValue(r)
    return index()


@app.route('/pixelFormat', methods=['POST'])
def pixel_format():
    ss = icam.PixelFormat.Value
    if request.method == 'POST':
        r = request.form.get('text_pixel_format')
        icam.StopGrabbing()
        icam.PixelFormat.SetValue(r)
        ss = icam.PixelFormat.Value
    return index()


if __name__ == "__main__":
    app.run(debug=True)
