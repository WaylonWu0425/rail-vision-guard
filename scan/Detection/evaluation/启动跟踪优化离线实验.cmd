@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
"C:\Users\吴炜\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0offline_lab.py" --dataset "D:\AAA空信242\比赛\进行中\第八届全球校园人工智能算法精英大赛\升级研究\现场评测集_v1" --output "D:\AAA空信242\比赛\进行中\第八届全球校园人工智能算法精英大赛\升级研究\现场评测集_v1\跟踪事件优化_20261017\交互演练" --port 8803 --tracking-profile continuity_v1
pause
