# CCFC 选题

> 目标：CCF-C 会议投稿，硬节点 2027-03 前投出。
> 路线：公开数据 + 可复现代码 + 单卡 RTX 4090 + 不依赖自采硬件。

## 当前状态

- 阶段：`IDEA`（RQ 待按导师意见修订）
- 主攻方向：**FocalInspect-NBV** —— 任务驱动无人机巡检：FocalAfford 感知（语境引导局部教师 + 优势加权局部修正蒸馏 + 2D→3D 迁移）+ 冻结下游观察验证
- 闸门：RQ 的 gap 锋利度须重审（导师意见：重审根问题是分辨率不足还是全局语义—局部空间精度的结构性矛盾）
- 下一步：按导师意见修订 RQ 与 gap，详见 `idea/FocalInspect-NBV_Research_Report.pdf`

## 阅读顺序（第一次看本项目的博士 / 队友）

1. `STATE.yaml` — 机器可读的当前状态
2. `RESEARCH_CHARTER.md` — 研究章程（目标、资源、约束、边界）
3. `idea/FocalInspect-NBV_Research_Report.pdf` — 当前主攻方向的 proposal
4. `DECISIONS.md` — 决策日志（含方向演变摘要，D-022 记录方向切换）
5. `GATE.md` — 选题闸门规则

## 目录

- `intake/` — 背景约束、会议政策、会议纪要
- `landscape/` — 文献矩阵、证据账本、方向地图
- `idea/` — 候选方向与 idea 报告
- `experiments/` — 基线复现与实验注册
- `paper/` — 主张矩阵与写作

## 归档说明

已否定方向与旧实验产物（PACE-PC、跨模态地点检索、点云退化恢复、FocalAfford / FocalLiDAR / FocalAerial、FocalNadir-VO）存放在**独立工作空间**：

```
Z:\科研总控台opencode-archive\
```

该归档**不在本仓库内**，避免污染高频工作空间。需要回溯旧方向细节时到归档工作空间查阅。
