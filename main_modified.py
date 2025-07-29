import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer
import os
import subprocess
import pygame
from pygame import mixer
import random
import psutil
import time
import pyautogui
import win32gui
import win32con
import webbrowser
from datetime import datetime
import wikipedia
import requests
from bs4 import BeautifulSoup
import pyjokes

# Инициализация pygame mixer
pygame.init()
mixer.init()
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def play_random_sound(sound_dir):
    try:
        sound_files = [f for f in os.listdir(sound_dir) if f.endswith('.mp3')]
        if sound_files:
            random_sound = random.choice(sound_files)
            sound_path = os.path.join(sound_dir, random_sound)
            mixer.music.load(sound_path)
            mixer.music.play()
            while mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Ошибка воспроизведения: {e}")

def close_browser_tabs():
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in ['chrome.exe', 'firefox.exe', 'msedge.exe']:
                proc.kill()
        return True
    except Exception as e:
        print(f"Ошибка закрытия браузера: {e}")
        return False

def get_weather(city="Москва"):
    try:
        url = f"http://wttr.in/{city}?format=%C+%t"
        response = requests.get(url)
        return f"Погода в {city}: {response.text}"
    except Exception as e:
        return f"Не удалось получить погоду: {e}"

def execute_command(command):
    try:
        if command in commands:
            print(f"Выполняю: {command}")
            result = commands[command]()
            play_random_sound("voice/perform")
            return result
        else:
            play_random_sound("voice/error")
            return "Команда не распознана"
    except Exception as e:
        play_random_sound("voice/error")
        print(f"Ошибка: {e}")
        return f"Ошибка выполнения: {e}"

# Основные команды
commands = {
    # Системные команды
    "выключи компьютер": lambda: os.system("shutdown /s /t 1"),
    "перезагрузить компьютер": lambda: os.system("shutdown /r /t 1"),
    "режим сна": lambda: os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0"),
    
    # Браузер
    "открой браузер": lambda: webbrowser.open("https://www.google.com"),
    "закрой браузер": lambda: close_browser_tabs(),
    "открой ютуб": lambda: webbrowser.open("https://youtube.com"),
   
    "открой вконтакте": lambda: webbrowser.open("https://vk.com"),
    "открой гитхаб": lambda: webbrowser.open("https://github.com"),


   
    "открой вконтакте": lambda: webbrowser.open("https://vk.com"),
    "открой гитхаб": lambda: webbrowser.open("https://github.com"),
    
    # Приложения
    "открой блокнот": lambda: subprocess.Popen("notepad.exe"),
    "закрой блокнот": lambda: os.system("taskkill /f /im notepad.exe"),
    "открой калькулятор": lambda: subprocess.Popen("calc.exe"),
    "открой проводник": lambda: subprocess.Popen("explorer.exe"),
    
    # Мультимедиа
    "сделай скриншот": lambda: pyautogui.screenshot().save(f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"),
    "громче": lambda: pyautogui.press('volumeup'),
    "тише": lambda: pyautogui.press('volumedown'),
    "выключи звук": lambda: pyautogui.press('volumemute'),
    
    # Разное
    "который час": lambda: f"Сейчас {datetime.now().strftime('%H:%M')}",
    "какой сегодня день": lambda: f"Сегодня {datetime.now().strftime('%d.%m.%Y')}",
    "расскажи анекдот": lambda: pyjokes.get_joke(language='ru'),
    "погода": lambda: get_weather(),
    
    # Для разработчиков
    "открой редактор": lambda: subprocess.Popen(["C:\\Users\\Ahmed\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"]),
     "включить обход": lambda: subprocess.Popen(["C:\\Users\\Ahmed\\Desktop\\zapret-discord-youtube-1.3.0"]),
}

# Инициализация модели Vosk
model_path = "model/vosk-model-small-ru-0.22"
if not os.path.exists(model_path):
    print("Модель не найдена!")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Основной цикл
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                      channels=1, callback=callback):
    print("Говорите команды... (Для выхода нажмите Ctrl+C)")
    
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            print(f"Распознано: {text}")
            
            if text:
                response = execute_command(text)
                if response:
                    print(response)