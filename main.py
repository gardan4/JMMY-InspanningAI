import mediapipe_demo
import install_deps

menu = {
    '0': "Exit Programma",
    '1': "Install Dependencies",
    '2': "Demo MediaPipe (Facemesh)",
    '3': "What's its gonna be..?",
    '4': "Find out next week!"
}


if __name__ == '__main__':
    flag = True
    print("\n" * 50)
    print("Welcome!")

    while flag:
        print("\nChoose an option down below:")
        for option in menu.keys():
            print(f"{option}. {menu[option]}")

        choice = str(input("\nType a number to select the option: "))

        if choice == "0":
            flag = False

        elif choice == "1":
            print("Running installer...")
            install_deps.unattended_install()

        elif choice == "2":
            mediapipe_demo.main_program()

        else:
            print(f"Option {choice} was either not found or not yet implemented!")