import cv2
import os


def vid_to_img():
    # Read the video from specified path
    vidpath = input("URL to Video: ")
    cam = cv2.VideoCapture(vidpath)

    try:
        # creating a folder named data
        if not os.path.exists('vidtoIMG_OUTPUT'):
            os.makedirs('vidtoIMG_OUTPUT')

    # if not created then raise error
    except OSError:
        print("Error: Can't create a folder here.")

    # frame
    currentframe = 0

    while True:
        # reading from frame
        ret, frame = cam.read()

        if ret:
            # if video is still left continue creating images
            name = './vidtoIMG_OUTPUT/frame' + str(currentframe) + '.jpg'
            print('Creating...' + name)

            # writing the extracted images
            cv2.imwrite(name, frame)

            # increasing counter so that it will
            # show how many frames are created
            currentframe += 1
        else:
            break

    # Release all space and windows once done
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    vid_to_img()
