from pypylon import pylon
import numpy as np
import cv2
from imageio import get_writer
from threading import Thread
import queue

# MAX_NUMBER_CAMERAS = 2

# # trigger jel nelkul nem megy a kamera
# # kapcsolo kell mivel trigger jel nelkul nem megy
# # minden kamera kulon threaden legyen  es kulon legyen feldolgozva?
# # ne blokkoljak egymast?

# cv2.namedWindow('Acquisition', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('Acquisition', 1280, 512)

# def image_saver_thread(image_queue):
#     while True:
#         try:
#             image, filename = image_queue.get(timeout=1)
#             cv2.imwrite(filename, image)
#         except queue.Empty:
#             pass

# tlFactory = pylon.TlFactory.GetInstance()
# devices = tlFactory.EnumerateDevices()
# if len(devices) == 0:
#     raise pylon.RUNTIME_EXCEPTION("No camera present.")

# cameras = pylon.InstantCameraArray((min(len(devices), MAX_NUMBER_CAMERAS)))

# for i, camera in enumerate(cameras):
#     camera.Attach(tlFactory.CreateDevice(devices[i]))

# cameras.Open()

# for i, camera in enumerate(cameras):
#     camera.TriggerSelector.SetValue("FrameStart")
#     camera.TriggerMode.SetValue("On")
#     camera.TriggerSource.SetValue("Line1")
#     camera.PixelFormat.SetValue("RGB8")
#     camera.StreamGrabber.MaxTransferSize = 4194304

# # Starts grabbing for all cameras
# cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, 
#                       pylon.GrabLoop_ProvidedByUser)

# # Create a queue for image saving
# image_queue = queue.Queue()

# # Create and start the image saver thread
# saver_thread = Thread(target=image_saver_thread, args=(image_queue,))
# saver_thread.daemon = True  # The thread will exit when the main program exits
# saver_thread.start()



# while cameras.IsGrabbing():
#     grabResult1 = cameras[0].RetrieveResult(5000, 
#                          pylon.TimeoutHandling_ThrowException)
    
#     grabResult2 = cameras[1].RetrieveResult(5000, 
#                          pylon.TimeoutHandling_ThrowException)

    
#     if grabResult1.GrabSucceeded():

#         im1 = cv2.cvtColor(grabResult1.GetArray(), cv2.COLOR_BGR2RGB)
#         im2 = cv2.cvtColor(grabResult2.GetArray(), cv2.COLOR_BGR2RGB)


#         cameraContextValue = grabResult1.GetCameraContext()
#         cameraContextValue2 = grabResult2.GetCameraContext()

#         image_filename1 = f"cam_0/image_{cameraContextValue}_{grabResult1.ImageNumber}.png"
#         image_filename2 = f"cam_1/image_{cameraContextValue2}_{grabResult2.ImageNumber}.png"
        
#         cv2.imwrite(image_filename1, im1)
#         cv2.imwrite(image_filename2, im2)

#         image_queue.put((im1, image_filename1))
#         image_queue.put((im2, image_filename2))

#         # If ESC is pressed exit and destroy window
#         cv2.imshow('Acquisition',np.hstack([im1,im2]))
#         if cv2.waitKey(1) & 0xFF == 27:
#             break

# cv2.destroyAllWindows()

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
            camera.TriggerSource.SetValue(f"Line1") # FIX
            camera.PixelFormat.SetValue("RGB8")
            camera.StreamGrabber.MaxTransferSize = 4194304
    
    def start_grabbing(self):
        if not self.cameras:
            raise RuntimeError("Cameras not initialized.")

        self.cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, 
                      pylon.GrabLoop_ProvidedByUser)
        is_true = True
        while is_true:   
            try:
                while is_true:
                    is_true = not self.cameras[0].RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
            except pylon.TimeoutException:
                print("camera trigger is not ready")
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
    
    def run(self):
        cv2.namedWindow('Acquisition', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Acquisition', 1280, 512)

        self.start_grabbing()
        self.start_saver_threads()

        while True: #any(camera.IsGrabbing() for camera in self.cameras):
            t = []
            grab_results = []
            for i, camera in enumerate(self.cameras):
                grab_result = camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
                # t.append(grab_result.GrabSucceeded())
                # grab_results.append(grab_result)
                if grab_result.GrabSucceeded():
                    image = cv2.cvtColor(grab_result.GetArray(), cv2.COLOR_BGR2RGB)
                    camera_context_value = grab_result.GetCameraContext()
                    image_filename = f"cam_{i}/image_{camera_context_value}_{grab_result.ImageNumber}.png"
                    self.image_queues[i].put((image, image_filename))
            # print(t)
            # if all(t):
            #     images = [cv2.cvtColor(grab_result.GetArray(), cv2.COLOR_BGR2RGB) for grab_result in grab_results]
            #     camera_context_values = [grab_result.GetCameraContext() for grab_result in grab_results]
            #     image_numbers = [grab_result.ImageNumber for grab_result in grab_results]
            #     image_filenames = [f"cam_{i}/image_{camera_context_values[i]}_{image_numbers[i]}.png" for i in range(self.number_of_cameras)]
            #     for i, image in enumerate(images):
            #         self.image_queues[i].put((image, image_filenames[i]))
            # If ESC is pressed, exit and destroy the window
            # cv2.imshow('Acquisition', np.hstack([self.cameras[i].RetrieveResult(5000).GetArray() for i in range(self.number_of_cameras)]))
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    max_number_cameras = 2
    camera_manager = CameraManager(max_number_cameras)
    camera_manager.initialize_cameras()
    camera_manager.run()