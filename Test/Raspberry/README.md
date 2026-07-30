# Deteccao de semaforo no Raspberry Pi

Le o stream serial da ESP32-CAM, roda o detector e aciona o rele quando o semaforo fica vermelho.
Requer Raspberry Pi OS **64 bits** (Bookworm) — os wheels do torch para ARM so existem em aarch64.

## 1. Pacotes de sistema

```bash
sudo apt update
sudo apt install -y python3-venv python3-dev libgl1 libglib2.0-0
```

## 2. Permissoes de serial e GPIO

```bash
sudo usermod -aG dialout,gpio $USER
```

Saia e entre de novo na sessao (ou reinicie) para os grupos valerem.

## 3. Ambiente Python

```bash
python3 -m venv ~/trafficlight-venv
~/trafficlight-venv/bin/pip install --upgrade pip
~/trafficlight-venv/bin/pip install -r ~/TrafficLight/Test/Raspberry/requirements.txt
```

No Pi 5 o `RPi.GPIO` classico nao funciona: edite o `requirements.txt` trocando-o por `rpi-lgpio`,
que expoe a mesma API e nao exige nenhuma mudanca no codigo.

## 4. Copiar o projeto e o backup do modelo

`.gitignore` exclui `*.pth` e `*.json`, entao os backups **nao vem pelo git** — copie do PC:

```bash
rsync -av --exclude '__pycache__' ~/Projects/TrafficLight/{Model,Test} pi@raspberrypi:~/TrafficLight/
```

Basta um backup em `Model/Backup/` (o melhor hoje e o `model_3`, IoU de teste 0.927). `Detector.best()`
escolhe sozinho o de maior `trainer.test_iou` e ignora o `model_1`, que nao tem esse campo.

## 5. Descobrir a porta da ESP32-CAM

```bash
ls -l /dev/serial/by-id/
```

O padrao no codigo e `/dev/ttyUSB0`. Se voce tiver mais de um dispositivo USB-serial, use o caminho
estavel `/dev/serial/by-id/<id>` no lugar — ele nao troca de numero entre boots.

## 6. Teste manual

```bash
cd ~/TrafficLight/Test/Raspberry
~/trafficlight-venv/bin/python index.py
```

Isso abre a janela de video (`show=True`), entao precisa de desktop. Para testar sem tela, do mesmo
jeito que o servico roda:

```bash
cd ~/TrafficLight/Test/Raspberry
~/trafficlight-venv/bin/python -c "from index import Raspberry; Raspberry(port='/dev/ttyUSB0', baud=921600, pin=16, show=False).start()"
```

O rele esta no BCM 16 e pulsa por 1 s a cada transicao de estado do vermelho. Os ajustes ficam em
`Relay/index.py`: `PULSE` (duracao do pulso), `ACTIVE_HIGH` (modulos de rele chineses costumam ser
active-low — troque para `False` se o rele ligar invertido) e `size` do `Smoother` (quantos frames de
media antes de aceitar a troca de cor).

## 7. Iniciar sozinho no boot

Ver `startscript.txt` — cria e habilita o servico systemd.

## Desempenho

O `model_3` e um `fasterrcnn` resnet50 em 512x512: na CPU do Pi da alguns segundos por frame. Para
semaforo isso costuma bastar, mas se precisar de mais taxa, treine um `fasterrcnn_mobile` ou `ssd`
mudando `"network"` no `Task/task.json` e copie o backup novo para o Pi.
