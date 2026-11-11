@echo off
setlocal
cd /d "%~dp0"
py -3.12 coupler_service.py
if errorlevel 1 (
  echo.
  echo 车钩识别服务启动失败。请确认 Python 3.12 和本目录 .ncnn-runtime 已安装。
  pause
)
