from pypylon import pylon
import numpy as np
import cv2
from imageio import get_writer
from threading import Thread
import queue
import pathlib

#todo create the folder if not exists
# flask app
# in the flask app person can change the expo, image quality, etc


class CameraManager:
    def __init__(self, max_cameras=2):
        self.max_cameras = max_cameras
        self.cameras = []
        self.image_queues = []
        self.saver_threads = []
        self.number_of_cameras = None

    def initialize_cameras(self):
        tlFactory = pylon.TlFactory.GetInstance()
        devices = tlFactory.EnumerateDevices()

        if len(devices) == 0:
            raise pylon.RUNTIME_EXCEPTION("No camera present.")

        num_cameras = min(len(devices), self.max_cameras)
        self.number_of_cameras = num_cameras
        self.cameras = pylon.InstantCameraArray(num_cameras)

        for i, camera in enumerate(self.cameras):
            camera.Attach(tlFactory.CreateDevice(devices[i]))

        self.cameras.Open()
        self.image_queues = [queue.Queue() for _ in range(num_cameras)]

        for i in range(num_cameras):
            camera = self.cameras[i]
            camera.TriggerSelector.SetValue("FrameStart")
            camera.TriggerMode.SetValue("On")
            camera.TriggerSource.SetValue("Line1") 
            camera.PixelFormat.SetValue("RGB8")
            camera.StreamGrabber.MaxTransferSize = 4194304
    
    def get_frame(self, camera_index):
        if camera_index < 0 or camera_index >= self.number_of_cameras:
            raise ValueError("Invalid camera index")

        try:
            image, _ = self.image_queues[camera_index].get(timeout=1)
            return image
        except queue.Empty:
            return None
        
    def start_grabbing(self):
        if not self.cameras:
            raise RuntimeError("Cameras not initialized.")

        self.cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, 
                      pylon.GrabLoop_ProvidedByUser)
        while True:
            try:
                for camera in self.cameras:
                    camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
                break
            except pylon.TimeoutException:
                print("Camera trigger is not ready")
        print("Camera trigger is ready")
        
    def image_saver_thread(self, image_queue, camera_index):
        while True:
            try:
                image, filename = image_queue.get(timeout=1)
                cv2.imwrite(filename, image)
            except queue.Empty:
                pass
    
    def start_saver_threads(self):
        for i, image_queue in enumerate(self.image_queues):
            saver_thread = Thread(target=self.image_saver_thread, args=(image_queue, i))
            saver_thread.daemon = True
            saver_thread.start()
            self.saver_threads.append(saver_thread)

    def create_folder(self):
        for i in range(self.number_of_cameras):
            pathlib.Path(f"cam_{i}").mkdir(parents=True, exist_ok=True)

    def run(self):
        # cv2.namedWindow('Acquisition', cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('Acquisition', 1280, 512)
        self.create_folder()
        self.start_grabbing()
        self.start_saver_threads()

        while True: #any(camera.IsGrabbing() for camera in self.cameras):
            for i, camera in enumerate(self.cameras):
                grab_result = camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
    
                if grab_result.GrabSucceeded():
                    image = cv2.cvtColor(grab_result.GetArray(), cv2.COLOR_BGR2RGB)
                    camera_context_value = grab_result.GetCameraContext()
                    image_filename = f"cam_{i}/image_{camera_context_value}_{grab_result.ImageNumber}.png"
                    self.image_queues[i].put((image, image_filename))
            
            # If ESC is pressed, exit and destroy the window
            # cv2.imshow('Acquisition', np.hstack([self.cameras[i].RetrieveResult(5000).GetArray() for i in range(self.number_of_cameras)]))
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    max_number_cameras = 3
    camera_manager = CameraManager(max_number_cameras)
    camera_manager.initialize_cameras()
    camera_manager.run()