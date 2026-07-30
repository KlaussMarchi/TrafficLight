import cv2
import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2


class Augmentation:
    # sem flip vertical nem hue shift: a classe depende da cor acesa e da orientacao do semaforo
    def __new__(cls, img_size, level=0):
        resize = [
            A.LongestMaxSize(max_size=img_size, p=1.0),
            A.PadIfNeeded(min_height=img_size, min_width=img_size, border_mode=cv2.BORDER_CONSTANT, fill=[0, 0, 0], p=1.0),
        ]

        transforms = []
        if level >= 1:
            transforms += [A.HorizontalFlip(p=0.5), A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5)]

        if level >= 2:
            transforms += [A.Affine(scale=(0.9, 1.1), translate_percent=(-0.05, 0.05), border_mode=cv2.BORDER_CONSTANT, p=0.5), A.GaussNoise(std_range=(0.02, 0.08), p=0.2)]

        params = A.BboxParams(format='pascal_voc', label_fields=['labels'], clip=True)
        return A.Compose(resize + transforms + [ToTensorV2(p=1.0)], bbox_params=params)
