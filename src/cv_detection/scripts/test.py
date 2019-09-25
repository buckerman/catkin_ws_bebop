#!/usr/bin/env python
import numpy as np
import cv2
from matplotlib import pyplot as plt
import rospkg

rospack = rospkg.RosPack()

# config_path = str(rospack.get_path('cv_detection')+'/config/feature_config.json')
images_path = str(rospack.get_path('cv_detection')+'/imgs/rectangle/cropped/')

# Initiate SIFT detector
orb = cv2.ORB_create()

img1 = cv2.imread(images_path + 'H3.png', 0)          # query Image
# find the keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1,None)
cap = cv2.VideoCapture(0)
while True:
    ret, image = cap.read()
    if ret:
        # img2 = cv2.imread('box_in_scene.png',0)  # target Image
        img2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


        kp2, des2 = orb.detectAndCompute(img2,None)

        # create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match descriptors.
        matches = bf.match(des1,des2)

        # Sort them in the order of their distance.
        matches = sorted(matches, key = lambda x:x.distance)

        good_matches = matches[:30]

        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches     ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()
        h,w = img1.shape[:2]
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)

        dst = cv2.perspectiveTransform(pts,M)
        dst += (w, 0)  # adding offset

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                    singlePointColor = None,
                    matchesMask = matchesMask, # draw only inliers
                    flags = 2)

        img3 = cv2.drawMatches(img1,kp1,img2,kp2,good_matches, None,**draw_params)

        # Draw bounding box in Red
        img3 = cv2.polylines(img3, [np.int32(dst)], True, (0,0,255),3, cv2.LINE_AA)

        cv2.imshow("result", img3)
    k = cv2.waitKey(1)
    if k == 27 :
        break

cv2.destroyAllWindows()