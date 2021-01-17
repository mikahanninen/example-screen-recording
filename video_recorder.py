import numpy as np
import cv2
import time
import mss
import threading
import os


class video_recorder:
    def __init__(self):
        self.worker = None
        self.filename = None
    
    def start_recorder(self, filename="recording.avi", max_length=60.0, monitor=1, scale=1.0):
        if self.worker:
            raise ValueError("Recorder busy")
        self.filename = filename
        self.worker = threading.Thread(target=self._loop, args=(filename, max_length, monitor, scale))
        self.worker.start()

    def stop_recorder(self, cancel=False):
        worker = self.worker
        self.worker = None
        worker.join()
        if cancel:
            os.remove(self.filename)

    def cancel_recorder(self):
        self.stop_recorder(True)
        
    def get_monitors(self):
        with mss.mss() as sct:
            return sct.monitors
        
    def _loop(self, filename, max_length, monitor, scale):
        with mss.mss() as sct:
            # Part of the screen to capture
            monitor = sct.monitors[monitor]
            width = int(monitor["width"] * scale)
            height = int(monitor["height"] * scale)

            frame_rate = 5
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(filename, fourcc, frame_rate, (width, height))

            frame_number = 0
            start_time = time.time()
            while self.worker and time.time() < start_time + max_length:
                delay = start_time + frame_number / frame_rate - time.time() 
                frame_number += 1
                if delay > 0: 
                    time.sleep(delay)

                # Get raw pixels from the screen, save it to a Numpy array
                frame = np.array(sct.grab(monitor))
                frame = cv2.resize(frame, (width, height))

                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # cv2.putText(frame, "%f" % (time.time() - start_time),
                #            (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                out.write(frame)

        # Clean up
        out.release()
        self.worker = None



