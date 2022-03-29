import cv2
import os
import moviepy.editor as mpe

class VideoProcessor():
    def __init__(self, vid_path):
        self.frame_height = None
        self.frame_width = None
        self.fps = None
        self.data_interval = None

        self.vid_path = vid_path

        print("---========---\n"
              "Intiated the Video Processor!\n"
              "---========---\n")

        self.file_name = self.get_file_name()
        self.capture = self.open_capture()
        self.encoder = self.make_encoder()
    
    def get_file_name(self):
        file_name = self.vid_path[self.vid_path.rfind('/') + 1:]
        # Splits out the file-type designation
        file_name, file_extension = file_name.split('.')
        return file_name

    def open_capture(self):
        self.resize_video()
        cap = cv2.VideoCapture(self.vid_path)
        if not cap.isOpened():
            print("Error opening video stream or file")
            raise TypeError
        return cap

    def make_encoder(self):
        # Gathering some info about the input-file
        self.frame_width = int(self.capture.get(3))
        self.frame_height = int(self.capture.get(4))
        self.fps = int(self.capture.get(5))
        self.data_interval = int(1000 / self.fps)

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
        encoder = cv2.VideoWriter(out_filename, fourcc, self.fps, (self.frame_width, self.frame_height))
        return encoder

    def resize_video(self):
        # The video is resized to reduce processing time. 
        print("")
        clip = mpe.VideoFileClip(self.vid_path)
        if clip.h > 360:
            print(f"Downsampling required.\n"
                  f"Current resolution: {clip.h}")
            # The height is set to 360P 
            # (According to moviePy documenation, the width is then computed so that 
            # the width/height ratio is conserved.)
            # TODO: Dismiss audio
            clip_resized = clip.resize(height=360)
            new_vid_path = self.vid_path[:self.vid_path.rfind('/')]
            new_vid_path = new_vid_path + "/" + self.file_name + "_360P.mp4"
            print(f"The new videofile will be saved to: \n"
                  f"{new_vid_path}")
            clip_resized.write_videofile(new_vid_path)
            self.vid_path = new_vid_path
        else:
            print(f"Downsampling is not required.\n"
                  f"Current resolution: {clip.h}")

    def cleanup(self):
        self.capture.release()
        self.encoder.release()
