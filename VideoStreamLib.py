import cv2

class VideoStream:
    def __init__(self) -> None:
        self.ret = False
        self.frame = None
        self.capture = None
        self.captureFlag = True

    def get_frame(self):
        return self.ret, self.frame
    
    def is_capturing(self):
        return self.captureFlag

    def start_capture(self):
        self.captureFlag = True
        self.capture = cv2.VideoCapture(0)

    def handle_capturing(self):
        while self.capture.isOpened() and self.captureFlag:
            self.ret, self.frame = self.capture.read()

            # Show the frame
            cv2.imshow('frame', self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if self.ret == False:
                continue

        self.capture.release()
        cv2.destroyAllWindows()
    
    def stop_capture(self):
        self.captureFlag = False