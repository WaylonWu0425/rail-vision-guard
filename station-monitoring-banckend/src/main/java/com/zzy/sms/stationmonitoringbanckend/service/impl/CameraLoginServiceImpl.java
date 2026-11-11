package com.zzy.sms.stationmonitoringbanckend.service.impl;

import com.netsdk.lib.NetSDKLib;
import com.netsdk.lib.ToolKits;
import com.sun.jna.Pointer;
import com.zzy.sms.stationmonitoringbanckend.entity.BallCamera;
import com.zzy.sms.stationmonitoringbanckend.entity.Camera;
import com.zzy.sms.stationmonitoringbanckend.entity.CameraAlarm;
import com.zzy.sms.stationmonitoringbanckend.entity.GunCamera;
import com.zzy.sms.stationmonitoringbanckend.mapper.BallCameraMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.CameraMapper;
import com.zzy.sms.stationmonitoringbanckend.mapper.GunCameraMapper;
import com.zzy.sms.stationmonitoringbanckend.service.CameraAlarmService;
import com.zzy.sms.stationmonitoringbanckend.service.CameraLoginService;
import com.zzy.sms.stationmonitoringbanckend.util.DateTimeUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component
@Service
public class CameraLoginServiceImpl implements CameraLoginService {
    public boolean cameraInited = false;
    public Map<Long, String> reLoginCameraSet = new ConcurrentHashMap<>();
    public Map<Long, String> offlineCameraSet = new ConcurrentHashMap<>();
    public List<BallCamera> ballCameraList = new ArrayList<>();
    public List<GunCamera> gunCameraList = new ArrayList<>();
    public static NetSDKLib netsdk = NetSDKLib.NETSDK_INSTANCE;
    public Map<Long, NetSDKLib.LLong> loggedCameraMap = new HashMap<>();

    /** 离线摄像头登录失败冷却期：5 分钟内不再重试（毫秒） */
    private static final long LOGIN_FAIL_COOLDOWN_MS = 5 * 60 * 1000L;
    /** 记录每台摄像头最后一次登录失败的时间戳，用于冷却判断 */
    private final Map<Long, Long> lastFailTimeMap = new ConcurrentHashMap<>();

    private final DisConnect disConnect = new DisConnect();
    private final HaveReConnect haveReConnect = new HaveReConnect();
    private volatile boolean sdkInitialized = false; // SDK 初始化状态


    @Autowired
    private BallCameraMapper ballCameraMapper;
    @Autowired
    private GunCameraMapper gunCameraMapper;
    @Autowired
    private CameraMapper cameraMapper;
    @Autowired
    private CameraAlarmService cameraAlarmService;
    @Autowired
    private DateTimeUtil dateTimeUtil;

//    @PostConstruct
//    public void init() {
//        // 将 SDK 初始化移到应用启动时执行，避免重复初始化
//        boolean bInit = netsdk.CLIENT_Init(disConnect, null);
//        if (!bInit) {
//            log.error("初始化摄像机 SDK 失败");
//            return;
//        }
//        netsdk.CLIENT_SetAutoReconnect(haveReConnect, null);
//        log.info("自动重连回调已设置");
//
//        NetSDKLib.NET_PARAM netParam = new NetSDKLib.NET_PARAM();
//        netParam.nConnectTime = 20000; // 延长连接超时时间至 20 秒
//        netParam.nGetConnInfoTime = 3000;
//        netParam.nGetDevInfoTime = 3000;
//        netsdk.CLIENT_SetNetworkParam(netParam);
//
//        initCameraObject();
//    }


    @PostConstruct
    public void init() {
        // SDK 初始化失败时持续重试
        int retryInterval = 5000; // 重试间隔 5 秒
        while (!sdkInitialized) {
            boolean bInit = netsdk.CLIENT_Init(disConnect, null);
            if (!bInit) {
                log.error("初始化摄像机 SDK 失败，将在 {} 毫秒后重试", retryInterval);
                try {
                    Thread.sleep(retryInterval);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    log.error("重试等待被中断", e);
                    return; // 如果被中断则退出
                }
            } else {
                sdkInitialized = true;
                log.info("摄像机 SDK 初始化成功");
                netsdk.CLIENT_SetAutoReconnect(haveReConnect, null);
                log.info("自动重连回调已设置");

                NetSDKLib.NET_PARAM netParam = new NetSDKLib.NET_PARAM();
                netParam.nConnectTime = 3000; // 连接超时时间 3 秒（离线摄像头快速失败，避免拖慢启动）
                netParam.nGetConnInfoTime = 3000;
                netParam.nGetDevInfoTime = 3000;
                netsdk.CLIENT_SetNetworkParam(netParam);

                initCameraObject();
            }
        }
    }


    @Scheduled(fixedDelay = 5000) // 隔段时间检查新摄像头
    public void checkAndInitNewCameras() {
        if (!sdkInitialized) {
            log.warn("SDK 未初始化，跳过新摄像头检查");
            return;
        }

        // 获取最新的摄像头列表
        List<BallCamera> latestBallCameraList = ballCameraMapper.getAllBallCamera();
        List<GunCamera> latestGunCameraList = gunCameraMapper.getAllGunCamera();

        // 更新内存中的摄像头列表
        synchronized (this) { // 同步更新列表
            ballCameraList.clear();
            ballCameraList.addAll(latestBallCameraList);
            gunCameraList.clear();
            gunCameraList.addAll(latestGunCameraList);
        }

        long now = System.currentTimeMillis();

        // 初始化新接入的球机（处于登录失败冷却期的跳过）
        for (BallCamera camera : latestBallCameraList) {
            if (!loggedCameraMap.containsKey(camera.getId()) && !inCooldown(camera.getId(), now)) {
                log.info("检测到新球机: {}，尝试初始化", camera.getIp());
                initAndLoginBallCamera(camera);
            }
        }

        // 初始化新接入的枪机（处于登录失败冷却期的跳过）
        for (GunCamera camera : latestGunCameraList) {
            if (!loggedCameraMap.containsKey(camera.getId()) && !inCooldown(camera.getId(), now)) {
                log.info("检测到新枪机: {}，尝试初始化", camera.getIp());
                initAndLoginGunCamera(camera);
            }
        }
    }

    /** 判断摄像头是否处于登录失败冷却期内 */
    private boolean inCooldown(Long cameraId, long now) {
        Long lastFail = lastFailTimeMap.get(cameraId);
        return lastFail != null && (now - lastFail) < LOGIN_FAIL_COOLDOWN_MS;
    }

    @Override
    public void initCameraObject() {
        if (!cameraInited) {
            ballCameraList = ballCameraMapper.getAllBallCamera();
            gunCameraList = gunCameraMapper.getAllGunCamera();
            loginAllCameras();
        }
    }

    @Override
    public void loginAllCameras() {
        if (!cameraInited) {
            for (BallCamera entry : ballCameraList) {
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                initAndLoginBallCamera(entry);
            }

            for (GunCamera entry : gunCameraList) {
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                initAndLoginGunCamera(entry);
            }
            cameraInited = true;
            log.info("摄像机登录结束");
        }
    }

    public void initAndLoginBallCamera(BallCamera camera) {
        // 移除重复的 CLIENT_Init 调用，移至 @PostConstruct
        netsdk.CLIENT_SetAutoReconnect(haveReConnect, null); // 确保每次登录前设置重连回调

        boolean isLogin = login(camera.getId(), camera.getIp(), camera.getPort(),
                camera.getUsername(), camera.getPassword(), netsdk);
        if (isLogin) {
            updateCameraStatus(camera.getId(), (byte) 0);
            log.info("球机 {} 登录成功", camera.getIp());
        }
    }

    public void initAndLoginGunCamera(GunCamera camera) {
        // 移除重复的 CLIENT_Init 调用，移至 @PostConstruct
        netsdk.CLIENT_SetAutoReconnect(haveReConnect, null); // 确保每次登录前设置重连回调

        boolean isLogin = login(camera.getId(), camera.getIp(), camera.getPort(),
                camera.getUserName(), camera.getPassword(), netsdk);
        if (isLogin) {
            updateCameraStatus(camera.getId(), (byte) 0);
            log.info("枪机 {} 登录成功", camera.getIp());
        }
    }

    private boolean login(Long id, String ip, int port, String userName, String password, NetSDKLib netsdk) {
        NetSDKLib.NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY pstInParam = new NetSDKLib.NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY();
        pstInParam.szIP = ip.getBytes();
        pstInParam.nPort = port;
        pstInParam.szUserName = userName.getBytes();
        pstInParam.szPassword = password.getBytes();

        NetSDKLib.NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY pstOutParam = new NetSDKLib.NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY();
        NetSDKLib.LLong m_hLoginHandle = netsdk.CLIENT_LoginWithHighLevelSecurity(pstInParam, pstOutParam);

        if (m_hLoginHandle.longValue() == 0) {
            // 登录失败：记录失败时间戳进入冷却期，日志降级为 debug 避免假摄像头刷屏
            lastFailTimeMap.put(id, System.currentTimeMillis());
            log.debug("登录摄像机 ip = {} Port = {} 失败. 失败原因为：{}.", ip, port, ToolKits.getErrorCodePrint());
            return false;
        } else {
            // 登录成功：清除冷却标记
            lastFailTimeMap.remove(id);
            log.info("登录摄像机 ip = {} Port = {} 成功.", ip, port);
            loggedCameraMap.put(id, m_hLoginHandle);
            return true;
        }
    }

    private class DisConnect implements NetSDKLib.fDisConnect {
        public void invoke(NetSDKLib.LLong m_hLoginHandle, String pchDVRIP, int nDVRPort, Pointer dwUser) {
            for (Map.Entry<Long, NetSDKLib.LLong> entry : loggedCameraMap.entrySet()) {
                if (entry.getValue().equals(m_hLoginHandle)) {
                    Long cameraId = entry.getKey();
                    log.info("摄像机 {} : {} 断开连接", pchDVRIP, nDVRPort); // 修正 IP 显示问题
                    CameraAlarm cameraAlarm = new CameraAlarm();
                    cameraAlarm.setCameraId(cameraId);
                    cameraAlarm.setCreateTime(dateTimeUtil.getCurrentTime());
                    cameraAlarm.setDealFlag("0");
                    cameraAlarmService.insertCameraAlarm(cameraAlarm);  //添加摄像头报警信息
                    loggedCameraMap.remove(cameraId);
                    offlineCameraSet.put(cameraId, "");
                    updateCameraStatus(cameraId, (byte) 1);
                    manualReconnect(pchDVRIP);
                    break;
                }
            }
        }
    }

    private class HaveReConnect implements NetSDKLib.fHaveReConnect {
        @Override
        public void invoke(NetSDKLib.LLong m_hLoginHandle, String pchDVRIP, int nDVRPort, Pointer dwUser) {
            log.info("进入 HaveReConnect 回调，IP: {}, 端口: {}", pchDVRIP, nDVRPort);
            Camera camera = cameraMapper.getCameraByIp(pchDVRIP);
            if (camera == null) {
                log.error("重连失败：未找到IP为 {} 的摄像头", pchDVRIP);
                return;
            }
            loggedCameraMap.put(camera.getId(), m_hLoginHandle);
            log.info("摄像机 {} : {} 重新建立连接", pchDVRIP, nDVRPort);
            updateCameraStatus(camera.getId(), (byte) 0);
            reLoginCameraSet.put(camera.getId(), "");
        }
    }

    private void manualReconnect(String ip) {
        log.info("尝试手动重连摄像机: {}", ip);
        // 从现有列表中查找匹配的摄像头
        for (BallCamera ballCamera : ballCameraList) {
            if (ip.equals(ballCamera.getIp())) {
                int maxRetries = 50;
                int retryInterval = 1000; // 1 秒
                for (int i = 0; i < maxRetries; i++) {
                    if (initAndLoginBallCameraWithRetry(ballCamera)) {
                        return;
                    }
                    log.info("球机 {} 第 {} 次重连失败，等待 {} 毫秒后重试", ip, i + 1, retryInterval);
                    try {
                        Thread.sleep(retryInterval);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
                log.error("手动重连球机 {} 失败，已达到最大重试次数", ip);
                return;
            }
        }
        for (GunCamera gunCamera : gunCameraList) {
            if (ip.equals(gunCamera.getIp())) {
                int maxRetries = 50;
                int retryInterval = 1000; // 1 秒
                for (int i = 0; i < maxRetries; i++) {
                    if (initAndLoginGunCameraWithRetry(gunCamera)) {
                        return;
                    }
                    log.info("枪机 {} 第 {} 次重连失败，等待 {} 毫秒后重试", ip, i + 1, retryInterval);
                    try {
                        Thread.sleep(retryInterval);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
                log.error("手动重连枪机 {} 失败，已达到最大重试次数", ip);
                return;
            }
        }
        log.error("手动重连失败：未找到IP为 {} 的摄像头", ip);
    }

    private boolean initAndLoginBallCameraWithRetry(BallCamera camera) {
        netsdk.CLIENT_SetAutoReconnect(haveReConnect, null);
        boolean isLogin = login(camera.getId(), camera.getIp(), camera.getPort(),
                camera.getUsername(), camera.getPassword(), netsdk);
        if (isLogin) {
            updateCameraStatus(camera.getId(), (byte) 0);
            log.info("球机 {} 重连成功", camera.getIp());
        }
        return isLogin;
    }

    private boolean initAndLoginGunCameraWithRetry(GunCamera camera) {
        netsdk.CLIENT_SetAutoReconnect(haveReConnect, null);
        boolean isLogin = login(camera.getId(), camera.getIp(), camera.getPort(),
                camera.getUserName(), camera.getPassword(), netsdk);
        if (isLogin) {
            updateCameraStatus(camera.getId(), (byte) 0);
            log.info("枪机 {} 重连成功", camera.getIp());
        }
        return isLogin;
    }

    private void updateCameraStatus(Long id, Byte status) {
        cameraMapper.updateStatus(id, status);
        log.info("摄像头 {} 状态更新为 {}", id, (status == 0 ? "在线" : "离线"));
    }

    @Override
    public int countOnlineCameras() {
        return loggedCameraMap.size();
    }

    // PTZ 控制指令映射：前端指令码 -> 大华 SDK CLIENT_DHPTZControlEx 命令值（DHNetSDK 标准定义 0x01~0x0E）
    private static final Map<String, Integer> PTZ_COMMAND_MAP = new HashMap<>();

    static {
        PTZ_COMMAND_MAP.put("Up", 0x01);          // 上
        PTZ_COMMAND_MAP.put("Down", 0x02);        // 下
        PTZ_COMMAND_MAP.put("Left", 0x03);        // 左
        PTZ_COMMAND_MAP.put("Right", 0x04);       // 右
        PTZ_COMMAND_MAP.put("LeftUp", 0x05);      // 上左
        PTZ_COMMAND_MAP.put("RightUp", 0x06);     // 上右
        PTZ_COMMAND_MAP.put("LeftDown", 0x07);    // 下左
        PTZ_COMMAND_MAP.put("RightDown", 0x08);   // 下右
        PTZ_COMMAND_MAP.put("ZoomTele", 0x09);    // 变倍+（拉近）
        PTZ_COMMAND_MAP.put("ZoomWide", 0x0a);    // 变倍-（拉远）
        PTZ_COMMAND_MAP.put("FocusNear", 0x0b);   // 聚焦+
        PTZ_COMMAND_MAP.put("FocusFar", 0x0c);    // 聚焦-
        PTZ_COMMAND_MAP.put("IrisLarge", 0x0d);   // 光圈+
        PTZ_COMMAND_MAP.put("IrisSmall", 0x0e);   // 光圈-
    }

    // 大华 NET_PTZ_ControlType 预置点相关指令码
    private static final int PTZ_GOTO_PRESET = 0x81;  // 跳转预置点
    private static final int PTZ_SET_PRESET  = 0x82;  // 添加/更新预置点
    private static final int PTZ_DEL_PRESET  = 0x83;  // 删除预置点

    @Override
    public boolean gotoPreset(Long cameraId, int presetId, int channel) {
        NetSDKLib.LLong handle = loggedCameraMap.get(cameraId);
        if (handle == null || handle.longValue() == 0) {
            log.warn("跳转预置点失败: 摄像头 {} 未登录或离线", cameraId);
            return false;
        }
        if (presetId < 0 || presetId > 255) {
            presetId = 1;
        }
        // CLIENT_DHPTZControlEx(handle, channel, GotoPreset, 0, 0, presetId, 0)
        // nPresetID=presetId 指定跳转到第几个预置点
        boolean ok = netsdk.CLIENT_DHPTZControlEx(handle, channel, PTZ_GOTO_PRESET, 0, 0, presetId, 0);
        if (ok) {
            log.info("摄像头 {} 跳转预置点 {} 指令下发成功", cameraId, presetId);
        } else {
            log.error("跳转预置点失败: cameraId={}, presetId={}, 错误={}",
                    cameraId, presetId, ToolKits.getErrorCodePrint());
        }
        return ok;
    }

    @Override
    public boolean ptzControl(Long cameraId, String code, boolean stop, int speed, int channel) {
        NetSDKLib.LLong handle = loggedCameraMap.get(cameraId);
        if (handle == null || handle.longValue() == 0) {
            log.warn("PTZ 控制失败: 摄像头 {} 未登录或离线", cameraId);
            return false;
        }
        Integer command = PTZ_COMMAND_MAP.get(code);
        if (command == null) {
            log.warn("PTZ 控制失败: 未知指令 {}", code);
            return false;
        }
        if (speed < 1 || speed > 8) {
            speed = 5;
        }
        // dwStop: 0=开始运动, 1=停止运动; dwSpeed: 1-8; nPresetID 非预置点指令传 0
        boolean ok = netsdk.CLIENT_DHPTZControlEx(handle, channel, command, stop ? 1 : 0, speed, 0, 0);
        if (!ok) {
            log.error("PTZ 指令下发失败: cameraId={}, code={}, stop={}, 错误={}",
                    cameraId, code, stop, ToolKits.getErrorCodePrint());
        }
        return ok;
    }

    @Override
    public int countOfflineCameras() {
        int totalCameras = ballCameraMapper.getBallCameraCount() + gunCameraMapper.getGunCameraCount();
        return totalCameras - loggedCameraMap.size();
    }
}