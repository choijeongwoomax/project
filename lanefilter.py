import cv2
import numpy as np
from helpers import roi, scale_abs


class LaneFilter:
    def __init__(self, p):
        self.sat_thresh = p['sat_thresh']
        self.light_thresh = p['light_thresh']
        self.light_thresh_agr = p['light_thresh_agr']
        self.grad_min, self.grad_max = p['grad_thresh']
        self.mag_thresh, self.x_thresh = p['mag_thresh'], p['x_thresh']
        self.hls, self.l, self.s = None, None, None
        self.z = None  # Initialization of the mask

    def apply(self, rgb_image):
        """Preprocesses the image and applies both color and sobel masks."""
        self.hls = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HLS)
        self.l = self.hls[:, :, 1]
        self.s = self.hls[:, :, 2]
        self.z = np.zeros_like(self.s)

        # Apply color and sobel masks in parallel
        color_img = self.apply_color_mask()
        sobel_img = self.apply_sobel_mask()
        return cv2.bitwise_or(sobel_img, color_img)

    def apply_color_mask(self):
        """Applies color thresholding to the L and S channels."""
        color_cond1 = (self.s > self.sat_thresh) & (self.l > self.light_thresh)
        color_cond2 = self.l > self.light_thresh_agr
        mask = (color_cond1 | color_cond2).astype(np.uint8)
        return mask

    def apply_sobel_mask(self):
        """Applies sobel gradient thresholding to the L channel."""
        lx = cv2.Sobel(self.l, cv2.CV_64F, 1, 0, ksize=5)
        ly = cv2.Sobel(self.l, cv2.CV_64F, 0, 1, ksize=5)
        grad = np.arctan2(np.absolute(ly), np.absolute(lx))
        magnitude = np.sqrt(lx ** 2 + ly ** 2)

        # Normalize and scale absolute values
        scaled_magnitude = scale_abs(magnitude)
        scaled_lx = scale_abs(lx)
        scaled_ly = scale_abs(ly)

        # Apply sobel conditions
        sobel_cond1 = scaled_magnitude > self.mag_thresh
        sobel_cond2 = scaled_lx > self.x_thresh
        sobel_cond3 = (grad > self.grad_min) & (grad < self.grad_max)

        mask = (sobel_cond1 & sobel_cond2 & sobel_cond3).astype(np.uint8)
        return mask

    def sobel_breakdown(self, img):
        """Returns an image breakdown with sobel masks applied."""
        filtered_img = self.apply(img)
        sobel_img = self.apply_sobel_mask()
        color_img = self.apply_color_mask()
        return np.dstack((color_img, sobel_img, filtered_img))

    def color_breakdown(self, img):
        """Returns an image breakdown with color masks applied."""
        filtered_img = self.apply(img)
        color_img = self.apply_color_mask()
        return np.dstack((color_img, color_img, filtered_img))


