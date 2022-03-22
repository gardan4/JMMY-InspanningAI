import cv2
import mediapipe as mp
import numpy as np
import sys
import os
import time
import json_export as json


class Generator:
    def __init__(self, vid_path):
        # Initial setup for MP
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Parameters for text
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 3.5
        self.text_color = (255, 255, 255)
        self.line_type = 2
        self.thickness = 5
        self.standard_text_offset = 20

        # Parameters for face meshing and drawing lines
        self.drawing_spec = self.mp_drawing.DrawingSpec(
            thickness=1,
            circle_radius=1
        )

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Setting up vars to filled later
        self.frame_height = None
        self.frame_width = None
        self.results = None
        self.image = None

        # Initial setup for program
        self.vid_path = vid_path
        self.face_landmarks_dict = {}

        # Running functions for setup
        self.file_name = self.get_file_name()
        self.capture = self.open_capture()
        self.encoder = self.make_encoder()

    def get_file_name(self):
        file_name = self.vid_path[self.vid_path.rfind('/') + 1:]
        # Splits out the file-type designation
        file_name, file_extension = file_name.split('.')
        return file_name

    def open_capture(self):
        cap = cv2.VideoCapture(self.vid_path)
        if not cap.isOpened():
            print("Error opening video stream or file")
            raise TypeError
        return cap

    def make_encoder(self):
        # Gathering some info about the input-file
        self.frame_width = int(self.capture.get(3))
        self.frame_height = int(self.capture.get(4))
        fps = int(self.capture.get(5))

        # Check and make sure the output folder exists.
        try:
            if not os.path.exists('generateData_OUTPUT'):
                os.makedirs('generateData_OUTPUT')

        # If we can't create the folder we raise an error.
        except OSError:
            print("Error: Can't create a folder here.")

        # Set the encoding type and filename (with the folder)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        out_filename = f'generateData_OUTPUT/{self.file_name}_trainingsData.mp4'

        # Make the video encoder:
        encoder = cv2.VideoWriter(out_filename, fourcc, fps, (self.frame_width, self.frame_height))
        return encoder

    def generate_data(self):
        # Editing the capture, frame by frame.
        frame_counter = 0
        while self.capture.isOpened():
            success, self.image = self.capture.read()
            if not success:
                print("Finished. ")
                break

            # Flipping just in case it's a webcam feed
            self.image = cv2.cvtColor(cv2.flip(self.image, 1), cv2.COLOR_BGR2RGB)
            self.image.flags.writeable = False

            # Apply face-mesh to the image
            self.results = self.face_mesh.process(self.image)

            # Prep the image so we can draw on it
            self.image.flags.writeable = True
            self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

            # Here we generate the face-landmarks.
            frame_counter += 1

            # IF the list with landmarks exists, we draw our information on it
            if self.results.multi_face_landmarks:
                self.draw()
                self.add_text(frame_counter)
                self.encoder.write(self.image)
                self.add_data_points(frame_counter)

        # Closing and cleaning up
        self.make_json_file()
        self.face_mesh.close()
        self.capture.release()
        self.encoder.release()

    def draw(self):
        for face_landmarks in self.results.multi_face_landmarks:
            # Making the grey grid
            self.mp_drawing.draw_landmarks(
                image=self.image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_tesselation_style())

            # Making the ring around the face
            self.mp_drawing.draw_landmarks(
                image=self.image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_FACE_OVAL,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_contours_style())

            # Making the irises
            self.mp_drawing.draw_landmarks(
                image=self.image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_iris_connections_style())

    def add_text(self, text):
        text_str = str(text)
        text_size = cv2.getTextSize(text_str, self.font, self.font_scale, self.thickness)[0]
        text_x = int((self.frame_width - text_size[0] - self.standard_text_offset) * 0.95)
        text_y = int((self.frame_height + text_size[1] - self.standard_text_offset) * 0.85)
        text_coords = (int(text_x), int(text_y))

        # Put the text
        cv2.putText(self.image, text_str, text_coords, self.font,
                    self.font_scale, self.text_color, self.thickness,
                    self.line_type)

    def add_data_points(self, frame_counter):
        self.face_landmarks_dict[frame_counter] = {}
        try:
            for i in self.results.multi_face_landmarks:
                for g in range(0, len(i.landmark)):
                    self.face_landmarks_dict[frame_counter][g] = []
                    self.face_landmarks_dict[frame_counter][g].append(
                        [i.landmark[g].x, i.landmark[g].y, i.landmark[g].z])
                    # face_landmarks_dict[frame_counter][g] = str(face_landmarks_dict[frame_counter][g][0])
        # TODO: Error catching cleanup
        except TypeError:
            pass

    def make_json_file(self):
        out_filename = f'generateData_OUTPUT/{self.file_name}_trainingsData.json'
        json.export_dump(self.face_landmarks_dict, out_filename)


def auto_run():
    print("\n"*3)
    vid = input("Provide the path to a video file\n"
                "Example: C:/Users/admin/video/video.mp4\n"
                "Path: ")
    gen = Generator(vid)
    gen.generate_data()


if __name__ == '__main__':
    auto_run()
