import subprocess
import sys
import os

def build():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    icons_dir = os.path.join(current_dir, "icons")
    data_dir = os.path.join(current_dir, "data")

    command = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--icon={os.path.join(icons_dir, 'Nexus.ico')}",
        f"--add-data={icons_dir};icons",
        f"--add-data={data_dir};data",
        "--name=Nexus",
        f"--distpath={os.path.join(current_dir, 'dist')}",
        f"--workpath={os.path.join(current_dir, 'build')}",
        f"--specpath={os.path.join(current_dir, 'build')}",
        "--hidden-import=aiortc",
        "--hidden-import=socketio",
        "--hidden-import=engineio",
        "--hidden-import=aiohttp",
        "--hidden-import=av",
        "--hidden-import=cryptography",
        "--hidden-import=OpenSSL",
        "--collect-all=aiortc",
        "--collect-all=av",
        os.path.join(current_dir, "interface.py")
    ]
    result = subprocess.run(command)
    print("Completed" if result.returncode == 0 else "Failed")
    return result.returncode

if __name__ == "__main__":
    sys.exit(build())
