import json
import os
from pathlib import Path
import papermill as pm

KERNEL_NAME = 'python3'


def execute(path):
    p = Path(path)
    dir_path, name, ext = p.parent, p.stem, p.suffix
    print('stage:', name)

    os.makedirs('logs', exist_ok=True)
    out = os.path.join('logs', f'{name}_out{ext}')
    pm.execute_notebook(path, out, kernel_name=KERNEL_NAME, log_output=True, progress_bar=True, cwd=str(dir_path))


with open('task.json', 'r') as file:
    tasks = json.load(file)

for i, task in enumerate(tasks):
    print(f'\n\nRound {i + 1}/{len(tasks)}')

    with open('info.json', 'w') as file:
        file.write(json.dumps(task, indent=4))

    print('info:', task)
    dataset = task.get('dataset')
    execute(f'../Dataset/{dataset}/Format.ipynb')
    execute('../Model/Analysis.ipynb')
