# Proposal v2：面向指令因果忠实性的三维功能区域定位

> 工作名：**CAGE-3D（Counterfactual Affordance Grounding and Evaluation in 3D）**  
> 状态：条件式 proposal，等待 D0/D1 根问题诊断；不代表正式立项。  
> 版本：2026-09-20

## 1. 一句话问题

现有 language-guided 3D affordance segmentation 能输出正确热图，但标准 object-affordance 配对评测未必能证明热图由**当前指令**决定；本研究拟用同一几何输入下的语义等价与语义反事实配对，诊断并改善模型的 instruction-conditioned faithfulness。

## 2. 为什么旧 proposal 不成立为强主线

旧方案把问题写成“全局多视图压缩细小区域，因此加入局部重渲染、全局语境和选择性蒸馏”。全文与代码核验后，这条主张面临四个直接覆盖：

- PointRefer 已针对不同尺度和形状做多尺度文本-点云融合。
- GEAL 已做 granularity-adaptive fusion、2D-3D consistency 和多视图迁移。
- GLANCE 已用多视图 VLM mask 和 geometry-aware query 处理目标区域先验。
- CMAT 已从 3D encoder 的 semantic capacity 解释细粒度 affordance 边界。

因此，crop/zoom、cross-attention 和 selective distillation 即使有效，也很难独立构成结构性新问题。无人机闭环只能证明应用价值，不能修复该 G1 缺陷。

## 3. 新的可证伪 RQ

> **RQ：在保持三维几何输入不变时，现有 language-guided 3D affordance 模型能否对语义等价问题保持区域预测不变，并对指向不同真实功能区域的有效问题产生正确、可区分的预测变化？如果不能，如何在不依赖更大语言模型或额外推理模态的条件下，使预测对指令具有可测的反事实忠实性？**

### 子问题

1. 标准 LASO 分数中有多少可以在 null、shuffled 或错误 affordance prompt 下保留？
2. 同一 shape 的不同有效 affordance 问题能否稳定切换到对应 mask？
3. 模型能否同时满足 paraphrase invariance 与 counterfactual sensitivity？
4. 失败主要来自语言 shortcut、几何分辨率，还是 encoder 表征能力？

## 4. 核心科学矛盾

Dense grounding 的输出是 mask，但监督与评价通常逐样本进行。只要对象类别和几何与 affordance 高度共现，模型可能在未充分使用当前指令时仍得到较高平均分。提高 backbone、分辨率或 2D teacher 可能继续提升 mask 质量，却不保证**条件变量真的控制输出**。

本 proposal 把问题从“怎样得到更细的热图”改为：

> **怎样证明并约束语言条件对三维功能区域预测具有因果可辨识的控制作用。**

这仍是待验证假设，不写成已发现事实。

## 5. 诊断先行

首先执行 `FocalInspect_Root_Problem_Diagnostic.md`：

- 数据审计：同 shape 多 affordance pair 是否足量。
- 语言消融：null、shuffle、错误 affordance、错误 object class。
- 双重要求：同义问题保持预测稳定，不同有效问题正确切换区域。
- 尺度排除：按 mask 比例分层，并比较提高分辨率和普通 crop。

诊断未达到 SURVIVE，proposal 自动终止，不开发方法。

## 6. 条件式方法：Paired Counterfactual Grounding

仅当诊断通过时，使用现有 PointRefer 或 GEAL 作为固定主干，加入一个由 failure 直接推出的训练协议，而不是继续堆局部模块。

### 6.1 同几何反事实配对

对同一 `shape_id` 选择两个 GT mask 明显不同的有效 affordance 问题 `(q_a, y_a)` 与 `(q_b, y_b)`。两次前向共享同一几何输入 `P`：

`p_a = f(P, q_a)`，`p_b = f(P, q_b)`。

这样把几何和对象类别固定，只允许指令解释预测差异。

### 6.2 语义等价不变性

LASO 每个 object-affordance 组合已有多种人工/GPT 改写。对同一功能的两个改写约束预测一致：

`L_inv = D(f(P, q_a^1), f(P, q_a^2))`。

该项只要求语义等价问题保持稳定，不鼓励所有问题输出相似 mask。

### 6.3 反事实区分约束

在标准分割损失之外，对正确配对与交叉错误配对建立 margin：

`L_cf = max(0, m - S(p_a,y_a) - S(p_b,y_b) + S(p_a,y_b) + S(p_b,y_a))`。

其中 `S` 是可微 mask 相似度。目标不是增加一个“注意力模块”，而是让同一几何下的预测变化可由指令和 GT pair 审计。

最终目标：

`L = L_seg(a) + L_seg(b) + lambda_inv L_inv + lambda_cf L_cf`。

推理结构不变，不新增传感器、VLM、局部 teacher 或动态选择器。

## 7. 必须比较的简单替代

| 对照 | 排除的解释 |
|---|---|
| 原始 PointRefer / GEAL | 标准起点 |
| 双样本训练但无 `L_inv/L_cf` | 收益是否只是 batch 中看到更多样本 |
| 只做 paraphrase augmentation | 是否普通文本增强已足够 |
| 只做 GT foreground/class reweight | 是否只是 mask 不平衡修正 |
| supervised contrastive text feature | 是否只需文本 embedding 拉近/推远 |
| 提高全图分辨率 / 普通 crop | 是否仍是旧的尺度问题 |
| CMAT（可复现时） | 更强 3D semantic encoder 是否自然解决问题 |

## 8. 数据与划分

### 主数据

- LASO：用于标准 seen/unseen 指标、paraphrase 和同 shape 反事实 pair。
- PIAD：只有在能建立等价语言和同对象多 affordance 映射时作为外部验证；不得直接复用 LASO 文本后宣称独立语言泛化。

### 新评测切片

- `CAGE-Pair`：同 shape、不同 affordance、低 mask overlap。
- `CAGE-Para`：同 shape、同 affordance、不同问题改写。
- `CAGE-Scale`：按 GT foreground point ratio 分桶，仅作机制分层。

所有切片由现有标注确定性生成；若需人工剔除歧义，只允许双人审计并保留排除记录。测试 pair 不参与超参数选择。

## 9. 指标

- 原任务：aIoU、AUC、SIM、MAE。
- 语言必要性：Prompt Reliance Drop。
- 语义等价性：Paraphrase Variance。
- 反事实控制：Counterfactual Swap Margin、Pair Correctness。
- 公平性：按 object class、affordance type、mask ratio、seen/unseen 分层。
- 统计：关键训练配置至少 3 个种子；pair 指标使用按 shape 聚类的 bootstrap CI。

不能用标准 aIoU 上升代替反事实指标成立，也不能用少数可视化样例证明指令忠实性。

## 10. Baseline 与资源

| 方法 | 角色 | 当前可用性 |
|---|---|---|
| PointRefer | 最小 baseline、协议来源 | 官方代码公开；尚未在本项目运行 |
| GEAL | 主 baseline | 官方代码、LASO/PIAD 权重和评测入口公开；尚未在本项目运行 |
| GLANCE | category shortcut 强邻居 | 论文已核；公开代码稳定性待确认 |
| CMAT/LAS | 2026 强 baseline | 官方代码公开；权重和单卡复现成本待审计 |
| Null/shuffle/object-only controls | 必须的非学习对照 | 由统一评测 wrapper 实现 |

先使用官方预训练权重做诊断，不下载无关模态，不启动完整训练。只有 D1 SURVIVE 后才审计单卡训练成本。

## 11. 与最近工作的边界

- 与 LASO/GEAL/GLANCE/CMAT：它们优化准确率、泛化、几何先验或表征；本 proposal 首先审计同几何下的 instruction control。
- 与 BEACON3D/Ref-Adv：借鉴语言扰动与一致性诊断，但输出是 point-level affordance mask，并利用同 shape 的多功能 GT。
- 与 GroundBench：GroundBench 诊断 VLM 的图像 affordance/action shortcut；本 proposal 必须把贡献限定为 dense 3D language-guided affordance segmentation，不宣称首次反事实 affordance 评测。
- 与 ThinkAfford/SegWorld：不宣称首次做 intent reasoning，也不以更大 MLLM 或 scene-level proposal reasoning 为方法主体。

以上边界仍需全文主张级查重后才能通过 G1。

## 12. 止损条件

1. LASO 不足以构造 300 个可靠反事实 pair，停止该题或另找公开数据。
2. PointRefer 与 GEAL 在 prompt swap 下均表现出强语言依赖和高 pair correctness，根问题被否证。
3. 现有 2025-2026 工作已包含同形状、多功能 mask 的等价训练与评价，且本方案没有机制差异，G1 KILL。
4. 新损失只提高标准 aIoU、不提高 CSM/PC，不能支持论文主张。
5. 简单 paraphrase augmentation 或双样本训练解释全部收益，删除复杂方法；若剩余贡献只是一套小评测，重新评估投稿档位。

## 13. 暂缓内容

- 暂不接 FlightBench、Aerial Gym、NBV 或无人机控制。
- 暂不做局部重渲染、优势 teacher 选择或新增 cross-attention。
- 暂不扩展 SceneFun3D；ThinkAfford 已使该路线拥挤。
- 暂不承诺 IJCNN/IROS/PRCV 匹配，会议政策和截止日期需官方核验。

## 14. 当前裁决

**条件保留，未立项。**

相较旧 proposal，本版的改进不是增加模块，而是把论文成败押在一个可诊断的结构问题上：模型输出是否真正受指令控制。它复用 LASO、PointRefer、GEAL 和现有评测资产，但必须先由 D0/D1 证明 failure 存在。诊断失败即停止，不用无人机工程或更多模块补故事。

## 15. 选题红队预审

### 最强反对意见

1. **这可能只是一篇 benchmark audit。** 若训练方法只是通用 contrastive loss，且标准指标不变，方法贡献偏弱。
2. **GroundBench 已抢占“counterfactual affordance shortcut”叙事。** 本工作必须依靠 dense 3D mask、同 shape 多功能 GT 和 point-level counterfactual metric 建立不可替代边界。
3. **数据协议问题不等于模型问题。** 固定 Question0 只是评测设计；只有 null/shuffle/swap 实验失败才能证明 shortcut。
4. **同 shape 的两个 affordance mask 可能并不互斥。** 例如 grasp 与 lift 可以共享区域，错误构造会制造伪反事实。
5. **paired loss 可能是普通 hard-negative training。** 必须与双样本、文本对比学习、GT 重加权和普通 paraphrase augmentation 对照。
6. **强 encoder 可能已经解决问题。** 若 CMAT 在 CAGE-Pair 上自然通过，则新方法缺少必要性，但可留下评测发现。

### 预审结论

`MAJOR REVISION / DIAGNOSTIC REQUIRED`。本版比旧方案的问题更尖，但尚无资格进入 baseline。它的上限取决于三个事实是否同时成立：LASO 有足量真实 pair；至少两个 baseline 暴露一致 failure；该 failure 未被 GroundBench、ThinkAfford 或现有 3D affordance 工作直接覆盖。

## 16. 版本分支

| 版本 | 内容 | 当前建议 |
|---|---|---|
| v2-A：Evaluation-first | 只构建 CAGE-Pair/CAGE-Para 与诊断协议 | 若 failure 强但方法收益弱，可保留为低成本评测论文候选 |
| v2-B：Paired learning | 诊断协议 + `L_inv/L_cf`，推理结构不变 | **推荐条件版**；只有 v2-A 证实 failure 后启动 |
| v2-C：Local zoom/distillation | 回到局部重渲染与修正蒸馏 | 不推荐；邻域覆盖强，除非 D2 给出新的不可替代机制证据 |
