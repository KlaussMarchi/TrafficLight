import torch
import torchvision
import torch.optim as optim

from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.retinanet import RetinaNetClassificationHead
from .metrics.index import JaccardIndex, ConfusionMatrix


class ModelNetwork:
    def __init__(self, network, img_size, classes, channels=3, lr=1e-4, score_threshold=0.5):
        self.network  = network
        self.img_size = img_size
        self.classes  = classes
        self.channels = channels
        self.score_threshold = score_threshold
        self.lr = lr

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model  = self.get().to(self.device)
        self.optimizer = optim.AdamW(self.model.parameters(), lr=self.lr, weight_decay=1e-4)

        self.iou    = JaccardIndex(num_classes=self.classes, threshold=self.score_threshold)
        self.matrix = ConfusionMatrix(num_classes=self.classes, score_threshold=self.score_threshold)

    def get(self):
        if self.network == 'fasterrcnn':
            model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights='DEFAULT')
            in_features = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(in_features, self.classes)
            return model

        if self.network == 'fasterrcnn_mobile':
            model = torchvision.models.detection.fasterrcnn_mobilenet_v3_large_fpn(weights='DEFAULT')
            in_features = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(in_features, self.classes)
            return model

        if self.network == 'retinanet':
            model = torchvision.models.detection.retinanet_resnet50_fpn(weights='DEFAULT')
            model.head.classification_head = RetinaNetClassificationHead(model.backbone.out_channels, model.head.classification_head.num_anchors, self.classes)
            return model

        if self.network == 'ssd':
            return torchvision.models.detection.ssd300_vgg16(weights_backbone='DEFAULT', num_classes=self.classes)

        raise ValueError(f'unknown network: {self.network}')
