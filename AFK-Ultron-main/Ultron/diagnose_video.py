import cv2
import time
import sys

def test_stream(url):
    print(f"--- DIGNOSIS START ---")
    print(f"Testing URL: {url}")
    print(f"OpenCV Build Info: {cv2.getBuildInformation().splitlines()[0]}")
    
    try:
        # Set a timeout for opening connection (doesn't always work for all backends but worth trying)
        # On Windows, strictly wait or use CAP_DSHOW if local, but this is network.
        # We'll just try standard open.
        
        start_time = time.time()
        print("Attempting cv2.VideoCapture()...")
        cap = cv2.VideoCapture(url)
        
        if not cap.isOpened():
            print("[FAILURE]: cap.isOpened() returned False.")
            print("Possible causes:")
            print("1. URL is unreachable (wrong IP/Port).")
            print("2. URL is not a direct video stream (maybe a web page?).")
            print("3. Firewall/VPN blocking access.")
            return
            
        print(f"[SUCCESS]: Connection opened in {time.time() - start_time:.2f}s")
        
        print("Attempting to read 10 frames...")
        for i in range(10):
            read_start = time.time()
            ret, frame = cap.read()
            read_dur = time.time() - read_start
            
            if not ret:
                print(f"[FAILURE] Frame {i}: read() returned False (No frame data). Duration: {read_dur:.2f}s")
            else:
                h, w = frame.shape[:2]
                print(f"[SUCCESS] Frame {i}: Size={w}x{h}, Read Time={read_dur:.2f}s")
                
        cap.release()
        print("--- DIAGNOSIS COMPLETE ---")
        
    except Exception as e:
        print(f"[EXCEPTION]: {e}")

if __name__ == "__main__":
    url = "http://100.72.253.48:8080/video"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    test_stream(url)
