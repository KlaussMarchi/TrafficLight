# conda activate base
import os
os.environ['QT_LOGGING_RULES'] = '*=false'
import csv
import cv2


class DataManager:
    EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    def __init__(self, dataDir, outputFile):
        self.dataDir     = dataDir
        self.outputFile  = outputFile
        self.annotations = []
        self.processed   = set()
        self.imageFiles  = []

    def update(self):
        if os.path.exists(self.outputFile):
            with open(self.outputFile, 'r', newline='') as file:
                reader = csv.reader(file); next(reader, None)
                self.processed = {row[0] for row in reader if row}

        for root, _, files in os.walk(self.dataDir):
            for name in files:
                path = os.path.join(root, name)

                if name.startswith('.') or not name.lower().endswith(self.EXTENSIONS):
                    continue

                if path not in self.processed:
                    self.imageFiles.append(path)

        self.imageFiles.sort()

    def add(self, path, label, bbox):
        self.annotations.append([path, label, *bbox])

    def export(self):
        if not self.annotations:
            return

        exists = os.path.exists(self.outputFile)

        with open(self.outputFile, 'a', newline='') as file:
            writer = csv.writer(file)
            if not exists: writer.writerow(['path', 'label', 'x_min', 'y_min', 'x_max', 'y_max'])
            writer.writerows(self.annotations)


class ImageAnnotator:
    WIDTH  = 800
    HEIGHT = 900

    def __init__(self, manager):
        self.manager = manager
        self.window  = 'Anotador'
        self.drawing = False
        self.origin  = (0, 0)
        self.bbox    = None
        self.clean   = None
        self.image   = None

    def handle(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True; self.origin = (x, y); self.bbox = None
            self.image = self.clean.copy()
            return

        if event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.image = self.clean.copy()
            cv2.rectangle(self.image, self.origin, (x, y), (0, 255, 0), 2)
            return

        if event == cv2.EVENT_LBUTTONUP and self.drawing:
            self.drawing = False
            self.bbox    = (min(self.origin[0], x), min(self.origin[1], y), max(self.origin[0], x), max(self.origin[1], y))
            cv2.rectangle(self.image, self.origin, (x, y), (0, 255, 0), 2)

    def start(self):
        cv2.namedWindow(self.window)
        cv2.setMouseCallback(self.window, self.handle)

        for path in self.manager.imageFiles:
            original = cv2.imread(path)

            if original is None:
                continue

            h, w           = original.shape[:2]
            scaleX, scaleY = w / self.WIDTH, h / self.HEIGHT
            label          = os.path.basename(os.path.dirname(path))

            self.clean = cv2.resize(original, (self.WIDTH, self.HEIGHT))
            self.image = self.clean.copy()
            self.bbox  = None

            while True:
                cv2.imshow(self.window, self.image)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    return self.stop()

                if key == ord('r'):
                    self.image = self.clean.copy(); self.bbox = None; self.drawing = False
                    continue

                if key in (ord('c'), 13):
                    if self.bbox is None:
                        break

                    box = (int(self.bbox[0] * scaleX), int(self.bbox[1] * scaleY), int(self.bbox[2] * scaleX), int(self.bbox[3] * scaleY))
                    self.manager.add(path, label, box)
                    print(f'[salvo] classe: {label} | arquivo: {os.path.basename(path)} | bbox: {box}')
                    break

        self.stop()

    def stop(self):
        self.manager.export()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    baseDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    manager = DataManager(baseDir, os.path.join(baseDir, 'DataBase.csv'))
    manager.update()

    annotator = ImageAnnotator(manager)
    annotator.start()
