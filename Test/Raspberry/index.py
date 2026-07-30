# conda activate base
import cv2, serial
from Stream.index import CameraStream
from Detector.index import Detector
from Relay.index import Relay


class Raspberry:
    WINDOW = 'Deteccao de Semaforo'

    def __init__(self, port, baud, modelDir=None, pin=16, show=False):
        self.stream   = CameraStream(port=port, baud=baud, window=self.WINDOW)
        self.detector = Detector(modelDir)
        self.relay    = Relay(pin=pin)
        self.show     = show

    def start(self):
        self.detector.update()
        self.stream.connect()

        if self.show:
            cv2.namedWindow(self.WINDOW, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.WINDOW, 800, 600)

        try:
            while True:
                frame = self.stream.get()

                if frame is None:
                    print('frame perdido, tentando de novo...')
                    continue

                canvas = self.detector.process(frame)
                label  = max(self.detector.found, key=lambda found: found['score'], default={}).get('label')
                self.relay.update(label)

                if not self.show:
                    continue

                cv2.imshow(self.WINDOW, canvas)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            print('interrompido pelo usuario')
        except serial.SerialException as err:
            print(f'erro na serial: {err}')
        finally:
            self.relay.stop()
            self.stream.stop()


if __name__ == '__main__':
    tester = Raspberry(port='/dev/ttyUSB0', baud=921600, pin=16, show=True)
    tester.start()
