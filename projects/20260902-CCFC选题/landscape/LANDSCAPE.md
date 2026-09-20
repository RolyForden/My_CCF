# Landscape - FocalInspect 根问题重审（2026-09-20）

## 当前任务边界

当前不把“局部重渲染 + global-local fusion + 选择性蒸馏”视为已成立方法，而是先回答一个可证伪问题：语言引导三维 affordance 模型是否真的根据指令改变功能区域预测，还是主要依赖对象类别、几何和 object-affordance 共现先验。

无人机巡检暂不构成核心贡献。只有感知问题成立且方法通过后，才考虑固定下游读出验证。

## 已核实的邻域事实

1. LASO 的 870 个问题由 58 个 object-affordance 组合构造，每个组合 15 个问题；训练随机取 Question1-14，验证/测试固定使用 Question0。官方代码按 `(object_name, affordance)` 查询问题。该协议验证了固定配对下的分割性能，但没有直接提供“保持点云不变、只改变有效指令”的反事实评价。
2. “目标区域尺度不同”不是空白：PointRefer 已用多尺度 Adaptive Fusion Module 处理不同尺度和形状的 affordance region。
3. GEAL 已使用 granularity-adaptive fusion、2D-3D consistency 和多视图 3DGS 表征，并提供 LASO/PIAD 的 seen/unseen 权重和评测代码。因此“全局图分辨率不够，加入局部观察”不能单独构成强 G1。
4. GLANCE 已指出 LASO 方法可能记忆 category-specific cues，并以 VLM 多视图 mask、跨视图一致性和 geometric query 处理 unseen-category affordance grounding。它是“全局语义 + 局部几何”主张的直接强邻居。
5. CMAT 把瓶颈归因于 3D encoder 的 semantic capacity，而非 prompt 数量，并用 2D VFM affinity transfer 学习细粒度功能边界。它进一步压缩了旧 FocalInspect 的新颖性空间。
6. 2025-2026 年邻域已经扩展到 open-vocabulary、multimodal evidence、sequential reasoning、intent-to-part 和 cluttered-scene reasoning；仅增加局部 teacher 或 cross-attention 容易落入已有范式。
7. 相邻视觉语言研究已使用语言扰动、反事实重问和跨任务一致性来揭示 shortcut。该诊断思想存在先例，但尚不能据此断言其在 LASO/GEAL 上成立。

## 候选根问题

> 在 language-guided 3D affordance segmentation 中，标准 object-affordance 配对协议是否足以证明模型使用了指令语义？当同一几何输入对应多个有效功能区域时，模型能否对语义等价改写保持不变，同时对功能相反或不同的有效指令产生正确、可区分的区域变化？

其结构性矛盾不再是“全局看不清局部”，而是：

> 标准平均分割指标可以奖励正确 mask，却不能识别该 mask 是由当前指令决定，还是由对象/几何先验猜中。

以上是由协议与代码事实导出的 **D 级研究假设**，必须通过根问题诊断后才能升级。

## 三条候选路线与裁决

| 路线 | 核心问题 | 当前裁决 | 理由 |
|---|---|---|---|
| A. Counterfactual instruction faithfulness | 同一几何下，模型是否随有效指令正确切换 mask | `SURVIVE_TO_DIAGNOSTIC` | 问题可测、复用 LASO/GEAL、方法可由 failure 推导；但需防 GroundBench/BEACON3D 等反事实评测邻域撞车 |
| B. Global semantic-local precision conflict | 全局语义与局部空间精度是否冲突 | `KILL_AS_PRIMARY` | PointRefer、GEAL、GLANCE、CMAT 已直接覆盖多尺度、语义和细粒度几何；除非表0出现不可被简单替代解释的新现象 |
| C. UAV inspection downstream | 热图是否改善观察位姿与飞行效率 | `HOLD` | 只能证明应用价值，不能抬高感知方法的新颖性；当前投入会扩大工程面 |

## 当前证据缺口

- 尚未统计 LASO 中同一 `shape_id` 拥有两个及以上非同质 affordance mask 的比例。
- 尚未运行 PointRefer、GEAL 或 CMAT 的 null/shuffled/counterfactual prompt 诊断。
- 尚未核实所有 2026 年 3D affordance 工作是否已有同形状反事实配对训练或评价。
- 尚未证明标准指标高分可在不使用问题语义时保持。
- 尚未确定 counterfactual split 是否能由现有标注构造，还是需要少量人工审计。

## 当前结论

旧 FocalInspect-NBV 的“分辨率不足”主张不再作为主线。唯一保留到最小诊断的候选是 **instruction-conditioned counterfactual faithfulness**。它在诊断通过前仍是候选 RQ，不进入 baseline 或方法开发。
