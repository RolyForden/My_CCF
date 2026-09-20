# CCFC 选题

> 目标：CCF-C 会议投稿，硬节点 2027-03 前投出。
> 路线：公开数据 + 可复现代码 + 单卡 RTX 4090 + 不依赖自采硬件。

## 当前状态

- 阶段：`IDEA`（立项决策）
- 主攻方向：**FocalNadir-VO** —— 高空俯视无人机单目视觉里程计，训练期平面运动归一化局部细节学习
- 闸门：`G1 = WEAK+`（须用表0 决定是否 SURVIVE）；G0/G2/G3/G4/G5 已通过
- 下一步：**表0 止损实验**（A0–A4 无训练信息增量 + B0–B3 短训练），详见 `idea/FocalNadir-VO.md`

## 阅读顺序（第一次看本项目的博士 / 队友）

1. `STATE.yaml` — 机器可读的当前状态
2. `RESEARCH_CHARTER.md` — 研究章程（目标、资源、约束、边界）
3. `idea/FocalNadir-VO.md` — 当前主攻方向的立项决策书
4. `DECISIONS.md` — 决策日志（含方向演变摘要）
5. `GATE.md` — 选题闸门规则

## 目录

- `intake/` — 背景约束、会议政策、会议纪要
- `landscape/` — 文献矩阵、证据账本、方向地图
- `idea/` — 候选方向与 idea 报告
- `experiments/` — 基线复现与实验注册
- `paper/` — 主张矩阵与写作

## 归档说明

已否定方向与旧实验产物（PACE-PC、跨模态地点检索、点云退化恢复、FocalAfford / FocalLiDAR / FocalAerial）存放在**独立工作空间**：

```
Z:\科研总控台opencode-archive\
```

该归档**不在本仓库内**，避免污染高频工作空间。需要回溯旧方向细节时到归档工作空间查阅。
