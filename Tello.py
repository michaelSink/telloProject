import socket
import threading
import cv2
import sys
from datetime import datetime

class Tello:

    CONTROL_ADDRESS = ('192.168.10.1', 8889)

    def __init__(self):

        # Set up thread for UDP communication responses
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        self.socket.bind(('', 9000))

        threading.Thread(target=self.udp_control_response).start();

        # Start video stream
        self.start_stream()

        # Set up thread for video capture frame read
        self.capture = TelloVideoStream()

    def start_stream(self):
        
        try:
            msg = "command"

            msg = msg.encode(encoding="utf-8") 
            self.socket.sendto(msg, self.CONTROL_ADDRESS)

            msg = "streamon"

            msg = msg.encode(encoding="utf-8") 
            self.socket.sendto(msg, self.CONTROL_ADDRESS)
            print("\nIn SDK mode, and stream is on\n")
        except Exception as e:
            self.stop_processes()

    """
    Purpose: Receive responses from tello drone commands
    Input:
        None
    Output:
        None
    """
    def udp_control_response(self):
        while True:
            try:
                data, _ = self.socket.recvfrom(1518)
                print("[{}] From Tello: {}\n".format(str(datetime.utcnow()), data.decode(encoding="utf-8")))
            except Exception as e:
                print("[{}] Error from UDP Control Resposne: {}".format(str(datetime.utcnow()), e))
                self.stop_processes()

    """
    Purpose: Sending commands to tello through CLI.
    Input:
        None
    Output:
        None
    """
    def send_commands(self):
        while True:
            try:
                msg = input("Command: ");
                if not msg:
                    continue;
                
                if msg == 'q':
                    self.stop_processes()

                msg = msg.encode(encoding="utf-8") 
                self.socket.sendto(msg, self.CONTROL_ADDRESS)
            except Exception as e:
                print("[{}] Error sending data to Tello: {}".format(str(datetime.utcnow()), e))
                self.stop_processes()

    """
    Purpose: Shut down all processes in Tello and TelloVideoFrame
    Input:
        None
    Output:
        None
    """
    def stop_processes(self):
        try:
            # Stop Tello socket
            self.socket.close()

            # Stop TelloVideoFrame processies
            self.capture.stop_processes()

        except Exception as e:
            print("[{}] Error trying to shut down: {}".format(str(datetime.utcnow()), e))
        finally:    
            sys.exit(1)

class TelloVideoStream:

    VIDEO_IP = '0.0.0.0'
    VIDEO_PORT = 11111

    def __init__(self):

        self.udp_address = 'udp://@' + self.VIDEO_IP + ":" + str(self.VIDEO_PORT)
        self.cap = cv2.VideoCapture(self.udp_address)

        self.curr_frame = None
        self.ret = True

        self.process = True

        if not self.cap.isOpened():
            self.cap.open(self.udp_address)

        threading.Thread(target=self.udp_video_capture).start()

    """
    Purpose: While the conditions to process are still
    Input:
        None
    Output:
        None
    """
    def udp_video_capture(self):
        while self.process:
            try:
                if not self.ret or not self.cap.isOpened():
                    self.procecces = False
                else:
                    self.ret, self.curr_frame = self.cap.read()
            except Exception as e:
                print("[{}] Error with video processing: {}".format(str(datetime.utcnow()), e))
                self.stop_processes()

    """
    Purpose: Shut down all procecces relating to TelloVideoStream
    Input:
        None
    Output:
        None
    """
    def stop_processes(self):
        try:

            # Stop processing frames
            self.process = False

            # Destroy created windows
            cv2.destroyAllWindows()

        except Exception as e:
            print("[{}] Error shutting down TelloVideoStream processes: {}".format(str(datetime.utcnow()), e))
        finally:
            sys.exit(1)