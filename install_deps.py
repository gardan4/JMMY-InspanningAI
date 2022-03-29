import subprocess
import sys


package_list = [
    "mediapipe",
    "pandas",
    "moviepy",
    "sklearn",
    "tensorflow",
    "keras",
    "opencv-python"
    ]


def update_pip():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def unattended_install():
    update_pip()
    for p in package_list:
        print(f"Installing: {p}")
        try:
            install(p)
        except Exception as e:
            print("Something went wrong installing: \n", p)
            print("Errorcode: \n", e)
    print("Installed dependencies!")


def auto_install(_package_list):
    update_pip()
    for p in package_list:
        print(f"Installing: {p}")
        try:
            install(p)
        except Exception as e:
            print("Something went wrong installing: \n", p)
            print("Errorcode: \n", e)
    print("Installed dependencies!")


if __name__ == '__main__':
    auto_install(package_list)
