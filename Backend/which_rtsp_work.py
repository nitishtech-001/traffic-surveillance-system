import cv2
import numpy as np
import requests
import time
from threading import Thread
from queue import Queue
import sys
import ultralytics
### FIRST METHOD TO GET THE VIDEO FEED

import cv2
import numpy as np
import requests
import time

model = ultralytics.YOLO("./ai_models/nightvision.pt")

def get_camera1():
    url = "http://192.168.29.2:8080/video"
    stream = requests.get(url, auth=("nk", "nk001"), stream=True)

    bytes_buffer = b""
    for chunk in stream.iter_content(chunk_size=1024):
        bytes_buffer += chunk
        start = bytes_buffer.find(b'\xff\xd8')
        end = bytes_buffer.find(b'\xff\xd9')
        if start != -1 and end != -1:
            jpg = bytes_buffer[start:end+2]
            bytes_buffer = bytes_buffer[end+2:]
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            result = model.predict(frame)
            print(result)
            # send_to_frontend(result)   # e.g. via websocket, API call, etc.

        pass  # replace with your actual pipeline


    sys.exit("First method check")


def get_camera2():
    url = "http://nk:nk001@192.168.29.2:8080/video"
    cap = cv2.VideoCapture(url)

    
        # sys.exit("camera connection error...")
        

    while True:
        # Read a frame from the mobile camera
        if cap is None or not cap.isOpened():
            print("connecting... to the camera ....")
            cap = cv2.VideoCapture(url)

        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to grab frame.")
            cap = None
            continue

        frame = cv2.resize(frame, (800,800))
        cv2.imshow("Mobile CCTV Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def print_hello():
    time_exe = 0
    while True:
        print("hello world ")
        time.sleep(2)
        time_exe += 2

thread1 = Thread(target=get_camera2,daemon=True)
thread2 = Thread(target=print_hello)
thread1.start()
thread2.start()
sys.exit("checking get camera 2 functions")

### SECOND METHOD










class IPWebcamStream:
    def __init__(self, ip, port, username=None, password=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        
        # Build the working URL
        if username and password:
            self.shot_url = f"http://{username}:{password}@{ip}:{port}/shot.jpg"
        else:
            self.shot_url = f"http://{ip}:{port}/shot.jpg"
        
        self.frame = None
        self.running = False
        self.fps = 10  # Adjust based on your needs
        self.thread = None
        
    def get_frame(self):
        """Capture a single frame from the camera"""
        try:
            response = requests.get(self.shot_url, timeout=2)
            if response.status_code == 200:
                img_array = np.array(bytearray(response.content), dtype=np.uint8)
                frame = cv2.imdecode(img_array, -1)
                return frame
        except Exception as e:
            print(f"Frame capture error: {e}")
        return None
    
    def start(self):
        """Start the stream in a separate thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = Thread(target=self._update, daemon=True)
        self.thread.start()
        print(f"✅ Stream started at {self.fps} FPS")
        return self
    
    def _update(self):
        """Background thread to continuously capture frames"""
        while self.running:
            frame = self.get_frame()
            if frame is not None:
                self.frame = frame
            else:
                print("⚠️ Failed to capture frame")
            time.sleep(1 / self.fps)
    
    def read(self):
        """Get the latest frame (non-blocking)"""
        return self.frame
    
    def stop(self):
        """Stop the stream"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("Stream stopped")
    
    def set_fps(self, fps):
        """Adjust the capture rate"""
        self.fps = max(1, min(30, fps))  # Limit between 1-30 FPS

# ============================================
# USAGE EXAMPLES
# ============================================

def example_1_basic_stream():
    """Simple stream with display"""
    stream = IPWebcamStream("192.168.29.2", 8080, "nk", "nk001")
    stream.start()
    
    print("Streaming... Press 'q' to quit")
    
    while True:
        frame = stream.read()
        if frame is not None:
            cv2.imshow('IP Webcam Stream', frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Waiting for frame...")
            time.sleep(0.1)
    
    stream.stop()
    cv2.destroyAllWindows()

def example_2_with_ai_processing():
    """Stream with AI processing (simulated)"""
    stream = IPWebcamStream("192.168.29.2", 8080, "nk", "nk001")
    stream.start()
    
    print("AI Processing Stream... Press 'q' to quit")
    
    while True:
        frame = stream.read()
        if frame is not None:
            # ===== YOUR AI MODEL GOES HERE =====
            # Example: Draw a rectangle (simulate detection)
            height, width = frame.shape[:2]
            cv2.rectangle(frame, (50, 50), (width-50, height-50), (0, 255, 0), 2)
            cv2.putText(frame, "AI Processing Active", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Add timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, height-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('AI Processed Stream', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    stream.stop()
    cv2.destroyAllWindows()

def example_3_save_frames():
    """Save frames to disk"""
    stream = IPWebcamStream("192.168.29.2", 8080, "nk", "nk001")
    stream.start()
    
    frame_count = 0
    max_frames = 50
    
    print(f"Saving {max_frames} frames...")
    
    while frame_count < max_frames:
        frame = stream.read()
        if frame is not None:
            # Save frame
            filename = f"frame_{frame_count:04d}.jpg"
            cv2.imwrite(filename, frame)
            print(f"✅ Saved {filename}")
            frame_count += 1
        else:
            print("Waiting for frame...")
            time.sleep(0.1)
    
    stream.stop()
    print("All frames saved!")

def example_4_fastest_stream():
    """Optimized for speed"""
    stream = IPWebcamStream("192.168.29.2", 8080, "nk", "nk001")
    stream.set_fps(15)  # Try 15 FPS
    stream.start()
    
    print("Fast stream (15 FPS)... Press 'q' to quit")
    
    # Pre-allocate frame display
    cv2.namedWindow('Fast Stream', cv2.WINDOW_NORMAL)
    
    while True:
        start_time = time.time()
        
        frame = stream.read()
        if frame is not None:
            cv2.imshow('Fast Stream', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Control loop speed
        elapsed = time.time() - start_time
        if elapsed < 0.05:  # ~20ms per frame
            time.sleep(0.05 - elapsed)
    
    stream.stop()
    cv2.destroyAllWindows()

# ============================================
# RUN THE EXAMPLES
# ============================================
# TODO: COMMENTING MAIN FOR CHECKING PURPOSE
if __name__ == "_main_": ## TODO : FIX THE MAIN VARIABLE
    print("=" * 50)
    print("IP Webcam Stream - Working Solution")
    print("=" * 50)
    print("\nSelect an example:")
    print("1. Basic Stream with Display")
    print("2. AI Processing (Simulated)")
    print("3. Save Frames to Disk")
    print("4. Fast Stream (Optimized)")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        example_1_basic_stream()
    elif choice == "2":
        example_2_with_ai_processing()
    elif choice == "3":
        example_3_save_frames()
    elif choice == "4":
        example_4_fastest_stream()
    else:
        print("Invalid choice")