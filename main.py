import mediapipe_demo
import vid_to_img
import install_deps
import generate_data_from_video

menu = {
    '0': "Exit program",
    '1': "Install Dependencies",
    '2': "Demo MediaPipe (Facemesh)",
    '3': "Convert a video to images",
    '4': "Apply facemesh to video!"
}


def main_menu(option_dic):
    print("\nChoose an option down below:")
    for option in option_dic.keys():
        print(f"{option}. {option_dic[option]}")

    choice = str(input("\nType a number to select the option: "))

    if choice == "0":
        return False

    elif choice == "1":
        print("Running installer...")
        install_deps.unattended_install()
        return True

    elif choice == "2":
        try:
            mediapipe_demo.menu()
        except TypeError:
            print(f"Mediapipe has crashed. Your face was not detected. ")
        return True

    elif choice == "3":
        vid_to_img.vid_to_img()
        return True

    elif choice == "4":
        generate_data_from_video.run()
        return True

    else:
        print(f"Option {choice} was either not found or not yet implemented!")
        return True


if __name__ == '__main__':
    flag = True
    print("\n" * 50)
    print("Welcome!")

    while flag:
        flag = main_menu(menu)
