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
    mp_pose = mp.solutions.pose

    # Setting parameters for detection
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # Error catching for videocap
    cap = cv2.VideoCapture(_video_path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        raise TypeError

    return mp_drawing, mp_pose, pose, cap


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


def program(pose, cap, out, mp_pose, mp_drawing):
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        out.write(image)

    pose.close()
    cap.release()
    out.release()


if __name__ == '__main__':
    print("File: ")
    video_path = input()
    mediapipe_drawing, mediapipe_pose, posevar, capture = startup(video_path)
    output = output(video_path, capture)
    program(posevar, capture, output, mediapipe_pose, mediapipe_drawing)


