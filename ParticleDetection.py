import cv2 as cv
import numpy as np
import os
import json

global paras

COLOR_ROI = (255,255,0)
COLOR_SCALE = (0,0,255)


def imageBinary(img:np.ndarray, k_median:int = 5, k_gaussian:int = 11, k_closing:int = 7, s_gaussian:int = 8):
    '''
    image_binary-> image_binary. 
    @kernals must be odd.
    '''
    img_median = cv.medianBlur(img, k_median)
    img_gaussian = cv.GaussianBlur(img_median,(k_gaussian, k_gaussian),s_gaussian)
    ret, img_binary = cv.threshold(img_gaussian, 120, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    kernal = cv.getStructuringElement(cv.MORPH_ELLIPSE, (k_closing,k_closing))  # kernal for morphological closing
    img_binary = cv.morphologyEx(img_binary, cv.MORPH_CLOSE, kernal, iterations=2)  # morphological closing
    cv.imwrite(os.path.join(OUTPUT_PATH, "debug.jpg"), img_binary)
    return img_binary

def findContours(img:np.ndarray, distT_thres=0.5):
    '''
    findContours -> contours.
    @img should be binary image.
    find contours using watershed.
    '''
    # use distance transform to determine the sure fontgrounds (particles)
    img_distT = cv.distanceTransform(img, cv.DIST_L2, 5)
    ret, fontground = cv.threshold(img_distT, img_distT.max()*distT_thres, 255, cv.THRESH_BINARY)
    fontground = np.uint8(fontground)
    cv.imwrite(os.path.join(OUTPUT_PATH, "debug2.jpg"), fontground)

    # use morphological dilate to determine the sure background (non-particles)
    kernal = cv.getStructuringElement(cv.MORPH_ELLIPSE, (7,7))
    background = cv.dilate(img, kernal, iterations=4)

    # the difference between the fontground and background is the unknown areas
    unknown = background - fontground

    # using numbers (>= 1) to mark the sure fontground and backgroud
    ret, markers = cv.connectedComponents(fontground)
    markers = markers + 1
    markers[unknown == 255] = 0  # mark the unknown areas as 0

    # separate the unknown areas and mark the boundaries as -1
    markers = cv.watershed(cv.cvtColor(img,cv.COLOR_GRAY2BGR), markers)
    edge = np.zeros(img.shape, np.uint8)
    edge[markers == -1] = 255

    # find contours
    contours, hierarchy = cv.findContours(edge,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    return contours

def drawCircularContours(img:np.ndarray, contours, sigma=1.4):
    '''
    using circle model to fit counters and draw circles on img.
    Export result as csv file.
    '''
    global scale, OUTPUT_PATH  
    cv.drawContours(img, contours, -1, (0,255,0))
    y=img.shape[0]
    x=img.shape[1]
    areas = np.array([cv.contourArea(contour) for contour in contours], np.int32)
    area_median = np.median(areas)  # calculate the median to exclude noise
    est_radius = 0.5 * np.sqrt(4*area_median/np.pi)
    count = 0
    files = open(os.path.join(OUTPUT_PATH,"result.csv"), "w", encoding='utf-8')

    for i,contour in enumerate(contours):
        M = cv.moments(contour)
        cx = int(M['m10']/M['m00'])  # centry coordinary x
        cy = int(M['m01']/M['m00'])  # centry coordinary y
        area = int(M['m00'])  # contour area
        equi_radius = 0.5 * np.sqrt(4*area/np.pi)  # equivalent radius
        circularity = cv.arcLength(contour,True) / 2 * np.pi * equi_radius

        # only the contour whose area is close to median area 
        # and circularity > threshold (0.87) 
        # and contour is not near the edge
        if (area_median / sigma < area < area_median * sigma 
                and circularity >= 0.87 
                and 2*est_radius < cx < x - 2*est_radius 
                and 2*est_radius < cy < y - 2*est_radius):
            cv.circle(img, (cx,cy), int(equi_radius),(0,0,255),5)
            count += 1
            cv.putText(img, str(count), (cx-10,cy), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            files.write("%s,%s\n"%(count, equi_radius * scale))

    files.close()

def drawRectangularContours(img:np.ndarray, contours, sigma=2):
    '''
    using rectangle model to fit counters and draw rectangle on img.
    Export result as csv file.
    '''
    global scale
    cv.drawContours(img, contours, -1, (0,255,0))
    y=img.shape[0]
    x=img.shape[1]
    areas = np.array([cv.contourArea(contour) for contour in contours], np.int32)
    area_median = np.median(areas)  # calculate the median to exclude noise
    count = 0
    files = open("result.csv", "w", encoding='utf-8')

    for i,contour in enumerate(contours):
        M = cv.moments(contour)
        area = int(M['m00'])  # contour area
        ret = cv.minAreaRect(contour)
        cx,cy = ret[0]
        cx,cy = int(cx),int(cy)
        w,h = sorted(list(ret[1]))
        rectangularity = area / (w*h)
        box = cv.boxPoints(ret)
        box = np.int0(box)

        if (area_median / sigma < area < area_median * sigma
            and rectangularity > 0.7
            and h < cx < x - h and h < cy < y - h):
            cv.drawContours(img,[box],0,(0,0,255),2)
            count += 1
            cv.putText(img, str(count), (cx-10,cy), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            files.write("%s,%s,%s\n"%(count, h * scale, w * scale))

    files.close()

def setScale(event, x, y, flags, para):
    '''
    On mouse function to set scale
    '''
    global pt1, pt2, COLOR_SCALE
    image, win_name = para
    image_copy = image.copy()
    if event == cv.EVENT_LBUTTONDOWN:  # button down
        pt1 = (x, y)
        cv.imshow(win_name, image_copy)
    elif event == cv.EVENT_MOUSEMOVE and flags == cv.EVENT_FLAG_LBUTTON:  # drag
        cv.line(image_copy, pt1, (x,y), COLOR_SCALE, 3)
        cv.imshow(win_name, image_copy)
    elif event == cv.EVENT_LBUTTONUP:  # button up
        pt2 = (x, y)
        cv.imshow(win_name, image_copy)
        cv.destroyWindow(win_name)   

def selectROI(event, x, y, flags, para):
    '''
    On mouse function to select ROI(Region of interest)
    '''
    global pt1, pt2, COLOR_ROI
    image, win_name = para
    image_copy = image.copy()
    if event == cv.EVENT_LBUTTONDOWN: 
        pt1 = (x, y)
        cv.imshow(win_name, image_copy)
    elif event == cv.EVENT_MOUSEMOVE and flags == cv.EVENT_FLAG_LBUTTON: 
        cv.rectangle(image_copy, pt1, (x,y), COLOR_ROI, 3)
        cv.imshow(win_name, image_copy)
    elif event == cv.EVENT_LBUTTONUP: 
        pt2 = (x, y)
        cv.imshow(win_name, image_copy)
        cv.destroyWindow(win_name)


if __name__ == "__main__":
    # select mode
    MODE = input("Mode select (fitting circle: c, fitting rectangle: r):\n> ")
    try:
        PARA_JSON = json.load(open("para.json",'r'))  # Read parameters from json
    except FileNotFoundError:
        PARA_JSON = {
            "circle_mode":{
                "median_blur_kernal":5,
                "gaussian_blur_kernal":11,
                "gaussian_blur_sigma":8,
                "closing_kernal":7,
                "dist_transform_threshold":0.5,
                "area_sigma":1.4
            },
            "rectangle_mode":{
                "median_blur_kernal":5,
                "gaussian_blur_kernal":11,
                "gaussian_blur_sigma":8,
                "closing_kernal":7,
                "dist_transform_threshold":0.15,
                "area_sigma":2

            }
        } 
    finally:
        if MODE == 'c':
            paras = PARA_JSON["circle_mode"]
        elif MODE == 'r':
            paras = PARA_JSON["rectangle_mode"]
        else:
            raise Exception("Mode Error")

    # read data
    img_path = os.path.normpath(input("Please input the path of the image:\n> ").replace('"',''))
    OUTPUT_PATH, ext = os.path.splitext(img_path)
    try:
        os.mkdir(OUTPUT_PATH)
    except FileExistsError:
        print("Warning: file has been processed!")
    os.chdir(OUTPUT_PATH)
    scale_bar = float(input("Please input the physical length of the scale bar:\n> "))
    img0 = cv.imread(img_path)
    print("Image resolution:", img0.shape)

    # Get the ratio between physical lenth and pixals
    cv.namedWindow("Set scale", cv.WINDOW_NORMAL)
    cv.setMouseCallback("Set scale", setScale, (img0, "Set scale"))
    cv.imshow("Set scale", img0)
    cv.waitKey(0)
    scale = scale_bar / np.sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)
    cv.line(img0, pt1, pt2, (255, 0, 0), 3)
    print("scale =", scale)

    # Select the ROI. The scale bar should be excluded.
    cv.namedWindow("Select ROI", cv.WINDOW_NORMAL)
    cv.setMouseCallback("Select ROI", selectROI, (img0, "Select ROI"))
    cv.imshow("Select ROI", img0)
    cv.waitKey(0)
    min_x = min(pt1[0],pt2[0])     
    min_y = min(pt1[1],pt2[1])
    width = abs(pt1[0] - pt2[0])
    height = abs(pt1[1] -pt2[1])
    img_ROI = img0[min_y:min_y+height, min_x:min_x+width]
    cv.rectangle(img0, pt1, pt2, (255, 0, 0), 3)

    # Process the particle detection
    img_ROI_copy = cv.cvtColor(img_ROI, cv.COLOR_BGR2GRAY)
    img_binary = imageBinary(img_ROI_copy, paras["median_blur_kernal"], 
                            paras["gaussian_blur_kernal"],
                            paras["closing_kernal"], 
                            paras["gaussian_blur_sigma"])
    contours = findContours(img_binary, paras["dist_transform_threshold"])
    if MODE == 'c':
        drawCircularContours(img_ROI, contours, paras["area_sigma"])
    elif MODE == 'r':
        drawRectangularContours(img_ROI, contours, paras["area_sigma"])
    img0[min_y:min_y+height, min_x:min_x+width] = img_ROI
    cv.namedWindow("Result", cv.WINDOW_NORMAL)
    cv.imshow("Result", img0)
    cv.imwrite(os.path.join(OUTPUT_PATH, "result.jpg"), img0)
    print("You can delete the misdetect particles manually.")
    cv.waitKey(0)
    cv.destroyAllWindows()
