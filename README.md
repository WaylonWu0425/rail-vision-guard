# 视界巡警（Rail Vision Guard）

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

1. 安装项目各子目录依赖，并启动 MySQL 与 Redis。前端依赖记录在 `station-monitoring-frontend/package-lock.json`，后端依赖记录在 `station-monitoring-banckend/pom.xml`，检测服务依赖记录在 `scan/Detection/requirements-runtime.txt`。
2. 将 `station-monitoring-banckend/src/main/resources/application.example.yaml` 复制为同目录的 `application.yaml`，根据本机数据库、Redis 与相关服务填写环境变量及连接参数。将 `scan/Detection/camera_config.example.json` 复制为 `camera_config.json`，按获授权的设备填写连接信息；无摄像头时保持示例设备禁用。
3. 在 `station-monitoring-frontend/` 运行 `npm ci`、`npm run serve`。在 `station-monitoring-banckend/` 按 `pom.xml` 构建并启动 Spring Boot。检测服务的独立启动方式见 `scan/Detection/README` 和根目录 `DEMO_RUNBOOK.md`。
4. 如需一次性演示启动，可参考 `start_demo.ps1`。运行前先核对其中的本机目录与端口配置。

数据库首次部署可使用 `station-monitoring-db/station_monitoring_schema.sql` 建表。仓库不包含真实用户记录、摄像头口令或现场监控视频。

## 能力与验证

现有模型 `best.pt` 用于人员、车辆检测。系统将检测结果与摄像头、时间、区域规则和截图证据关联，并支持人工核查。与检测效果有关的验证记录见 `docs/`；模型能力、受控演示和现场验证分别说明，不将单一演示结果概括为通用准确率。

`scan/Detection/models/best12_20.param` 与 `.bin` 是老师提供并获许可使用的 NCNN 模型文件，用于作业感知原型的本地推理；它与 `best.pt` 承担的任务不同。模型接入说明见 `scan/Detection/车钩识别接入说明.md`。移动端 APK 是独立交付物，不属于本仓库网页端源码。

## 团队与版本

最初版本由视界巡警项目团队编写。后续工作围绕检测服务接入、跟踪与规则验证、业务闭环、空间展示和作业感知原型逐步开展。版本过程与对应材料见 `VERSION_HISTORY.md`。Git 历史中的早期提交是根据原版和当前保存的源码快照**在建库时导入**，提交时间不是当时的开发时间；此后的修改按实际开发过程提交。

项目开发使用常规开发工具和 AI 辅助工具进行代码检查、实现与文档整理；团队负责需求判断、代码复核、场景解释与测试。第三方框架、基础模型及老师提供的材料会在对应说明中标明来源和用途。
