@echo off
chcp 65001 >nul
setlocal
set "PYTHONIOENCODING=utf-8"
echo 启动独立离线实验台：http://127.0.0.1:8803/
echo 本窗口保持打开；按 Ctrl+C 正常停止。本脚本不更改正式系统或摄像头配置。
"C:\Users\吴炜\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0offline_lab.py" --dataset "D:\AAA空信242\比赛\进行中\第八届全球校园人工智能算法精英大赛\升级研究\现场评测集_v1" --output "D:\AAA空信242\比赛\进行中\第八届全球校园人工智能算法精英大赛\升级研究\现场评测集_v1\离线视频实验_20261016\交互演练" --port 8803
pause
