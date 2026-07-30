import math, subprocess
from array import array
from time import time

try:
    import RPi.GPIO as GPIO
    print('raspberry configurado')
except ImportError:
    print('configuração no PC')
    GPIO = None

try:
    import winsound
except ImportError:
    winsound = None


class Smoother:
    def __init__(self, size):
        self.size = size
        self.reset()

    def reset(self):
        self.array = [0.0] * self.size
        self.sum   = 0.0
        self.i     = 0

    def update(self, value):
        self.sum -= self.array[self.i]
        self.array[self.i] = float(value)
        self.sum += self.array[self.i]
        self.i = (self.i + 1) % self.size
        return self.sum / self.size


class Relay:
    HIGH_LEVEL  = 0.95
    LOW_LEVEL   = 0.05
    ACTIVE_HIGH = True
    PULSE       = 1.0

    def __init__(self, pin=16, size=5):
        self.pin    = pin
        self.state  = False
        self.red    = None
        self.since  = 0.0
        self.states = Smoother(size)
        self.setup()

    def setup(self):
        if GPIO is None:
            return print('RPi.GPIO indisponivel, avisando por beep no PC')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.set(False)

    def update(self, label=None):
        if self.state and (time() - self.since) > self.PULSE:
            self.set(False)

        if label is None:
            return self.red

        mean = self.states.update(label == 'red')
        red  = True if mean >= self.HIGH_LEVEL else (False if mean <= self.LOW_LEVEL else self.red)

        if red != self.red and self.red is not None:
            print(f'semaforo {"entrou no" if red else "saiu do"} vermelho -> {label}, acionando rele')
            self.set(True)

        self.red = red
        return self.red

    def set(self, state=False):
        self.state = state
        self.since = time()

        if GPIO is not None:
            return GPIO.output(self.pin, state == self.ACTIVE_HIGH)

        if state:
            self.beep()

    def beep(self):
        if winsound is not None:
            return winsound.Beep(1000, 250)

        rate = 44100
        wave = array('h', [int(16000 * math.sin(2 * math.pi * 1000 * i / rate)) for i in range(rate // 4)])

        try:
            subprocess.run(['paplay', '--raw', '--format=s16le', f'--rate={rate}', '--channels=1'], input=wave.tobytes())
        except FileNotFoundError:
            print('\a', end='', flush=True)

    def stop(self):
        self.set(False)

        if GPIO is not None:
            GPIO.cleanup()
