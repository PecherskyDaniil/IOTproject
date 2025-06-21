import asyncio
import subprocess
import threading
import webbrowser
from TelegramBot.Bot import start_bot
from API.main import start_server
import DB
import API
import time
from pathlib import Path
# Конфигурация
BASE_DIR = Path(__file__).parent.resolve()
REACT_PATH = BASE_DIR / "UI"/"iot-dashboard"  # Относительный путь к React-проекту
REACT_PORT = 3000

def run_react():
    try:
        react_process = subprocess.Popen(
            ["npm", "start"],
            cwd=str(REACT_PATH),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Для чтения текстового вывода
        )
        
        # Выводим логи в реальном времени
        def log_stream(stream, prefix):
            for line in stream:
                print(f"{prefix}: {line}", end='')
        
        threading.Thread(target=log_stream, args=(react_process.stdout, "REACT OUT"), daemon=True).start()
        threading.Thread(target=log_stream, args=(react_process.stderr, "REACT ERR"), daemon=True).start()
        
        time.sleep(10)  # Увеличиваем время ожидания
        return react_process
    except Exception as e:
        print(f"React launch error: {str(e)}")
        return None

async def main():
    # Запускаем React в отдельном потоке
    react_thread = threading.Thread(target=run_react)
    react_thread.daemon = True
    react_thread.start()
    
    # Запускаем бота и API
    await asyncio.gather(start_bot(), start_server())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПриложение остановлено")