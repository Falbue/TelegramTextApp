import os
import sys

def autostart():
    if len(sys.argv) != 2:
        print("Usage: TTA-autostart <NAME-PROJECT>")
        sys.exit(1)

    name = sys.argv[1]

    startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

    bat_file_path = os.path.join(startup_dir, f"TTA-{name}.cmd")
    
    with open(bat_file_path, 'w') as bat_file:
        command = f"powershell -windowstyle hidden -command \"Start-Process 'cmd.exe' -ArgumentList '/c @echo off & cd /d %HOMEDRIVE%%HOMEPATH% & TTA {name} & pause' -NoNewWindow\""
        bat_file.write(command)

    
    print(f"Приложение {name} добавлено в автозапуск")