import requests
import cv2
import numpy as np
import time

import torch

model = torch.hub.load("ultralytics/yolov5", "yolov5s")  # or yolov5n - yolov5x6, custom

save_interval = 0.5
last_save_time = time.time()

# MJPEG 스트림 URL 설정
mjpeg_url = "http://raspberrypi:8000/stream.mjpg"  # 실제 MJPEG 스트림 URL로 변경하세요

# 요청을 보내 MJPEG 스트림을 가져옵니다.
response = requests.get(mjpeg_url, stream=True)
if response.status_code == 200:
    bytes = bytes()
    for chunk in response.iter_content(chunk_size=1024):
        bytes += chunk
        a = bytes.find(b"\xff\xd8")  # JPEG 시작 마커 찾기
        b = bytes.find(b"\xff\xd9")  # JPEG 끝 마커 찾기
        if a != -1 and b != -1:
            jpg = bytes[a : b + 2]  # JPEG 이미지 추출
            bytes = bytes[b + 2 :]
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # MJPEG 스트림 이미지를 화면에 표시
            # cv2.imshow('MJPEG Stream', frame)

            current_time = time.time()
            if current_time - last_save_time >= save_interval:
                cv2.imwrite("capture_picamera.jpg", frame)
                img = "capture_picamera.jpg"
                results = model(img)
                cv2.imwrite("capture_picamera_yolo.jpg", results)
                # results.save(file_name='capture_picamera_yolo.jpg')
                results.show()  # or .show(), .save(), .crop(), .pandas(), etc.
                last_save_time = current_time

            if cv2.waitKey(1) & 0xFF == 27:
                break
else:
    print("Failed to retrieve MJPEG stream.")

cv2.destroyAllWindows()
