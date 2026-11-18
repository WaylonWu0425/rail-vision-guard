# 视界巡警——车站视频智能识别与协同平台

面向铁路站场的视频智能监控与事件核查原型。系统连接摄像头或本地视频，组织实时画面、人员与车辆目标提示、区域规则、告警证据、录像回放和人工核查，帮助值守人员沿“发现—查看证据—核查—回溯”的路径处理现场信息。

## 项目结构

| 目录 | 用途 |
| --- | --- |
| `station-monitoring-frontend/` | Vue 工作台、监控与业务页面、三维站场场景 |
| `station-monitoring-banckend/` | Spring Boot 业务接口、告警与设备数据 |
| `scan/Detection/` | Python 检测、识别验证和本地服务 |
| `scan/recoder_server/` | 视频录制相关脚本 |
| `station-monitoring-db/` | 数据库结构与迁移脚本 |
| `station-monitoring-yidongend/` | 移动端源码 |
| `docs/` | 演示、验证与设计记录 |

前端使用 Vue；后端使用 Java/Spring Boot；识别服务使用 Python、OpenCV 和 Ultralytics。三维站场用于空间化展示与交互；没有完成设备与真实坐标标定的标记以示意状态呈现。

## 本地运行

评审首次运行请按[环境配置与验证](docs/评审运行指南.md)配置。指南提供 Windows PowerShell 命令、依赖目录、端口和两个验证入口：

- **先验证人车识别**：安装 Python 运行依赖，放置评审用权重，使用自备或获授权的录像运行验证脚本。
- **再启动业务工作台**：配置 JDK 17、Maven、Node.js、MySQL 和 Redis，准备 SDK，依次启动前端、Java 后端和检测服务。

根目录 [环境变量模板](.env.example) 用于准备本地配置。首次建表使用 `station-monitoring-db/station_monitoring_schema.sql`，只对新的演示数据库执行。

## 能力与验证

「连挂复核」源码作为作业感知原型保留，当前工作台导航已隐藏该入口。原型验证范围见[作业感知升级设计与实施报告](docs/作业感知升级设计与实施报告.md)。

「人车识别」支持从录像时间轴定位画面、切换同帧原图与标注、记录人工复核片段。「告警中心」按摄像头和发生时间关联录像。系统录像的复核意见可供已登录的操作人员交接查看，本地导入录像的标记随当前页面会话保留。

在 `scan/Detection/` 运行 `python original_recognition.py` 启动人车识别服务（5002）。如需 AVI 等格式转码预览，运行 `python -m pip install ncnn imageio-ffmpeg` 安装配套依赖，再运行 `python coupler_service.py`（5003）。可用 `RAIL_FFMPEG_PATH` 指定 FFmpeg，或用 `RAIL_COUPLER_MODEL_DIR` 指定 NCNN 模型目录。录像管理后端导入非 MP4/WebM 文件时，从 `RAIL_FFMPEG_PATH` 或系统 `PATH` 调用 FFmpeg。

「人车识别」页使用 `yolov8l.pt`，仅输出人员和汽车。启动人车识别服务前，将老师提供的权重放在 `scan/Detection/models/yolov8l.pt`。加载时校验文件 SHA-256 和类别映射。

后台自动告警使用 `best.pt`，将检测结果与摄像头、时间、区域规则和截图证据关联，支持人工核查。与检测效果有关的验证记录见 `docs/`。

`scan/Detection/models/best12_20.param` 与 `.bin` 是老师提供并获许可使用的 NCNN 模型文件，用于作业感知原型的本地推理；它与 `best.pt` 承担的任务不同。模型接入说明见 `scan/Detection/车钩识别接入说明.md`。移动端 APK 是独立交付物，不属于本仓库网页端源码。

## 团队与版本

最初版本由视界巡警项目团队编写。后续工作围绕检测服务接入、跟踪与规则验证、业务闭环、空间展示和作业感知原型逐步开展。版本过程与对应材料见 `VERSION_HISTORY.md`。Git 历史中的早期提交是根据原版和当前保存的源码快照**在建库时导入**，提交时间不是当时的开发时间；此后的修改按实际开发过程提交。

团队协作分工包括场景与产品、系统与集成、算法与数据。对应工作包括事件定义与页面设计、前后端和视频接入、模型与现场样本验证。正式参赛成员信息以赛事报名表为准。

项目开发使用常规开发工具和 AI 辅助工具进行代码检查、实现与文档整理；团队负责需求判断、代码复核、场景解释与测试。第三方框架、基础模型及老师提供的材料会在对应说明中标明来源和用途。
