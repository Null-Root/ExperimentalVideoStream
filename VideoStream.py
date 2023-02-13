import cv2

class VideoHandler:
    def __init__(self) -> None:
        self.ret = False
        self.frame = None
        self.capture = None

    def get_frame(self):
        return self.ret, self.frame
    
    def is_capturing(self):
        return self.captureFlag

    def start_capture(self):
        self.captureFlag = True
        self.capture = cv2.VideoCapture(0)

        while self.capture.isOpened() and self.captureFlag:
            self.ret, self.frame = self.capture.read()

            if self.ret == False:
                continue

            cv2.imshow('Server', self.frame)

            # Case Insensitive Check
            if ord(chr(cv2.waitKey(1) & 0xFF).lower()) == ord('b'):
                break

        self.capture.release()
        cv2.destroyAllWindows()
    
    def stop_capture(self):
        self.captureFlag = False