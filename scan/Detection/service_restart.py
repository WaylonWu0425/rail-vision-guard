# coding:utf-8
import os
import time
import subprocess
import sys
import signal
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("restart_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局变量，用于控制程序是否继续运行
running = True
# 当前运行的进程
current_process = None
SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_FILE = SERVICE_DIR / "detection_service.py"

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    global running
    logger.info("接收到终止信号，正在停止服务...")
    running = False
    stop_service()
    sys.exit(0)

def start_service():
    """启动统一的 YOLO 检测服务。"""
    global current_process
    try:
        logger.info("正在启动服务...")
        current_process = subprocess.Popen(
            [sys.executable, str(SERVICE_FILE)],
            cwd=str(SERVICE_DIR)
        )
        logger.info(f"服务已启动，PID: {current_process.pid}")
        return True
    except Exception as e:
        logger.error(f"启动服务失败: {e}")
        return False

def stop_service():
    """停止后端服务"""
    global current_process
    if current_process:
        try:
            logger.info(f"正在停止服务，PID: {current_process.pid}")
            current_process.terminate()
            try:
                current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                current_process.kill()
            current_process = None
            logger.info("服务已停止")
        except Exception as e:
            logger.error(f"停止服务失败: {e}")

def main_loop():
    """服务异常退出时自动恢复，不再按分钟破坏正在播放的检测流。"""
    global running
    
    # 第一次启动服务
    if not start_service():
        logger.error("首次启动服务失败，程序终止")
        return
    
    try:
        while running:
            exit_code = current_process.poll() if current_process else -1
            if exit_code is not None:
                logger.warning("检测服务退出（代码 %s），3秒后重新启动", exit_code)
                time.sleep(3)
                if running and not start_service():
                    time.sleep(10)
            time.sleep(1)
    except Exception as e:
        logger.error(f"主循环发生错误: {e}")
    finally:
        stop_service()

if __name__ == "__main__":
    print("YOLO检测服务守护程序已启动")
    print("按 Ctrl+C 可以退出程序")
    
    # 注册信号处理器，捕获Ctrl+C信号
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行主循环
    main_loop() 
