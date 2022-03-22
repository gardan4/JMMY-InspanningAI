import cv2
import mediapipe as mp
import numpy as np
import sys
import os
import time
import json_export as json


def startup(_video_path):
    # Initializing some starting variables
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing_styles = mp.solutions.drawing_styles

    # Error catching for video capture
    cap = cv2.VideoCapture(_video_path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        raise TypeError

    return mp_drawing, mp_face_mesh, mp_drawing_styles, cap


def output(_video_path, cap):
    # Gathering some info about the input-file
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(5))

    # Gets the file path and its name.
    outdir, inputflnm = _video_path[:_video_path.rfind(
        '/') + 1], _video_path[_video_path.rfind('/') + 1:]
    # Splits out the file-type designation
    inflnm, inflext = inputflnm.split('.')

    # Creating the appropriate folder for the data
    try:
        if not os.path.exists('generateData_OUTPUT'):
            os.makedirs('generateData_OUTPUT')

    # If we can't create the folder we raise an error.
    except OSError:
        print("Error: Can't create a folder here.")

    # Finally, we define the filename, file-type and we encode the file.
    out_filename = f'generateData_OUTPUT/{inflnm}_trainingsData.mp4'
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(out_filename, fourcc, fps, (frame_width, frame_height))
    return out


def program(cap, out, mp_face_mesh, mp_drawing, mp_drawing_styles, _video_path):
    # Used when drawing occurs, see OUTPUT MARKER
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    # Parameters fot face-mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    # Editing the capture, frame by frame.
    frame_counter = 0
    face_landmarks_dict = {}
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_mesh.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Here we generate the face-landmarks.
        '''OUTPUT MARKER'''
        frame_counter += 1
        if results.multi_face_landmarks:
            face_landmarks_dict[frame_counter] = {}
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

            # Get Size
            frame_height, frame_width, tmp = image.shape

            # Parameters for text
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 3.5
            fontColor = (255, 255, 255)
            thickness = 5
            lineType = 2
            text = str(frame_counter)

            # Text size and location (relative to img)
            standard_offset = 20
            text_size = cv2.getTextSize(text, font, fontScale, thickness)[0]
            textX = int((frame_width - text_size[0] - standard_offset) * 0.95)
            textY = int((frame_height + text_size[1]- standard_offset) * 0.95)
            text_coords = (int(textX), int(textY))

            # Put the text
            cv2.putText(image, text, text_coords, font, fontScale, fontColor, thickness, lineType)
        out.write(image)

        try:
            for i in results.multi_face_landmarks:
                for g in range(0, len(i.landmark)):
                    face_landmarks_dict[frame_counter][g] = []
                    face_landmarks_dict[frame_counter][g].append([i.landmark[g].x, i.landmark[g].y, i.landmark[g].z])
                    # face_landmarks_dict[frame_counter][g] = str(face_landmarks_dict[frame_counter][g][0])
        # TODO: Error catching cleanup
        except TypeError:
            pass

    # Cleanup!
    outdir, inputflnm = _video_path[:_video_path.rfind(
        '/') + 1], _video_path[_video_path.rfind('/') + 1:]
    # Splits out the file-type designation
    inflnm, inflext = inputflnm.split('.')

    out_filename = f'generateData_OUTPUT/{inflnm}_trainingsData.json'
    json.export_dump(face_landmarks_dict, out_filename)

    # Closing up shop
    face_mesh.close()
    cap.release()
    out.release()


def auto_run():
    print("\n"*3)
    vid = input("Provide the path to a video file\n"
                "Example: C:/Users/admin/video/video.mp4\n"
                "Path: ")
    mp_d, mp_mesh, mp_dstyle, c = startup(vid)
    output_file = output(vid, c)
    program(c, output_file, mp_mesh, mp_d, mp_dstyle, vid)


if __name__ == '__main__':
    auto_run()
