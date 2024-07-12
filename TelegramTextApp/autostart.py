import os
import sys

def autostart():
    if len(sys.argv) != 2:
        print("Usage: TTA-autostart <NAME-PROJECT>")
        sys.exit(1)

    name = sys.argv[1]

    startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

    bat_file_path = os.path.join(startup_dir, f"TTA-{name}.bat")
    
    with open(bat_file_path, 'w') as bat_file:
        bat_file.write(f"TTA {name}\n")
    
    print(f"Приложение {name} добавлено в автозапуск")