# 现场评测与回退说明

本工具不训练模型，不导入正式告警服务，不写业务数据库，不上传现场素材。现有模型和正式服务仍默认full640。84张样本不是84个独立场景，不能据此宣传泛化性能。

## 1. 打开人工复核工具

已启动地址：<http://127.0.0.1:8799/>。只监听本机，不应配置端口转发。默认显示首批10张；可切换全部84张。

在本目录打开PowerShell，重启命令如下（Python可替换为安装了运行依赖的解释器）：

```powershell
$python = 'C:\Users\吴炜\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$dataset = 'D:\AAA空信242\比赛\进行中\第八届全球校园人工智能算法精英大赛\升级研究\现场评测集_v1'
& $python .\workbench.py serve --dataset $dataset --port 8799
```

先检查原图与人员：所有可定位的人员都要框，不能只保留模型已找到的人。用“画人员框”拖动补框，用“选择/移动/调整”移动和拖动四角修框；右侧选择框后可直接输入原图像素坐标。放大后画布区域可滚动；不改变图片纵横比。

无可评价人员时明确勾选“确认此图没有可评价人员”。严重遮挡无法可靠标注的区域可画忽略区，不要为排除错误预测而画忽略区。完成检查后勾选“已逐项人工复核”，再保存；只点保存草稿不会进入评测。修改框后需要重新确认复核。界面不会替你确认真值。

人工确认仅表示人员目标框，不表示违规入侵。若背景照片有远处人员，不能标无人。两张带原有检测框的图片已经排除，原始照片中的小尺寸人员由用户确认真实拍摄。

## 2. 文件与复现

- manifest.json：原素材路径、哈希、片段分组、时间点和划分；images保存派生图片，原素材不变。
- annotations/*.json：人员框、矩形忽略区、人工复核状态、时间和预标注来源；未复核值不是训练真值。
- labels/*.txt：class 0代表person的YOLO归一化框；使用前必须检查同名JSON的reviewed状态，不能直接把整个labels目录当已核验数据集。
- history：用户再次保存时保留上一次JSON；首次预标注只写未存在文件，不覆盖人工标注。

首次准备新数据集（已有manifest时拒绝覆盖）：

```powershell
& $python .\workbench.py prepare --dataset $dataset --videos 'D:\AAA空信242\比赛\进行中\第八届全球校园人工智能算法精英大赛\真实车站监控视频' --photos 'D:\AAA空信242\比赛\进行中\第八届全球校园人工智能算法精英大赛\系统运行监控照片'
& $python .\workbench.py prelabel --dataset $dataset
```

当前视频按片段分组：列车运行、夜晚监控为调参组；环境监控、人员MP4为测试组；4张未带旧检测标注的照片保守放在同一测试组。分组不是已确认的摄像头ID。若确认跨文件属于同一机位/连续场景，必须合并到同一分组和划分，并重新冻结评测；不可反复根据测试结果调参。

## 3. 对照评测

```powershell
& $python .\workbench.py evaluate --dataset $dataset --split test --device cpu --repeats 3 --output ($dataset + '\runs\test_001')
```

输出目录必须新建，不覆盖旧实验。运行前安装本目录requirements.txt及上级运行依赖。没有人工复核样本则拒绝生成准确率报告。部分样本已复核时可生成中间报告，但offlineGatePassed必须为false；完整测试集复核、有明确无人负例、相对基线至少少漏1个小目标、精确率不降低、无人图误检不增加，才通过离线门槛。

输出含冻结manifest、每策略逐图人员预测及真值快照、派生图片哈希、误框漏框、模型哈希、环境、置信度、精确率/召回率及小目标漏检数、完整推理耗时中位数/P95、离线循环吞吐和采样RSS峰值。忽略规则：先匹配GT，再忽略预测框面积至少50%落在忽略区内的未匹配框。GT若位于忽略区内，人工应删除该不可评价GT，避免含义冲突。

三种策略：整图640、整图1280、960×960分块20%重叠输入640，分块回映射后类别内IoU 0.5 NMS。默认阈值均0.45，不进行自动阈值搜索。速度在同一设备预热后重复测量；模型单次耗时与离线实际循环吞吐分开。RSS为进程采样值，不是精确GPU显存峰值；GPU时延显式同步。无人图误检为backgroundFp，其他图的误检仍计入总体精确率。

## 4. 启用与回退

离线过门槛并不等于已允许上线；还必须在原单机实机条件下记录30分钟画面、事件去重、断流恢复及资源曲线。实测未完成之前保持原默认。

在识别服务目录的新PowerShell进程启动可选策略：

```powershell
$env:DETECTION_STRATEGY = 'tiled640' # 或full1280；仅候选通过验收后使用
.\start_detection.ps1
```

改变策略必须重启识别服务；不要运行两份争用5000端口。/health的strategy和inputSize用于核对。任务状态performance保留原字段，追加strategy/inputSize，inferenceMs为完整帧推理EMA、inferenceFps为实际完成间隔频率EMA，不再为耗时倒数；第一帧频率为0。

回退：先正常停止识别服务，再设置`$env:DETECTION_STRATEGY = 'full640'`并重新启动。不改模型权重，不迁移数据库。非法策略使模型未就绪，拒绝启动任务；推理异常停止该任务，保留错误信息，不暗中回退。失败后先停止任务，再检查配置和资源、重新启动。

## 5. 检查命令

在上级Detection目录运行：

```powershell
& $python -m unittest discover -s evaluation -p 'test_*.py' -v
& $python -m unittest test_detection_logic -v
& $python .\evaluation\smoke_browser.py
& $python .\evaluation\smoke_inference.py --image ($dataset + '\images\photo_20261016-162712.jpg')
```

浏览器冒烟检查需本机Edge和Python playwright，只读检查真实样本；保存/重载/安全拒绝测试使用临时数据集。浏览器截图在evaluation/browser_smoke.png。冒烟推理不包含人工真值，不能用其框数量或首轮耗时宣称准确率或速度提升。
