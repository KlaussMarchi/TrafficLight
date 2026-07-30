import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from torchvision.ops import box_iou


class JaccardIndex:
    def __init__(self, num_classes, threshold=0.5):
        self.num_classes = num_classes
        self.threshold   = threshold
        self.reset()

    def reset(self):
        self.history = {c: [] for c in range(1, self.num_classes)}

    def update(self, outputs, targets):
        batch = {c: [] for c in range(1, self.num_classes)}

        for out, tgt in zip(outputs, targets):
            mask = out['scores'] >= self.threshold
            pred_boxes, pred_labels = out['boxes'][mask], out['labels'][mask]
            gt_boxes, gt_labels     = tgt['boxes'], tgt['labels']

            for c in range(1, self.num_classes):
                c_pred = pred_boxes[pred_labels == c]
                c_gt   = gt_boxes[gt_labels == c]

                if len(c_pred) == 0 and len(c_gt) == 0:
                    continue

                val = 0.0 if len(c_pred) == 0 or len(c_gt) == 0 else box_iou(c_pred, c_gt).max(dim=0).values.mean().item()
                batch[c].append(val)
                self.history[c].append(val)

        means = [sum(vals) / len(vals) for vals in batch.values() if len(vals) > 0]
        return sum(means) / len(means) if len(means) > 0 else 0.0

    def compute(self):
        class_ious = {c: sum(vals) / len(vals) for c, vals in self.history.items() if len(vals) > 0}
        mean_iou   = sum(class_ious.values()) / len(class_ious) if len(class_ious) > 0 else 0.0
        return (mean_iou, class_ious)


class ConfusionMatrix:
    def __init__(self, num_classes, score_threshold=0.5, iou_threshold=0.5):
        self.num_classes     = num_classes
        self.score_threshold = score_threshold
        self.iou_threshold   = iou_threshold
        self.reset()

    def reset(self):
        self.matrix = np.zeros((self.num_classes, self.num_classes), dtype=np.int32)

    def update(self, outputs, targets):
        for out, tgt in zip(outputs, targets):
            mask = out['scores'] >= self.score_threshold
            pred_boxes, pred_labels = out['boxes'][mask], out['labels'][mask]
            gt_boxes, gt_labels     = tgt['boxes'], tgt['labels']

            if len(gt_boxes) == 0 and len(pred_boxes) == 0:
                continue

            if len(pred_boxes) == 0:
                for gl in gt_labels:
                    self.matrix[gl.item()][0] += 1
                continue

            if len(gt_boxes) == 0:
                for pl in pred_labels:
                    self.matrix[0][pl.item()] += 1
                continue

            iou_matrix = box_iou(pred_boxes, gt_boxes)
            matched    = set()

            for gt_ix, gl in enumerate(gt_labels):
                best_ix  = iou_matrix[:, gt_ix].argmax().item()
                best_iou = iou_matrix[best_ix, gt_ix].item()

                if best_iou >= self.iou_threshold:
                    self.matrix[gl.item()][pred_labels[best_ix].item()] += 1
                    matched.add(best_ix)
                else:
                    self.matrix[gl.item()][0] += 1

            for pred_ix, pl in enumerate(pred_labels):
                if pred_ix not in matched:
                    self.matrix[0][pl.item()] += 1

    def plot(self, names=None, title='Matriz de Confusão'):
        names = names if names is not None else [str(c) for c in range(self.num_classes)]
        norm  = self.matrix.astype('float') / (self.matrix.sum(axis=1)[:, np.newaxis] + 1e-6)
        sns.heatmap(norm, annot=self.matrix, fmt='d', cmap='Blues', xticklabels=names, yticklabels=names, annot_kws={'size': 12, 'weight': 'bold'})
        plt.title(title)
        plt.xlabel('Predito')
        plt.ylabel('Real')
