import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer
import os
import subprocess

# Очередь для аудиопотока
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

# Путь к модели
model_path = "model/vosk-model-small-ru-0.22"
if not os.path.exists(model_path):
    print("Модель не найдена!")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Команды, которые ты можешь распознавать
commands = {
    "открой браузер": lambda: subprocess.Popen(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"]),
    "открой папку": lambda: subprocess.Popen("explorer.exe"),
    "завершить работу": lambda: os.system("shutdown /s /t 1")
}

# Аудиовход
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Говори что-нибудь (Ctrl+C для выхода)...")

    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result["text"]
            print("Распознано:", text)

            if text in commands:
                print(f"Выполняется команда: {text}")
                commands[text]()
