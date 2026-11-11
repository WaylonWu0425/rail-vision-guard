package com.zzy.sms.stationmonitoringbanckend.service;

public interface CameraLoginService {
    int countOnlineCameras();
    int countOfflineCameras();

    void initCameraObject();

    void loginAllCameras();

    /**
     * 云台控制（PTZ）
     *
     * @param cameraId 摄像头 ID
     * @param code     控制指令：Up/Down/Left/Right/LeftUp/RightUp/LeftDown/RightDown/ZoomTele/ZoomWide/FocusNear/FocusFar/IrisLarge/IrisSmall
     * @param stop     true=停止运动, false=开始运动
     * @param speed    速度 1-8
     * @param channel  通道号（IPC 一般为 0）
     * @return 指令是否下发成功
     */
    boolean ptzControl(Long cameraId, String code, boolean stop, int speed, int channel);

    /**
     * 跳转预置点（回到初始位置）
     *
     * @param cameraId 摄像头 ID
     * @param presetId 预置点编号（camera 表 initViewPoint 字段，默认 1）
     * @param channel  通道号（IPC 一般为 0）
     * @return 指令是否下发成功
     */
    boolean gotoPreset(Long cameraId, int presetId, int channel);
}
