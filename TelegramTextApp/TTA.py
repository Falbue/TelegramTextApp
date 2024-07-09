import sys
import os
import sqlite3
import shutil

def start():
    if len(sys.argv) != 2:
        print("Usage: TTA <NAME-PROJECT> or TTA ALL")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f'{script_dir}/TTA_dir.txt', 'r') as file:
        tta_path = file.readline().strip()
    NAME = sys.argv[1]

    if sys.argv[2] == "ALL": 
        for entry in os.listdir(tta_path):
            if os.path.isdir(os.path.join(tta_path, entry)):
                os.system(f'python {tta_path}/{entry}/bot.py')
    else:
        os.system(f'python {tta_path}/{NAME}/bot.py')