# conda activate base
import os, cv2
from Detector.index import Detector


class VideoTester:
    WINDOW = 'Deteccao de Semaforo'

    def __init__(self, videoPath, modelDir=None):
        self.videoPath = videoPath
        self.detector  = Detector(modelDir)

    def start(self):
        self.detector.update()
        video = cv2.VideoCapture(self.videoPath)
        cv2.namedWindow(self.WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.WINDOW, 800, 600)

        while video.isOpened():
            ok, frame = video.read()

            if not ok:
                break

            cv2.imshow(self.WINDOW, self.detector.process(frame))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    base   = os.path.dirname(os.path.abspath(__file__))
    tester = VideoTester(videoPath=os.path.join(base, 'video.mp4'))
    tester.start()
