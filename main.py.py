import cv2
import numpy as np
import pickle
import threading
from helpers import roi
from lanefilter import LaneFilter
from birdseye import BirdsEye
from curves import Curves

calibration_data = pickle.load(open('calibration_data.p', 'rb'))
matrix = np.array(calibration_data['camera_matrix'])
dist_coef = np.array(calibration_data['distortion_coefficient'])

source_points = [(65, 475), (245, 355), (415, 355), (595, 475)]


dest_points = [
    (img_width - 100, img_height),  
    (img_width - 220, 0),  
    (img_width - 420, 0),  
    (img_width - 635, img_height)   
]

warp_matrix = cv2.getPerspectiveTransform(np.float32(source_points), np.float32(dest_points))
inv_warp_matrix = cv2.getPerspectiveTransform(np.float32(dest_points), np.float32(source_points))

p = {'sat_thresh': 80, 'light_thresh': 40, 'light_thresh_agr': 150,
     'grad_thresh': (0.7, 1.4), 'mag_thresh': 40, 'x_thresh': 20}

birdsEye = BirdsEye(source_points, dest_points, matrix, dist_coef)
laneFilter = LaneFilter(p)
curves = Curves(number_of_windows=9, margin=100, minimum_pixels=50,
                ym_per_pix=30 / 720, xm_per_pix=3.7 / 700)

curve_history = {'left': None, 'right': None}


def pipeline_debug(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        ground_img = birdsEye.undistort(img)
        ground_img_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        binary_img = laneFilter.apply(ground_img_rgb)

        if binary_img is None or np.count_nonzero(binary_img) == 0:
            print("Error: Empty binary image detected.")
            return None

        wb = np.logical_and(birdsEye.sky_view(binary_img), roi(binary_img)).astype(np.uint8)
        if np.count_nonzero(wb) == 0:
            print("Error: Empty working binary image detected.")
            return None

        result = curves.fit(wb)
        if result is None:
            print("Error: Curve fitting failed.")
            return None

        left_curve = result['pixel_left_best_fit_curve']
        right_curve = result['pixel_right_best_fit_curve']

        if curve_history['left'] is None or curve_history['right'] is None:
            curve_history['left'] = left_curve
            curve_history['right'] = right_curve
        else:
            curve_history['left'] = 0.9 * curve_history['left'] + 0.1 * left_curve
            curve_history['right'] = 0.9 * curve_history['right'] + 0.1 * right_curve

        projected_img = birdsEye.project(ground_img, binary_img,
                                         curve_history['left'],
                                         curve_history['right'])
        return projected_img
    except Exception as e:
        print(f"Error in pipeline_debug: {e}")
        return None


def process_frame(capture, callback, output_path):
  
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30 

    fourcc = cv2.VideoWriter_fourcc(*'XVID') 
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        try:
            result = callback(frame)
            if result is not None:
                out.write(result) 
                cv2.imshow('Lane Detection', result)
        except Exception as e:
            print(f"Error in process_frame: {e}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    out.release() 


if __name__ == '__main__':
    capture = cv2.VideoCapture('videos/drive.mp4')

    if not capture.isOpened():
        print("Error: Could not open video file.")
        exit()

    output_path = 'output_video.avi' 

    processing_thread = threading.Thread(target=process_frame, args=(capture, pipeline_debug, output_path))
    processing_thread.start()

    processing_thread.join()

    capture.release()
    cv2.destroyAllWindows()
