# FocalInspect 根问题诊断预注册草案

> 状态：实验前设计；无结果。执行前必须由用户 checkpoint 确认，并冻结数据版本、代码 commit、随机种子和阈值。

## 1. 诊断目标

区分三个解释：

- `H_scale`：失败主要来自小功能区域和有限空间分辨率。
- `H_shortcut`：模型主要利用对象类别、几何或 object-affordance 共现，而非当前问题语义。
- `H_conditional`：模型确实使用语言，但无法同时做到“对同义改写不变”和“对不同有效意图敏感”。

根问题诊断优先于任何新模块。旧 proposal 的局部重渲染只作为 `H_scale` 的简单干预，不是默认答案。

## 2. D0：数据可诊断性审计（不训练）

对 LASO 的 train/val/test 标注执行：

1. 按 `shape_id` 聚合 annotation。
2. 统计每个 shape 的 affordance 数量、mask 两两 IoU、前景点比例和 object class。
3. 保留同一 shape 下至少两个有效 affordance、且两 mask IoU 小于 0.5 的 pair。
4. 检查 pair 是否跨 split、是否存在同 shape 泄漏；任何跨 split 重复单独报告。
5. 统计 15 个问题改写的词汇重合、是否显式出现对象名/部件名/动作词。

**可行性门槛**：test 中至少 30% 的 shape 能形成上述 pair，且总 pair 数不少于 300；否则不把 LASO 作为反事实主数据，候选 RQ 退回。

## 3. D1：无训练 prompt reliance 诊断

使用官方预训练 PointRefer 和 GEAL；CMAT 仅在官方权重与入口可复现时加入。

| 条件 | 点云 | 问题 | 用途 |
|---|---|---|---|
| P0 | 原始 | 官方 Question0 | 标准起点 |
| P1 | 原始 | 空字符串/中性句 | 测试语言是否必要 |
| P2 | 原始 | batch 内随机问题 | 测试几何/类别先验 |
| P3 | 原始 | 同 object class 的错误 affordance 问题 | 强反事实 prompt swap |
| P4 | 原始 | 同 affordance 的 Question1-14 | 测试 paraphrase invariance |
| P5 | 原始 | 正确 affordance、错误 object class 表述 | 分离对象词与动作词依赖 |

除官方指标 aIoU/AUC/SIM/MAE 外，增加：

- `Prompt Reliance Drop (PRD)`：`1 - score(P1/P2) / score(P0)`。
- `Paraphrase Variance (PV)`：同一样本 15 个同义问题预测的点级方差与指标方差。
- `Counterfactual Swap Margin (CSM)`：正确配对相似度之和减去交叉错误配对相似度之和。
- `Pair Correctness (PC)`：CSM 大于 0 的反事实 pair 比例。

所有阈值在读取模型输出前冻结。

## 4. D2：尺度解释排除

按 GT 前景点比例分桶，并在同一 baseline 上比较：

- 原始输入；
- 提高全图渲染分辨率；
- 普通固定 crop/zoom；
- 仅改变 prompt，不改变视觉输入。

使用回归或分层 bootstrap 同时控制 object class、affordance type 和 split。若性能只随前景比例下降，且简单分辨率干预恢复，则支持 `H_scale`；若 prompt swap 在相同几何和尺度下仍导致错误不切换，则支持 `H_shortcut/H_conditional`。

## 5. 预注册裁决

### SURVIVE

至少两个可复现 baseline 同时满足以下任一组：

1. P1/P2 保留 P0 至少 80% 的 aIoU，且 PC 不高于 60%；或
2. P3 的 CSM 95% bootstrap 置信区间包含 0，且该失败不能由 mask 高重合解释；或
3. PV 超过同模型重复推理方差的 2 倍，并在至少 3 个 affordance type 上复现。

### WEAK

现象只在一个模型、一个类别或极少 pair 上成立；允许一次数据无关修正后复验。

### KILL

PointRefer 与 GEAL 都表现出明确语言依赖：P1/P2 相对下降超过 30%，PC 超过 75% 且 CSM 的 95% 置信区间严格大于 0；或 D0 无法构造足量反事实 pair。

## 6. 输出与审计

- 原始逐样本预测，不只保存汇总表。
- pair 构造清单、排除理由和 hash。
- 固定脚本生成全部指标和图，不手工挑样例。
- 负结果进入 `DECISIONS.md`。
- D0/D1 完成前不训练新方法，不接 FlightBench/Aerial Gym。
