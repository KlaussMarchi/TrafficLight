import glob
import os
import shutil

import cv2
import numpy as np


def getFiles(path, limit=None, shuffle=False):
    target = sorted(glob.glob(os.path.join(path, '*')))
    if shuffle:
        np.random.shuffle(target)
    return target[:limit]


def getAllFiles(base):
    return [os.path.join(root, file) for root, _, files in os.walk(base) for file in files]


def setFolder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def loadImage(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f'could not read image: {path}')
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def drawBox(canvas, box, text, color, thickness=2):
    xMin, yMin, xMax, yMax = [int(v) for v in box]
    cv2.rectangle(canvas, (xMin, yMin), (xMax, yMax), color, thickness)

    (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(canvas, (xMin, yMin - h - 10), (xMin + w, yMin), color, -1)
    cv2.putText(canvas, text, (xMin, yMin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return canvas
