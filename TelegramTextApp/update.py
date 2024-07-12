import sys
import os
import shutil

def update():
    if len(sys.argv) != 2:
        print("Usage: TTA-update <NAME>")
        sys.exit(1)
    
    NAME = sys.argv[1]
    NAME_dir = f'Falbue/TelegramTextApp/{NAME}'

    print(f"{NAME} обновлён")

    source = f'{script_dir}/bot.py'
    destination = f'{NAME_dir}'
    shutil.copy(source, destination)