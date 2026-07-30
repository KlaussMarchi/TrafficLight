import cv2
import time
import struct
import serial
import numpy as np


class CameraStream:
    HEADER    = b'IMG'
    REQUEST   = b'F'
    BOOT_TIME = 3
    MAX_SIZE  = 200000

    def __init__(self, port='/dev/ttyUSB0', baud=921600, window='Camera ESP32'):
        self.port   = port
        self.baud   = baud
        self.window = window
        self.conn   = None

    def connect(self):
        print(f'conectando em {self.port} a {self.baud} bps...')
        self.conn = serial.Serial(baudrate=self.baud, timeout=2, write_timeout=1, exclusive=True)
        self.conn.port = self.port
        self.conn.dtr  = False
        self.conn.rts  = False
        self.conn.open()
        time.sleep(self.BOOT_TIME)
        self.conn.reset_input_buffer()
        print('conexao aberta, solicitando frames (aperte q para sair)')

    def get(self):
        self.conn.reset_input_buffer()
        self.conn.write(self.REQUEST)
        head = self.conn.read(7)

        if len(head) < 7 or head[:3] != self.HEADER:
            return None

        size = struct.unpack('<I', head[3:])[0]

        if size == 0 or size > self.MAX_SIZE:
            return None

        data = self.conn.read(size)

        if len(data) < size:
            return None

        return cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

    def start(self):
        self.connect()
        cv2.namedWindow(self.window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window, 800, 600)

        try:
            while cv2.waitKey(1) & 0xFF != ord('q'):
                frame = self.get()

                if frame is None:
                    print('frame perdido, tentando de novo...')
                    continue

                cv2.imshow(self.window, frame)
        except KeyboardInterrupt:
            print('interrompido pelo usuario')
        except serial.SerialException as err:
            print(f'erro na serial: {err}')
        finally:
            self.stop()

    def stop(self):
        cv2.destroyAllWindows()

        if self.conn is not None and self.conn.is_open:
            self.conn.close()

        print('conexao encerrada')
