
import numpy as np
import pandas as pd
import cv2 as cv 

def gammaCorrection(src, gamma):
    invGamma = 1 / gamma

    table = [((i / 255) ** invGamma) * 255 for i in range(256)]
    table = np.array(table, np.uint8)

    return cv.LUT(src, table)


def sharppen(src):
    # kernel = np.array([[0, -1, 0],
                #    [-1, 5,-1],
                #    [0, -1, 0]])
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    return cv.filter2D(src=src, ddepth=-1, kernel=kernel)

