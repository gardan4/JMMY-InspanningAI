from platform import processor
import cv2
import mediapipe as mp
import os
import json_export as json
import pandas as pd
import video_processor as vid_proc


class Generator:
    def __init__(self, vid_path):
        # Initiate the video processor
        self.processor = vid_proc.VideoProcessor(vid_path)

        # Initial setup for MP
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Parameters for text
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.text_color = (255, 255, 255)
        self.line_type = 2
        self.thickness = 2
        self.standard_text_offset = 15

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
        self.results = None
        self.image = None

        # Doing the same, but for the used vars
        self.time_stamp = None
        self.heart_rate = None
        self.wattage = None
        self.maxhr = None
        self.face_landmarks_dict = {}

        # Running functions for setup
        self.data_table = self.make_panda_table()
        
        # Creating the HR Zone column
        self.maxhr = max(self.data_table["idHeartrate"])
        self.data_table['heartRateZone'] = self.data_table.apply(
            lambda row: 5 if (row.idHeartrate > (self.maxhr * 0.9)) else (
                4 if (row.idHeartrate > (self.maxhr * 0.8)) else (
                    3 if (row.idHeartrate > (self.maxhr * 0.7)) else (
                        2 if (row.idHeartrate > (self.maxhr * 0.6)) else (
                            1 if (row.idHeartrate > (self.maxhr * 0.5)) else (0))))), axis=1)

    def make_panda_table(self):
        path = input("Provide the name to the CSV file\n"
                "Example: C:/Users/admin/document/220316_1120_ROEL.csv\n"
                "Path: ")
        return pd.read_csv(path, sep=";")

    def generate_data(self):
        # Editing the capture, frame by frame.
        frame_counter = 0
        self.processor.capture
        while self.processor.capture.isOpened():
            success, self.image = self.processor.capture.read()
            if not success:
                print("Finished.")
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
                # Printing framecount every "x" frames:
                if frame_counter%250 == 0:
                    print(f"Frame: {frame_counter}")

                self.get_data_for_frame(frame_counter)
                self.add_text(self.heart_rate, "TL")
                self.add_text(self.wattage, "BL")

                frame_id = f"Frame: {frame_counter} - TS: {self.time_stamp}"
                self.add_text(frame_id, "BR")

                # Write the IMG and save the facemesh coords
                self.processor.encoder.write(self.image)
                self.add_data_points(frame_counter)

        # Closing and cleaning up
        self.make_json_file()
        self.face_mesh.close()
        self.processor.cleanup()

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

    def get_text_coords(self, text_str, location):
        text_size = cv2.getTextSize(text_str, self.font, self.font_scale, self.thickness)[0]

        if location == "TL":  # Top Left
            text_x = int((self.processor.frame_width - text_size[0] - self.standard_text_offset) * 0.05)
            text_y = int((self.processor.frame_height + text_size[1] - self.standard_text_offset) * 0.15)

        elif location == "TR":  # Top Right
            text_x = int((self.processor.frame_width - text_size[0] - self.standard_text_offset) * 0.95)
            text_y = int((self.processor.frame_height + text_size[1] - self.standard_text_offset) * 0.15)

        elif location == "BL":  # Bottom Left 
            text_x = int((self.processor.frame_width - text_size[0] - self.standard_text_offset) * 0.05)
            text_y = int((self.processor.frame_height + text_size[1] - self.standard_text_offset) * 0.85)

        elif location == "BR":  # Bottom Right
            text_x = int((self.processor.frame_width - text_size[0] - self.standard_text_offset) * 0.95)
            text_y = int((self.processor.frame_height + text_size[1] - self.standard_text_offset) * 0.85)

        else:  # Bottom Right (as Default)
            print(f"Location '{location}' is not valid.\nResulting to default (BR).")
            text_x = int((self.processor.frame_width - text_size[0] - self.standard_text_offset) * 0.95)
            text_y = int((self.processor.frame_height + text_size[1] - self.standard_text_offset) * 0.85)

        return (int(text_x), int(text_y))

    def add_text(self, text, location):
        text_str = str(text)
        text_coords = self.get_text_coords(text_str, location)
        # Put the text
        cv2.putText(self.image, text_str, text_coords, self.font,
                    self.font_scale, self.text_color, self.thickness,
                    self.line_type)

    def get_data_for_frame(self, frame_counter):
        current_time = self.processor.data_interval * frame_counter

        row_count = 0
        while current_time > 0:
            current_time -= 500
            row_count += 1
        try:
            self.time_stamp = self.data_table["idTime"][row_count]
            self.heart_rate = self.data_table["idHeartrate"][row_count]
            self.wattage = self.data_table["idPower"][row_count]
            self.hrz = self.data_table["heartRateZone"][row_count]

        except Exception as e:
            print(f"An error {e} was raised.")

    def add_data_points(self, frame_counter):
        self.face_landmarks_dict[frame_counter] = {}
        self.face_landmarks_dict[frame_counter]["TS"] = str(self.time_stamp)
        self.face_landmarks_dict[frame_counter]["HR"] = str(self.heart_rate)
        self.face_landmarks_dict[frame_counter]["PWR"] = str(self.wattage)
        self.face_landmarks_dict[frame_counter]["heartRateZone"] = str(self.hrz)

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
        out_filename = f"generateData_OUTPUT/{self.processor.file_name}_trainingsData.json"
        json.export_dump(self.face_landmarks_dict, out_filename)


def get_user_path():
    print("\n" * 3)
    vid = input("Provide the path to a video file\n"
                "Example: C:/Users/admin/video/video.mp4\n"
                "Path: ")
    return vid


def auto_run():
    vid = get_user_path()
    gen = Generator(vid)
    gen.generate_data()


if __name__ == '__main__':
    auto_run()
