# coding:utf-8
import os
import time
import subprocess
import sys
import signal
import threading
import logging
import keyboard

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

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    global running
    logger.info("接收到终止信号，正在停止服务...")
    running = False
    stop_service()
    sys.exit(0)

def key_listener():
    """监听键盘输入，当按下q时退出程序"""
    global running
    try:
        keyboard.wait('q')  # 等待按下q键
        logger.info("检测到q键被按下，正在停止服务...")
        running = False
        stop_service()
        os._exit(0)  # 强制退出程序
    except Exception as e:
        logger.error(f"键盘监听错误: {e}")

def start_service():
    """启动后端服务"""
    global current_process
    try:
        logger.info("正在启动服务...")
        # 使用subprocess启动后端服务
        # 根据实际服务启动命令进行修改
        current_process = subprocess.Popen(
            ["python", "Detection/CamVueScan.py"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True
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
            # 在Windows上使用taskkill强制终止进程及其子进程
            subprocess.run(f"taskkill /F /T /PID {current_process.pid}", shell=True)
            current_process = None
            logger.info("服务已停止")
        except Exception as e:
            logger.error(f"停止服务失败: {e}")

def restart_service():
    """重启后端服务"""
    stop_service()
    time.sleep(1)  # 等待服务完全停止
    return start_service()

def main_loop():
    """主循环，定时重启服务"""
    global running
    
    # 第一次启动服务
    if not start_service():
        logger.error("首次启动服务失败，程序终止")
        return
    
    try:
        while running:
            # 等待60秒（1分钟）
            for _ in range(60):
                if not running:
                    break
                time.sleep(1)
            
            if running:
                logger.info("定时重启时间到，准备重启服务...")
                if not restart_service():
                    logger.error("重启服务失败，尝试在10秒后重试")
                    time.sleep(10)
    except Exception as e:
        logger.error(f"主循环发生错误: {e}")
    finally:
        stop_service()

if __name__ == "__main__":
    print("定时重启服务已启动，服务将每隔1分钟自动重启一次")
    print("按下 'q' 键或 Ctrl+C 可以退出程序")
    
    # 注册信号处理器，捕获Ctrl+C信号
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动键盘监听线程
    keyboard_thread = threading.Thread(target=key_listener, daemon=True)
    keyboard_thread.start()
    
    # 运行主循环
    main_loop() 