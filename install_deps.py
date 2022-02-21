import subprocess
import sys


package_list = [
    "mediapipe",
    "opencv-python"
    ]


def update_pip():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def auto_install(_package_list):
    update_pip()
    for p in _package_list:
        try:
            install(p)
        except:
            print("Something went wrong installing: ", p)


if __name__ == '__main__':
    auto_install(package_list)
    print("Installed dependencies!")


else:
    auto_install(package_list)
    print("Installed dependencies!")