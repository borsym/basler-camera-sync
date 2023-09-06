from flask import Flask, render_template, Response, request
import cv2
import pypylon.pylon as py
import sys
import signal

app = Flask(__name__)

# Initialize the camera
# icam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
# icam.Open()

tlFactory = py.TlFactory.GetInstance()
devices = tlFactory.EnumerateDevices()
cameras = py.InstantCameraArray(len(devices))

for i, camera in enumerate(cameras):
    camera.Attach(tlFactory.CreateDevice(devices[i]))

cameras.Open()
print("open")

def signal_handler(sig, frame):
    global cameras
    print("Ctrl+C pressed. Closing camera gracefully...")
    cameras.Close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.route('/')
def index():
    # icam = cameras[0]
    # camera_info = {
    #     'current_w': icam.Width.GetValue(),
    #     'current_h': icam.Height.GetValue(),
    #     'max_gain': icam.Gain.GetMax(),
    #     'min_gain': icam.Gain.GetMin(),
    #     "current_gain": icam.Gain.GetValue(),
    #     'current_exp': icam.ExposureTime.GetValue(),
    #     'max_exp': icam.ExposureTime.GetMax(),
    #     'min_exp': icam.ExposureTime.GetMin(),
    #     "pixel_format": icam.PixelFormat.GetValue()
    # }
    # return render_template('index.html', **camera_info)
    camera_info = []
    for i, icam in enumerate(cameras):
        info = {
            'camera_index': i,
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
        camera_info.append(info)
    return render_template('index.html', cameras=camera_info)


def gen(camera_index):
    icam = cameras[camera_index]
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


@app.route('/video/<int:camera_index>', methods=['GET', 'POST'])
def video(camera_index):
    return Response(gen(camera_index), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/width1', methods=['POST'])
def width():
    if request.method == 'POST':
        camera_index = int(request.form.get('camera_index'))
        width = request.form.get('text_width')
        icam = cameras[camera_index]
        icam.StopGrabbing()
        icam.Width.SetValue(int(width))
    return index()
    # return render_template("index.html")


@app.route('/height1', methods=['POST'])
def height():
    if request.method == 'POST':
        camera_index = int(request.form.get('camera_index'))
        height = request.form.get('text_height')
        icam = cameras[camera_index]
        icam.StopGrabbing()
        icam.Height.SetValue(int(height))
    return index()


@app.route('/reverseX', methods=['POST'])
def reverse_x():
    icam = cameras[0]
    ss = icam.ReverseX.Value
    if request.method == 'POST':
        r = request.form.get('text_reverseX')
        icam.StopGrabbing()
        icam.ReverseX.SetValue(r == 'on')
        ss = icam.ReverseX.Value
    return index()


@app.route('/reverseY', methods=['POST'])
def reverse_y():
    icam = cameras[0]
    ss = icam.ReverseY.Value
    if request.method == 'POST':
        r = request.form.get('text_reverseY')
        icam.StopGrabbing()
        icam.ReverseY.SetValue(r == 'on')
        ss = icam.ReverseY.Value
    return index()


@app.route('/exposure', methods=['POST'])
def exposure():
    icam = cameras[0]
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
    icam = cameras[0]
    if request.method == 'POST':
        r = int(request.form.get('text_gain'))
        icam.Gain.SetValue(r)
    return index()


@app.route('/pixelFormat', methods=['POST'])
def pixel_format():
    icam = cameras[0]
    ss = icam.PixelFormat.Value
    if request.method == 'POST':
        r = request.form.get('text_pixel_format')
        icam.StopGrabbing()
        icam.PixelFormat.SetValue(r)
        ss = icam.PixelFormat.Value
    return index()


if __name__ == "__main__":
    app.run(debug=True)
