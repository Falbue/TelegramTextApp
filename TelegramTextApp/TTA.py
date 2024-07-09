import sys
import os
import sqlite3
import shutil

def start():
    if len(sys.argv) != 2:
        print("Usage: TTA <NAME PROJECT>")
        sys.exit(1)

start()