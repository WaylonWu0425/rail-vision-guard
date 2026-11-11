"""Validate paired snapshots before reporting a fixed-model comparison."""
import argparse
from pathlib import Path

from workbench import read,write


def summarize(root):
    protocol=read(root/'comparison_protocol.json')
    environment=read(root/'environment.json')
    runs={name:read(root/'runs'/name/'summary.json') for name in protocol['jobOrder']}
    for split in ('tune','test'):
        for strategy in protocol['strategies']:
            baseline=read(root/'runs'/('baseline_'+split)/(strategy+'.json'))
            candidate=read(root/'runs'/('candidate_'+split)/(strategy+'.json'))
            left={r['id']:r for r in baseline}
            right={r['id']:r for r in candidate}
            if set(left)!=set(right):
                raise ValueError('Mismatched comparison samples')
            for key in left:
                if left[key]['annotation']!=right[key]['annotation'] or left[key]['imageSha256']!=right[key]['imageSha256']:
                    raise ValueError('Mismatched truth/image snapshot: '+key)
    for name,data in runs.items():
        kind='baseline' if name.startswith('baseline') else 'candidate'
        if data['modelSha256']!=protocol[kind]['sha256'] or data['confidence']!=protocol['confidence'] or data['device']!=protocol['device']:
            raise ValueError('Comparison conditions differ from protocol')
    write(root/'paired_comparison.json',dict(protocol=protocol,snapshotsVerified=True,runs=runs,activated=False))
    lines=['# 环境核查与固定候选模型对照','',
           '本轮仅在隔离目录进行本地离线评测，未训练、未改原best.pt、未安装CUDA/驱动、未改默认服务策略、未修改人工标注。',
           '', '## 1. 已核实的运行条件','',
           f"- 当前解释器：{environment['python'].splitlines()[0]}；PyTorch {environment['torch']}；Ultralytics {environment['ultralytics']}。",
           f"- 内存可见总量约{environment['memoryBytes']/1024**3:.2f} GiB，逻辑处理器{environment['logicalCores']}。",
           f"- NVIDIA硬件/驱动：{environment['nvidiaSmi']}。",
           '- 当前torch.version.cuda为空、cudaAvailable=false，证明这套评测环境只用CPU，不代表电脑没有独显。备用Python 3.12环境检查时缺少torch与ultralytics，且无.gpu-ready标记。',
           '- 原权重为两类别person/car，训练元数据指向yolov8n.pt；候选YOLO11n是官方COCO预训练权重。两者训练数据和权重也不同，不能将效果差异仅归因于模型架构或版本。',
           '', '## 2. 配对评测约定','',
           '事前固定CPU、FP32、640/1280两种输入、置信度0.45、IoU匹配0.5、预热1次及每图3次计时；四个任务顺序执行，不并行争用CPU。按类别名person评分，不直接复用类别ID。原模型car=1，候选car=2，不能在正式系统盲目沿用数字映射。',
           '', '两模型的逐图图片哈希、人工框快照和样本ID已配对核对一致。44张诊断图此前已查看，不是全新盲测；40张调参图均无人。以下均为本批场景结果，不能外推新站点、估计整体系统准确率或宣称现场落地效果。',
           '', '## 3. 44张人员/背景诊断图（79个人员框）','',
           '| 模型 | 输入 | TP | FP | FN | 精确率 | 召回率 | 推理中位数 | P95 |',
           '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for kind,label in [('baseline','现有best.pt'),('candidate','官方YOLO11n')]:
        for strategy in protocol['strategies']:
            s=runs[kind+'_test']['summaries'][strategy]
            lines.append(f"| {label} | {strategy} | {s['tp']} | {s['fp']} | {s['fn']} | {s['precision']:.1%} | {s['recall']:.1%} | {s['medianMs']:.1f} ms | {s['p95Ms']:.1f} ms |")
    lines+=['','FP是未匹配人工框的人员预测；仍需区分真实背景误报、漏标和定位差异。推理耗时不含摄像头、告警写库与浏览器链路。','',
            '## 4. 40张无人调参图（单独报告）','','| 模型 | 输入 | 人员误框数 | 推理中位数 |','| --- | --- | ---: | ---: |']
    for kind,label in [('baseline','现有best.pt'),('candidate','官方YOLO11n')]:
        for strategy in protocol['strategies']:
            s=runs[kind+'_tune']['summaries'][strategy]
            lines.append(f"| {label} | {strategy} | {s['fp']} | {s['medianMs']:.1f} ms |")
    lines+=['','无人负例没有人员真值，不能计算人员召回率；无预测也不能写为“准确率100%”。不把此组与诊断组混成一个测试分数。','',
            '## 5. 来源、许可与边界','',
            '- [官方YOLO11说明](https://docs.ultralytics.com/models/yolo11/)列出COCO预训练检测权重及80类别。这里只验证person，不把80类别宣传为系统已实现功能。',
            '- [官方权重仓库](https://huggingface.co/Ultralytics/YOLO11)：下载固定revision的yolo11n.pt并匹配官方LFS SHA-256，详见candidate/provenance.json。GitHub API限流403后使用此官方渠道，未使用第三方镜像。',
            '- [发布方许可说明](https://www.ultralytics.com/license)：提供AGPL-3.0及Enterprise路径。免费获取不等于无条件闭源商用；正式分发、网络部署、合作方交付前应按具体使用方式核对完整条款，必要时寻求专业意见。本轮不购买许可、不替用户公开源码或作合规保证；既有Ultralytics方案同样需要核查。',
            '', '## 6. 上线前未完成事项','',
            '本轮activated=false。原有高度<32像素GT验证门槛仍不可用，未做实机30分钟稳定性与录像关联回归；不能通过本轮诊断自动宣布验收通过。GPU安装与CUDA推理未实施。若候选更好，仅可作为下一阶段受控枪机测试的候选；如无改善，保留现方案。',
            '', '配对证据见paired_comparison.json及runs下四组逐图预测/标注快照；环境见environment.json、candidate_metadata.json。']
    (root/'环境核查与候选模型对照.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Paired snapshots verified; report written; production unchanged')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--audit-dir',type=Path,required=True)
    summarize(parser.parse_args().audit_dir)
