import numpy as np
import cv2
import time
import mss
import threading
import os
import queue


class video_recorder:
    def __init__(self):
        self.capture_thread = None
        self.output_thread = None

        self.state = "IDLE"
        self.buffer = queue.Queue()

        self.filename = None
        self.monitor = None
        self.width = 0
        self.height = 0
        self.max_frames = 0
        self.fps = 0.0
        self.compress = False

    def start_recorder(self, filename="recording.avi", max_length=10, monitor=1, scale=1.0, fps=5.0, compress="True"):
        self.filename = filename
        self.fps = float(fps)
        self.max_frames = round(self.fps * float(max_length))
        self.compress = compress.lower() == "true"

        self.state = "RUNNING"

        with mss.mss() as sct:
            # Part of the screen to capture
            self.monitor = sct.monitors[int(monitor)]
            self.width = round(self.monitor["width"] * float(scale))
            self.height = round(self.monitor["height"] * float(scale))

        self.output_thread = threading.Thread(target=self._write_file)
        self.capture_thread = threading.Thread(target=self._capture)
        self.output_thread.start()
        self.capture_thread.start()

    def stop_recorder(self):
        self.state = "STOPPING"
        self.capture_thread.join()
        self.output_thread.join()

    def cancel_recorder(self):
        self.stop_recorder()
        os.remove(self.filename)

    def get_monitors(self):
        with mss.mss() as sct:
            return sct.monitors

    def _write_file(self):
        num_frames = 0
        prev_frame = None

        fourcc = cv2.VideoWriter_fourcc(*'VP80')
        out = cv2.VideoWriter(self.filename, fourcc, self.fps, (self.width, self.height))

        while True:
            if num_frames == self.max_frames:
                break

            ts, frame = self.buffer.get()
            print(num_frames, ts)
            if frame == "END":
                break

            if compress and prev_frame is not None and (prev_frame==frame).all():
                continue

            num_frames += 1
            prev_frame = frame

            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            frame = cv2.resize(frame, (width, height))

            cv2.putText(frame, '{0:.2f}'.format(ts), (10, 30),  cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 4)
            out.write(frame)

        out.release()
        self.state = "STOPPING"

    def _capture(self):
        with mss.mss() as sct:
            frame_number = 0
            start_time = time.time()

            while True:
                if self.state == "STOPPING":
                    break

                trigger_time = start_time + frame_number / fps
                while time.time() < trigger_time:
                    time.sleep(0.001)
                frame_number += 1

                # Get raw pixels from the screen, save it to a Numpy array
                frame = np.array(sct.grab(monitor))
                self.buffer.put_nowait((time.time() - start_time, frame))

        self.buffer.put_nowait((time.time() - start_time, "END"))




