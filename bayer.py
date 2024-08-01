import cv2 as cv
import numpy as np

def create_mosaic(width, height):
    # G(1) B(0) (repeat)
    # R(2) G(1) (repeat)
    mosaic = []
    for y in range(height):
        row = []
        pattern = [1, 0] if y % 2 == 0 else [2, 1]
        for x in range(width):
            row.append(pattern[x % 2])
        mosaic.append(row)
    return mosaic

def bayer_filter(img):
    height, width, _ = img.shape
    mosaic = create_mosaic(width, height)
    grayscale = np.zeros((height, width), dtype=float)
    color_code = np.zeros((height, width, 3), dtype=float)
    for y in range(height):
        for x in range(width):
                grayscale[y][x] = img[y][x][mosaic[y][x]]/255.
                for i in range(3):
                    color_code[y][x][i] = grayscale[y][x] if i == mosaic[y][x] else 0.
    return grayscale, color_code

def get_channels(img):
    red_channel = np.zeros_like(img)
    green_channel = np.zeros_like(img)
    blue_channel = np.zeros_like(img)
    red_channel [:,:,2] = img[:,:,2]
    green_channel [:,:,1] = img[:,:,1]
    blue_channel [:,:,0] = img[:,:,0]
    return red_channel, green_channel, blue_channel

# For averaging blue and or red pixels, from a red or blue pixel
def neighbor4_perp(img, x, y, channel):
    return (img[y-1][x][channel]+img[y+1][x][channel]+img[y][x-1][channel]+img[y][x+1][channel])/4

# For averaging green pixels, from a red or blue pixel
def neighbor4_diag(img, x, y, channel):
    return (img[y-1][x-1][channel]+img[y+1][x+1][channel]+img[y-1][x+1][channel]+img[y+1][x-1][channel])/4

# For averaging 2 vertical neighboring pixels, from a green pixel
def neighbor2_vert(img, x, y, channel):
    return (img[y-1][x][channel]+img[y+1][x][channel])/2

# For averaging 2 horizontal neighboring pixels, from a green pixel
def neighbor2_horz(img, x, y, channel):
    return (img[y][x-1][channel]+img[y][x+1][channel])/2

# Implemented using bilinear interpolation
def demosaic(img):
    height, width, _ = img.shape
    mosaic = create_mosaic(width, height)
    demosaic_img = np.zeros((height, width, 3), dtype=float)

    for y in range(1, height-1):
        for x in range(1, width-1):
            if mosaic[y][x] == 0: # At blue pixel. Need red and green pixels.
                demosaic_img[y][x][0] = img[y][x][0]
                demosaic_img[y][x][1] = neighbor4_perp(img, x, y, 1)
                demosaic_img[y][x][2] = neighbor4_diag(img, x, y, 2)
            elif mosaic[y][x] == 1: # At green pixel. Need blue and red pixels.
                demosaic_img[y][x][1] = img[y][x][1]
                if y % 2 == 0:
                    demosaic_img[y][x][0] = neighbor2_horz(img, x, y, 0)
                    demosaic_img[y][x][2] = neighbor2_vert(img, x, y, 2)
                else:
                    demosaic_img[y][x][0] = neighbor2_vert(img, x, y, 0)
                    demosaic_img[y][x][2] = neighbor2_horz(img, x, y, 2)
            elif mosaic[y][x] == 2: # At red pixel. Need blue and green pixels.
                demosaic_img[y][x][2] = img[y][x][2]
                demosaic_img[y][x][0] = neighbor4_diag(img, x, y, 0)
                demosaic_img[y][x][1] = neighbor4_perp(img, x, y, 1)
    return demosaic_img

scan_dir = "scans"
scan_name = "scan.png"
scan_path = scan_dir + '/' + scan_name
img = cv.imread(scan_path)

images_dir = "images"
cv.imshow("Original " + str(img.shape), img)
cv.imwrite(images_dir+"/original.png", img)
k = cv.waitKey(0)

greyscale, color_coded = bayer_filter(img)

cv.imshow("Bayer Filter " + str(greyscale.shape), greyscale)
cv.imwrite(images_dir+"/greyscale.png", 255*greyscale)
k = cv.waitKey(0)

cv.imshow("Bayer Filter color-coded " + str(color_coded.shape), color_coded)
cv.imwrite(images_dir+"/color-coded.png", 255*color_coded)
k = cv.waitKey(0)

red_channel, green_channel, blue_channel = get_channels(color_coded)
cv.imshow("Bayer Filter Red Channel", red_channel)
k = cv.waitKey(0)
cv.imshow("Bayer Filter Green Channel", green_channel)
k = cv.waitKey(0)
cv.imshow("Bayer Filter Blue Channel", blue_channel)
k = cv.waitKey(0)

cv.imwrite(images_dir+"/red.png", 255*red_channel)
cv.imwrite(images_dir+"/green.png", 255*green_channel)
cv.imwrite(images_dir+"/blue.png", 255*blue_channel)

demosaic_img = demosaic(color_coded)
cv.imshow("Reconstructed", demosaic_img)
k = cv.waitKey(0)

cv.imwrite(images_dir+"/demosaic_img.png", 255*demosaic_img)