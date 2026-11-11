import os
#coding:utf-8
import cv2
from ultralytics import YOLO

# 所需加载的模型目录
path = 'models/best.pt'

# Load the YOLOv8 model
model = YOLO(path)

# 设置大华摄像头的 RTSP URL
rtsp_url = os.environ.get("CAMERA_RTSP_URL", "")
cap = cv2.VideoCapture(rtsp_url)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("无法连接到摄像头，请检查 RTSP URL 或网络连接")
    exit()

print('已连接到摄像头:', rtsp_url)

# 主循环
while True:
    # 检查摄像头是否仍打开
    if not cap.isOpened():
        print("摄像头连接已断开")
        break

    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        results = model(frame)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # 检查键盘输入，延迟 30ms
        key = cv2.waitKey(30) & 0xFF
        if key == ord("q") or cv2.getWindowProperty("YOLOv8 Inference", cv2.WND_PROP_VISIBLE) < 1:
            print("用户关闭窗口或按下 'q' 键，程序退出")
            break
    else:
        print("读取帧失败，可能是连接中断")
        break

# 释放资源并关闭窗口
cap.release()
cv2.destroyAllWindows()
print("程序已正常退出")