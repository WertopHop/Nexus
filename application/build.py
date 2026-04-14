import subprocess
import sys
import os

def build():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    command = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        "--windows-console-mode=disable",
        "--windows-icon-from-ico=icons/Nexus.ico",
        "--include-data-dir=icons=icons",
        "--include-data-dir=data=data",
        "--output-filename=Nexus.exe",
        "--output-dir=dist",
        "--assume-yes-for-downloads",
        "--disable-ccache",
        "--include-package=aiortc",
        "--include-package=socketio",
        "--include-package=engineio",
        "--include-package=aiohttp",
        "--include-package=av",
        "--include-package=cryptography",
        "--include-package=OpenSSL",
        "--include-package=asyncio",
        "interface.py"
    ]
    result = subprocess.run(command)
    print("1" if result.returncode == 0 else "0")
    return result.returncode

if __name__ == "__main__":
    sys.exit(build())