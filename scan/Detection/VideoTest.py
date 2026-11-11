# coding:utf-8
import cv2
from ultralytics import YOLO

# 所需加载的模型目录
path = 'Detection/models/best.pt'
video_path = "TestFiles/1.mp4"

# 加载YOLOv8模型
model = YOLO(path)
cap = cv2.VideoCapture(video_path)

# 设置可调窗口
cv2.namedWindow("YOLOv8 Inference", cv2.WINDOW_NORMAL)

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model(frame, retina_masks=False)
        annotated_frame = results[0].plot(conf=False)

        # 设置窗口大小为原始视频帧尺寸
        cv2.resizeWindow("YOLOv8 Inference", frame.shape[1], frame.shape[0])
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # 检查窗口是否被关闭
        if cv2.getWindowProperty("YOLOv8 Inference", cv2.WND_PROP_VISIBLE) < 1:
            break

        # 按下q键退出
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
