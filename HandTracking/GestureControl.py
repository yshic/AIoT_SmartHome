import cv2
import numpy as np
import time
import HandTracking as ht

wCam, hCam = 640, 480

cap =  cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

cTime = 0
pTime = 0

detector = ht.HandDetection(detectionCon=0.7)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPos(img, draw=False)
    if len(lmList) != 0:
        print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        cv2.circle(img, (x1, y1), 15, (255, 0 , 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0 , 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 6, 250), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)