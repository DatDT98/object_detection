import time
from detect import detect
import cv2
import numpy as np
from copy import deepcopy
from utils.face_processing import get_coordinates_with_margin
from datetime import datetime, timedelta
import pygame
pygame.mixer.init()


def alert(audio, timer, alert_time):
    if datetime.now().time() > alert_time[0].time():
        pygame.mixer.Sound(audio).play()
        pygame.mixer.Sound(audio).stop()
        time = datetime.now()+timedelta(seconds=timer)
        alert_time.clear()
        alert_time.append(time)
def violate_object_detect(model, url, image_size, iou_thres, conf_thres, device, sort_tracker, areas):
    alert_time=[datetime.now()]

    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        name_class, counted_vehicle, timestamp, bounding_boxes, scores, response_bounding_boxes = detect(model, frame, image_size, iou_thres, conf_thres, device)
        time_arrival = time.time()
        draw_frame = deepcopy(frame)

        if len(scores) > 0:
            print("*******BB: ", len(response_bounding_boxes))
            response_bounding_boxes = np.array(
                [get_coordinates_with_margin(draw_frame, box) for box in response_bounding_boxes]).reshape(-1, 4)
            # Change confidence to (N, 1)
            scores = np.array(scores)
            confidences = scores.reshape(-1, 1)
            detections = response_bounding_boxes.astype(np.float32)
            detections = np.hstack((detections, confidences))
            area = areas[0].detection_area
            cv2.rectangle(frame, (int(area.x), int(area.y)), (int(area.x + area.width), int(area.y + area.height)), [0, 255, 0], 3)
            # Do tracking
            trackers = sort_tracker.update(detections)

            for i, tracker in enumerate(trackers):
                is_Inside = check_object_location(response_bounding_boxes[i], areas)
                if is_Inside == True:
                    cv2.rectangle(frame,
                                  (int(response_bounding_boxes[i][0]), int(response_bounding_boxes[i][1]))
                                  , (int(response_bounding_boxes[i][2]), int(response_bounding_boxes[i][3])),
                                  [0, 0, 255], 3)
                    alert("./alert.ogg", 3, alert_time)
                    yield name_class, counted_vehicle, timestamp, bounding_boxes, trackers

        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Image", frame)
        cv2.waitKey(1)

def check_object_location(bounding_box, areas):
    if bounding_box is None:
        return False
    center_x = int((bounding_box[0] + bounding_box[2]) / 2)
    center_y = int((bounding_box[1] + bounding_box[3]) / 2)
    for area in areas:
        area_bounding_box = area.detection_area
        if area_bounding_box \
                and area_bounding_box.x <= center_x <= area_bounding_box.x+area_bounding_box.width \
                and area_bounding_box.y < center_y < area_bounding_box.y + area_bounding_box.height:
            return True

    return False

def caculate_distance_object(bounding_box_1, bounding_box_2):

    center_x_1 = int((bounding_box_1[0] + bounding_box_1[2]) / 2)
    center_y_1 = int((bounding_box_1[1] + bounding_box_1[3]) / 2)
    center_x_2 = int((bounding_box_2[0] + bounding_box_2[2]) / 2)
    center_y_2 = int((bounding_box_2[1] + bounding_box_2[3]) / 2)
    dist = np.sqrt((center_x_1 - center_x_2) ** 2 + (
                center_y_1 - center_y_2) ** 2)

    return dist



