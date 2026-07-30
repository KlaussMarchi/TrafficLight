# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Traffic-light detection (green/red/yellow) with torchvision detectors, fed by an ESP32-CAM over serial and
driving a relay on a Raspberry Pi. Not a git repository. No test suite, no linter, no package manifest.

## Environment

Conda `base` at `~/miniconda3` — `python` is not on PATH until `conda activate base`. Torch + CUDA on an
RTX 3050 6GB (batch sizes and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` in `Analysis.ipynb` exist
because of that ceiling). Jupyter kernel name is `python3`; albumentations is 2.x (`fill=`, `std_range=`).

## Commands

```bash
conda activate base
cd Task && python index.py                  # full pipeline over every config in task.json
python Dataset/Aquisition/index.py          # manual bbox annotator (OpenCV window)
cd Test/Video && python index.py            # inference on Test/Video/video.mp4
cd Test/Camera && python index.py           # inference on the ESP32-CAM serial stream
cd Test/Raspberry && python index.py        # same + relay (RPi only)
cd Hardware && python index.py              # raw ESP32-CAM stream viewer, no model
```

Notebooks use paths relative to their own folder (`../Task/info.json`, `Backup/`, `files/`), so they must be
run with the cwd set to that folder — papermill already does this via `cwd=`. Firmware is Arduino IDE
(`Hardware/Main/Main.ino`, board AI-Thinker ESP32-CAM); there is no CLI build.

## Pipeline

`Task/task.json` is a **list** of run configs — one entry per training round. `Task/index.py` loops it,
writes each entry to `Task/info.json`, then papermills `Dataset/<dataset>/Format.ipynb` and
`Model/Analysis.ipynb`, dropping executed copies in `Task/logs/<name>_out.ipynb`.

`Task/info.json` is the single config channel: every notebook reads it as `OPTIONS` at cell ~3 and derives
its constants from it. `Format.ipynb` also *writes back* to it (overwrites `dataset` with its own folder
name); `Analysis.ipynb` adds the resolved `n_images` split counts before embedding OPTIONS in the backup.

Data flow: `Dataset/Aquisition/files/<label>/*.png` + `files/DataBase.csv` (annotator output, machine-local
paths) → `Format.ipynb` → `Dataset/DataBase.csv` with paths relative to `Dataset/` → `Analysis.ipynb`.
Adding a dataset means a new `Dataset/<Name>/` folder with its own `Format.ipynb` emitting that same CSV
schema (`path,label,x_min,y_min,x_max,y_max`), then setting `"dataset"` in `task.json`.

Predict/PostProc are analysis-only and not in the runner: `Model/Predict.ipynb` re-scores the best backup on
the test split, `Model/PostProc.ipynb` ranks every backup's `info.json` into a comparison table.

## Backups are the model contract

`Analysis.ipynb` auto-increments `Model/Backup/model_N/` and writes `model.pth` (state_dict + optimizer +
history), `info.json`, and the plots. `info.json` has four consumers (`Predict.ipynb`, `PostProc.ipynb`,
`Test/*/Detector`), all of which do the same two things: pick the backup with the highest
`info['trainer']['test_iou']`, then rebuild the net with `ModelNetwork(**info['model'])`. Changing
`ModelNetwork.__init__`'s signature or the `trainer`/`model`/`classes`/`processing` keys breaks every
existing backup — old checkpoints cannot be re-derived.

`model_1` predates that schema (`network`/`classes`/`test_iou` only) and is deliberately kept; consumers
score it as `-inf` and skip it. `PostProc.ipynb` also filters `id >= 3` because `model_2` used the old
non-stratified split.

`Model/progress.json` is overwritten each epoch by `Trainer.start` — a live progress probe for long runs.

## Model modules

`Model/<Component>/index.py`, imported from notebooks by folder name. `Network` builds the detector
(`fasterrcnn`, `fasterrcnn_mobile`, `retinanet`, `ssd`) and owns the `JaccardIndex`/`ConfusionMatrix`
metrics under `Network/metrics/`. `Losses` and `Augmentation` are `__new__` factories returning a
torchvision-ready object, dispatched by the `loss` / `n_aug` (level 0-2) config values. `Augmentation`
deliberately excludes vertical flip and hue shift — the class *is* the lit color and its position.

The letterbox (`LongestMaxSize` + `PadIfNeeded`) is why `Test/*/Detector.process` reverses scale and pad
before drawing: model coordinates are 512×512 padded space, frames are not.

## Inference harnesses

`Test/Camera`, `Test/Video`, `Test/Raspberry` share the same shape: an `index.py` that owns a stream and a
`Detector`, calling `detector.update()` once then `detector.process(frame)` per frame. Each keeps its own
copy of `Detector/index.py` (and `Stream/index.py`) — they are duplicated, not shared, so a fix in one must
be applied to the others. `Detector` reaches the model via `sys.path.insert` of `../../../Model`.

## Firmware

`Hardware/Main/` is the header-only ESP32 component tree: `Main.ino` holds one `Device`, `device/index.h`
composes `Camera<Device>` and `Protocol<Device>` with the parent injected by template pointer, every
component exposes `setup()`/`handle()`, and all pin/tuning constants are `#define`s in `globals/constants.h`.

The wire protocol lives in two places that must stay in sync: `Protocol` on the ESP32 and `CameraStream` in
`Hardware/index.py` (mirrored into `Test/*/Stream/index.py`). Host writes `'F'`, device answers `"IMG"` +
little-endian `uint32` length + JPEG bytes, at 921600 baud, after a 3 s boot wait with DTR/RTS held low.

## Conventions

Global code style is `~/.claude/CLAUDE.md` (English identifiers, Portuguese prose/plots/messages, no
docstrings or type hints, aligned assignments, `update()`/`get()`/`process()`/`start()` method vocabulary,
`Folder/index.*` modules). This repo follows it with two local exceptions: notebook-level variables use
`snake_case` matching the config keys (`train_df`, `val_iou`, `model_options`), and notebook cells end in
visual proof — a bare DataFrame, a chart, or a short shape/metric print. Plot functions take `save=None`
and switch between `plt.show()` and `savefig` on it.
