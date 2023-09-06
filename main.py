from flask import Flask, render_template, Response, request
import cv2
from multi_normal  import CameraManager # Import your CameraManager class
import pypylon.pylon as py
import sys
import signal
app = Flask(__name__)

# Initialize the camera manager
# max_number_cameras = 3
# camera_manager = CameraManager(max_number_cameras)
# camera_manager.initialize_cameras()

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
    current_w = icam.Width.GetValue()
    current_h = icam.Height.GetValue()


    current_exposure  = icam.ExposureTime.GetValue()
    max_exposure = icam.ExposureTime.GetMax()
    min_exposure = icam.ExposureTime.GetMin()

    return render_template('index.html', current_w=current_w, current_h=current_h, current_exp=current_exposure, max_exp=max_exposure, min_exp=min_exposure)  # Create an HTML template for displaying the video feed


def gen():
  while True:
        image = icam.GrabOne(4000) ### 4ms time for grabbing image 
        image = image.Array
        image = cv2.resize(image, (0,0), fx=0.8366, fy=1, interpolation=cv2.INTER_LINEAR)### 2048x2048 resolution or INTER_AREA  inter_linear is fastest for and good for downsizing 
        ret, jpeg = cv2.imencode('.jpg', image)    
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type:image/jpeg\r\n'
               b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
               b'\r\n' + frame + b'\r\n')



@app.route('/video')
def video():
    """Video streaming route. Put this in the src attribute of an img tag."""

    return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/width1', methods=['POST', "GET"])
def width():
    if request.method == 'POST':
        # Access the form data using request.form
        width = request.form.get('text_width')
        print(type(width))
        # Process the form data as needed
        # ...
        icam.StopGrabbing()
        icam.Width.SetValue(int(width))

        # Redirect or render a response
    return render_template("index.html")

@app.route('/height1', methods=['POST', "GET"])
def height():
    if request.method == 'POST':
        # Access the form data using request.form
        height = request.form.get('text_height')
        print(type(height))
        # Process the form data as needed
        # ...
        icam.StopGrabbing()
        icam.Height.SetValue(int(height))

        # Redirect or render a response
    return render_template("index.html")


# create a reverseX endpoint
@app.route('/reverseX', methods=['GET', 'POST'])
def reverseX():
    ss = icam.ReverseX.Value
    if request.method == 'POST':
        r = request.form.get('text_reverseX')
        icam.StopGrabbing()
        icam.ReverseX.SetValue(r == 'True')
        ss = icam.ReverseX.Value
    return render_template('index.html',result = ss)


# create a reverseY endpoint
@app.route('/reverseY', methods=['GET', 'POST'])
def reverseY():
    ss = icam.ReverseY.Value
    if request.method == 'POST':
        r = request.form.get('text_reverseY')
        icam.StopGrabbing()
        icam.ReverseY.SetValue(r == 'True')
        ss = icam.ReverseY.Value
    return render_template('index.html',result = ss)


@app.route('/exposure', methods=['GET', 'POST'])
def exposure():
    ss = icam.ExposureTime.Value
    max = icam.ExposureTime.GetMax()
    if request.method == 'POST':
       # print(request.form.get('text_exposure'))
        r = int(request.form.get('text_exposure'))
        if r < max:
            icam.StopGrabbing()
            icam.ExposureTime.SetValue(r)
            ss = icam.ExposureTime.Value
    return render_template('index.html',result = ss, max = max)

# create a pixel format
@app.route('/pixelFormat', methods=['GET', 'POST'])
def pixel_format():
    ss = icam.PixelFormat.Value
    if request.method == 'POST':
        r = request.form.get('text_pixel_format')
        icam.StopGrabbing()
        icam.PixelFormat.SetValue(r)
        ss = icam.PixelFormat.Value
    return render_template('index.html',result = ss)
if __name__ == "__main__":
    app.run(debug=True)

