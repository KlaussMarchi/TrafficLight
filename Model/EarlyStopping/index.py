class EarlyStopping:
    def __init__(self, patience=15, mode='max', min_delta=1e-4):
        self.patience = patience
        self.mode = mode
        self.min_delta = min_delta
        self.best = None
        self.num_bad = 0
        self.best_state = None

    @staticmethod
    def snapshot(model):
        # best state lives on the CPU so the snapshot never competes with training for VRAM
        return {key: value.detach().to('cpu', copy=True) for key, value in model.state_dict().items()}

    def ready(self, model, metric):
        if self.best is None:
            self.best = metric
            self.best_state = self.snapshot(model)
            return False

        improved = (metric > self.best + self.min_delta) if self.mode == 'max' else (metric < self.best - self.min_delta)

        if improved:
            self.best = metric
            self.num_bad = 0
            self.best_state = self.snapshot(model)
            print(f'(early stopping) model improved to {metric:.4f}')
        else:
            self.num_bad += 1

        return self.num_bad >= self.patience

    def restore_best(self, model):
        if self.best_state is not None:
            model.load_state_dict(self.best_state)
