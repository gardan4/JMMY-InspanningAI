import cv2
import mediapipe as mp
import numpy as np
import sys
import os


def auto_run(_video_path):
    mp_d, mp_p, p, c = startup(video_path)
    o = output(video_path, c)
    program(p, c, o, mp_p, mp_d)


def startup(_video_path):
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing_styles = mp.solutions.drawing_styles

    # Error catching for videocap
    cap = cv2.VideoCapture(_video_path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        raise TypeError

    return mp_drawing, mp_face_mesh, mp_drawing_styles, cap


def output(_video_path, cap):
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    outdir, inputflnm = _video_path[:_video_path.rfind(
        '/')+1], _video_path[_video_path.rfind('/')+1:]

    inflnm, inflext = inputflnm.split('.')

    try:
        # creating a folder named data
        if not os.path.exists('generateData_OUTPUT'):
            os.makedirs('generateData_OUTPUT')

    # if not created then raise error
    except OSError:
        print("Error: Can't create a folder here.")

    out_filename = f'{outdir}generateData_OUTPUT/{inflnm}_annotated.{inflext}'
    out = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(
        'M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
    return out


def program(cap, out, mp_face_mesh, mp_drawing, mp_drawing_styles):
    # Used when drawing occurs, see OUTPUT MARKER
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    count = 0
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print(f"fail_{count}")
            count += 1
            break

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_mesh.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        '''OUTPUT MARKER'''
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
        out.write(image)

    cap.release()
    out.release()


if __name__ == '__main__':
    print("File: ")
    video_path = input()
    mediapipe_drawing, mediapipe_face_mesh, mediapipe_drawing_styles, capture = startup(video_path)
    output = output(video_path, capture)
    program(capture, output, mediapipe_face_mesh, mediapipe_drawing, mediapipe_drawing_styles)
