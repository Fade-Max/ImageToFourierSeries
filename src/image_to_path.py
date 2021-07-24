# For edge detection I use canny edge detection algorithm

from PIL import Image, ImageOps, ImageFilter
import numpy as np
import matplotlib.pyplot as plt

img = Image.open("gh.png")
img = ImageOps.grayscale(img)
img = np.array(img)


def generate_gaussian_kernel(kernel_size, sigma):
    ax = np.linspace(-(kernel_size - 1) / 2, (kernel_size - 1) / 2, kernel_size)
    x, y = np.meshgrid(ax, ax)
    kernel = np.exp(-0.5 * (np.square(x) + np.square(y)) / np.square(sigma))
    return kernel / np.sum(kernel)


def convolve(img, kernel):
    kernel_size = kernel.shape[0]
    pad_size = (kernel_size - 1) / 2
    gradient_map = np.zeros(img.shape)
    img = np.pad(img, int(pad_size), 'edge')

    for y in range(gradient_map.shape[0]):
        for x in range(gradient_map.shape[1]):
            gradient_map[y, x] = np.sum(img[y:y + kernel_size, x:x + kernel_size] * kernel)

    return gradient_map


def non_maximum_suppression(img, angles):
    w, h = img.shape
    new_img = np.zeros(img.shape)
    img = np.pad(img, 1, 'edge')

    for y in range(w):
        for x in range(h):
            angle = abs(angles[y, x])
            xx = 0
            yy = 0

            if (0 < angle < np.pi / 8) or (np.pi > angle > 7 * np.pi / 8):
                xx = -1
                yy = 0
            elif np.pi / 8 < angle < 3 * np.pi / 8:
                xx = -1
                yy = -1
            elif 3 * np.pi / 8 < angle < 5 * np.pi / 8:
                xx = 0
                yy = 1
            elif 5 * np.pi / 8 < angle < 7 * np.pi / 8:
                xx = 1
                yy = -1

            if img[y + 1 + yy, x + 1 + xx] > img[y + 1, x + 1] or img[y + 1 - yy, x + 1 - xx] > img[y + 1, x + 1]:
                new_img[y, x] = 0
            else:
                new_img[y, x] = img[y + 1, x + 1]

    return new_img

def double_threshold(img, high, low):
    high_threshold = img.max() * high
    low_threshold = high_threshold * low
    strong = np.int16(255)
    week = np.int16(30)

    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            val = img[y,x]
            if val >= high_threshold:
                img[y,x] = strong
            elif val < low_threshold:
                img[y,x] = 0
            else:
                img[y,x] = week

    return img

def hysteresis(img):
    img = np.pad(img, 1)
    week = np.int16 = 30
    strong = np.int16 = 255

    for y in range(1,img.shape[0]-1):
        for x in range(1,img.shape[1]-1):
            if img[y,x] == week:
                area = img[y-1:y+1, x-1:x+1]
                if area.max() == strong:
                    img[y,x] = strong
                else:
                    img[y,x] = 0

    return img[1:-1, 1:-1]

# Apply gaussian blur
kernel = generate_gaussian_kernel(5, 2)
img = convolve(img, kernel)

# Calculate gradients
x_kernel = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
])

y_kernel = np.array([
    [-1, -2, -1],
    [0, 0, 0],
    [1, 2, 1]
])

g_x = convolve(img, x_kernel)
g_y = convolve(img, y_kernel)

gradients = np.sqrt(np.square(g_x) + np.square(g_y))
gradients = gradients / gradients.max() * 255
# Get direction for every pixel
theta = np.arctan2(g_y, g_x)
# Apply non-maximum suppression
img = non_maximum_suppression(gradients, theta)
# Apply double thresholding
img = double_threshold(img, 0.09, 0.05)
# Apply edge tracking
img = hysteresis(img)
# Show edges
img = Image.fromarray(img)
img.show()
