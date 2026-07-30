import torch.nn as nn


class DetectionSumLoss(nn.Module):
    def forward(self, loss_dict):
        return sum(loss_dict.values())


class DetectionWeightedLoss(nn.Module):
    def __init__(self, weights):
        super().__init__()
        self.weights = weights

    def forward(self, loss_dict):
        return sum(self.weights.get(name, 1.0) * loss for name, loss in loss_dict.items())


class Losses:
    detection = {
        'sum': DetectionSumLoss(),
        'classifier': DetectionWeightedLoss({'loss_classifier': 2.0, 'classification': 2.0}),
        'boxes': DetectionWeightedLoss({'loss_box_reg': 2.0, 'loss_rpn_box_reg': 2.0, 'bbox_regression': 2.0}),
    }

    def __new__(cls, name, multiclass=False):
        return cls.detection[name]
