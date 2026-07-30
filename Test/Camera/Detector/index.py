import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../Model'))

import torch, cv2
import numpy as np
from torchvision.ops import nms

from Network.index import ModelNetwork
from Augmentation.index import Augmentation


class Detector:
    colors = {'green': (0, 255, 0), 'red': (0, 0, 255), 'yellow': (0, 255, 255)}

    def __init__(self, modelDir=None, threshold=None):
        self.modelDir  = modelDir
        self.threshold = threshold
        self.backupDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../Model/Backup')
        self.found     = []

    def best(self):
        score  = lambda name: json.load(open(os.path.join(self.backupDir, name, 'info.json'))).get('trainer', {}).get('test_iou', float('-inf'))
        models = [name for name in os.listdir(self.backupDir) if name.startswith('model_')]
        return os.path.join(self.backupDir, max(models, key=score))

    def update(self):
        self.modelDir = self.modelDir if self.modelDir is not None else self.best()

        with open(os.path.join(self.modelDir, 'info.json')) as file:
            self.info = json.load(file)

        options   = self.info['model']
        self.size = options['img_size']
        self.nms  = self.info['processing'].get('nms_threshold', 0.3)
        self.threshold = self.threshold if self.threshold is not None else options['score_threshold']

        self.network = ModelNetwork(**options)
        data = torch.load(os.path.join(self.modelDir, 'model.pth'), map_location=self.network.device)
        self.network.model.load_state_dict(data['model'])
        self.network.model.eval()

        self.aug    = Augmentation(self.size)
        self.labels = {value: name for name, value in self.info['classes'].items()}
        print(f'modelo carregado: {os.path.basename(self.modelDir)} ({options["network"]}, IoU de teste {self.info["trainer"]["test_iou"]:.3f})')

    def process(self, frame):
        image  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        tensor = self.aug(image=image, bboxes=np.zeros((0, 4)), labels=[])['image'].unsqueeze(0).to(self.network.device)

        with torch.no_grad():
            pred = self.network.model(tensor)[0]

        keep = nms(pred['boxes'], pred['scores'], self.nms)
        boxes, scores, labels = pred['boxes'][keep], pred['scores'][keep], pred['labels'][keep]

        h, w  = frame.shape[:2]
        scale = self.size / max(h, w)
        padX  = (self.size - int(round(w * scale))) // 2
        padY  = (self.size - int(round(h * scale))) // 2
        self.found = []

        for box, score, label in zip(boxes.cpu().numpy(), scores.cpu().numpy(), labels.cpu().numpy()):
            if score < self.threshold:
                continue

            xMin, yMin = max(0, int((box[0] - padX) / scale)), max(0, int((box[1] - padY) / scale))
            xMax, yMax = min(w, int((box[2] - padX) / scale)), min(h, int((box[3] - padY) / scale))
            name  = self.labels.get(int(label), 'unknown')
            color = self.colors.get(name, (255, 255, 255))

            self.found.append({'label': name, 'score': float(score), 'bbox': (xMin, yMin, xMax, yMax)})
            cv2.rectangle(frame, (xMin, yMin), (xMax, yMax), color, 2)
            cv2.putText(frame, f'{name} {score:.2f}', (xMin, yMin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame
