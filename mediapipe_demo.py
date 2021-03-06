import os
import cv2
import mediapipe as mp
import json_export as jsonexporter


def menu():
    # Initialize variables for the code:
    drawing = mp.solutions.drawing_utils
    drawing_styles = mp.solutions.drawing_styles
    face_mesh = mp.solutions.face_mesh
    flag = True

    # Menu
    while flag:
        print("\n----------\n"
              "Which would you like to mesh?\n"
              "1. Static Images\n"
              "2. A live Webcam Feed\n"
              "3. A video (converts the video to images,"
              "then processes the images and deletes them after)"
              )
        option = input("Choose: ")

        try:
            option = int(option)
        except ValueError:
            print(f"{option} is not a number!")

        # Static Images
        if option == 1:
            flag = False
            print("Format: C:/Path/To/Img.png/ with commas in between files. \n"
                  "\nExample: ':/Users/admin/etc/img.png/,C:/Users/admin/etc/img2.png/,C:/Users/admin/etc/img3.png/"
                  "\nProvide the IMG files: ")

            usr_input = str(input())
            img_list = usr_input.split(",")
            option = input("Would you like to print the coordinates? (0/1)")

            try:
                option = int(option)
                if option < 0 or option > 1:
                    print(f"{option} is not a valid number!\n"
                          f"Choosing default...")
                    static_images(0, drawing, drawing_styles, face_mesh)
                    break
                static_images(option, img_list, drawing, drawing_styles, face_mesh)
            except ValueError:
                print(f"{option} is not a valid number!\n"
                      f"Choosing default...")
                static_images(0, drawing, drawing_styles, face_mesh)

        # Live Webcam Feed
        elif option == 2:
            print("Press Escape button to exit!")
            option = input("Would you like to print the coordinates? \n"
                           "(No: 0 / Yes: 1)\n"
                           "Default: No (0)")

            try:
                option = int(option)
                if option < 0 or option > 1:
                    print(f"{option} is not a valid number!\n"
                          f"Choosing default...")
                    webcam_mesh(0, drawing, drawing_styles, face_mesh)
                    break
                webcam_mesh(option, drawing, drawing_styles, face_mesh)

            except ValueError:
                print(f"{option} is not a number!\n"
                      f"Choosing default...")
                webcam_mesh(0, drawing, drawing_styles, face_mesh)

            except UnicodeDecodeError:
                print(f"UnicodeDecodeError, the code closed with an internal (known) error.")

        else:
            print(f"Option {option} was not found!\n")


def get_coords_list(_option, _results):
    '''
    Toevoeging van de projectgroep,
    hiermee proberen we de punten van gezichten op te slaan
    zodat deze herkend kunnen worden.
    '''
    try:
        coords_list = []
        for i in _results.multi_face_landmarks:
            for g in range(0, len(i.landmark)):
                coords_list.append([i.landmark[g].x, i.landmark[g].y, i.landmark[g].z])
            if _option == 1:
                jsonexporter.export(coords_list)
            else:
                pass
    # TODO: Error catching cleanup
    except:
        pass


# For static images:
def static_images(option, _img_list, mp_drawing, mp_drawing_styles, mp_face_mesh):
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    # Creates the folder for the output
    try:
        # creating a folder named data
        if not os.path.exists('staticImg_OUTPUT'):
            os.makedirs('staticImg_OUTPUT')

    except OSError:
        print("Error: Can't create a folder here.")

    with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5) as face_mesh:

        for count, file in enumerate(_img_list):
            image = cv2.imread(file)
            # Convert the BGR image to RGB before processing.
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # Print and draw face mesh landmarks on the image.
            if not results.multi_face_landmarks:
                continue
            annotated_image = image.copy()

            for face_landmarks in results.multi_face_landmarks:

                '''Checkt of de landmarks geprint moeten worden naar console!'''
                if option == 1:
                    print('face_landmarks:', face_landmarks)

                else:
                    mp_drawing.draw_landmarks(
                        image=annotated_image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                            .get_default_face_mesh_tesselation_style())
                    mp_drawing.draw_landmarks(
                        image=annotated_image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                            .get_default_face_mesh_contours_style())
                    mp_drawing.draw_landmarks(
                        image=annotated_image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                            .get_default_face_mesh_iris_connections_style())

                name = './staticImg_OUTPUT/testImage' + str(count) + '.png'
                print('Creating...' + name)
                cv2.imwrite(name, annotated_image)


# For webcam input
def webcam_mesh(option, mp_drawing, mp_drawing_styles, mp_face_mesh):
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    cap = cv2.VideoCapture(0)

    with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as face_mesh:

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image)

            '''Toevoeging casusgroep:'''
            get_coords_list(option, results)

            # Draw the face mesh annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                            .get_default_face_mesh_tesselation_style())
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_FACE_OVAL,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                            .get_default_face_mesh_contours_style())
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                            .get_default_face_mesh_iris_connections_style())
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()


if __name__ == '__main__':
    menu()
