import cv2
import numpy as np
import math
import time
from collections import deque
from HandTracking import HandDetection
from ImageClassification import Classifier


class GestureControl:
    def __init__(self, model_path="model/keras_model.h5", labels_path="model/labels.txt", max_hands=1, offset=20, img_size=300, smoothing_window=10):
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetection(maxHands=max_hands)
        self.classifier = Classifier(model_path, labels_path)
        self.offset = offset
        self.img_size = img_size
        self.labels = ["0", "1", "2", "3", "4", "5", "A", "B", "C", "E", "F"]
        self.capture = False
        self.result = None
        self.smoothing_window = smoothing_window
        self.predictions = deque(maxlen=smoothing_window)  # Sliding window for smoothing

    def start_capture(self, capture_duration=None):
        self.capture = True
        start_time = time.time()

        while self.capture:
            success, img = self.cap.read()
            if not success:
                continue

            img_output = img.copy()
            hands, img = self.detector.findHands(img)
            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']

                img_white = np.ones((self.img_size, self.img_size, 3), np.uint8) * 255

                # Ensure the cropping coordinates are within the image bounds
                y1, y2 = max(0, y - self.offset), min(img.shape[0], y + h + self.offset)
                x1, x2 = max(0, x - self.offset), min(img.shape[1], x + w + self.offset)

                img_crop = img[y1:y2, x1:x2]

                aspect_ratio = h / w

                if aspect_ratio > 1:
                    k = self.img_size / h
                    w_cal = math.ceil(k * w)
                    img_resize = cv2.resize(img_crop, (w_cal, self.img_size))
                    w_gap = math.ceil((self.img_size - w_cal) / 2)
                    img_white[:, w_gap:w_cal + w_gap] = img_resize
                    prediction, index = self.classifier.getPrediction(img_white, draw=False)
                else:
                    k = self.img_size / w
                    h_cal = math.ceil(k * h)
                    img_resize = cv2.resize(img_crop, (self.img_size, h_cal))
                    h_gap = math.ceil((self.img_size - h_cal) / 2)
                    img_white[h_gap:h_cal + h_gap, :] = img_resize
                    prediction, index = self.classifier.getPrediction(img_white, draw=False)

                self.predictions.append(self.labels[index])  # Add prediction to the sliding window

                # Get the most frequent prediction in the sliding window
                self.result = max(set(self.predictions), key=self.predictions.count)

                cv2.putText(img_output, self.result, (x, y - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

                cv2.imshow("ImageCrop", img_crop)
                cv2.imshow("ImageWhite", img_white)

            cv2.imshow("Image", img_output)
            cv2.waitKey(1)

            # Check if the capture duration has passed
            if capture_duration and (time.time() - start_time) > capture_duration:
                break;
        self.capture = False               

    def stop_capture(self):
        self.capture = False
        self.cap.release()
        cv2.destroyAllWindows()

    def reset_capture(self):
        self.result = None
        self.predictions.clear()

    def get_capture_status(self):
        return self.capture

    def get_result(self):
        return self.result


if __name__ == "__main__":
    gesture_control = GestureControl()
    gesture_control.start_capture(capture_duration=30)  # Run the capture for 30 seconds
    result = gesture_control.get_result()
    print("Detected gesture:", result)
