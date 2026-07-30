# conda activate base
import os, cv2, serial
from Stream.index import CameraStream
from Detector.index import Detector


class CameraTester:
    def __init__(self, port, baud, modelDir=None):
        self.stream   = CameraStream(port=port, baud=baud, window='Deteccao de Semaforo')
        self.detector = Detector(modelDir)

    def start(self):
        self.detector.update()
        self.stream.connect()
        cv2.namedWindow(self.stream.window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.stream.window, 800, 600)

        try:
            while cv2.waitKey(1) & 0xFF != ord('q'):
                frame = self.stream.get()

                if frame is None:
                    print('frame perdido, tentando de novo...')
                    continue

                cv2.imshow(self.stream.window, self.detector.process(frame))
                self.update()
        except KeyboardInterrupt:
            print('interrompido pelo usuario')
        except serial.SerialException as err:
            print(f'erro na serial: {err}')
        finally:
            self.stream.stop()


if __name__ == '__main__':
    tester = CameraTester(port='/dev/ttyUSB0', baud=921600)
    tester.start()
