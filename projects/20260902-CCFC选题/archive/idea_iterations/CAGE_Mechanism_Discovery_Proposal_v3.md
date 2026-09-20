# Proposal v3：Language-Guided 3D Affordance Grounding 中的 Query Control 传播机制

> 状态：机制发现型候选 proposal；尚未立项，尚无实验结果。  
> 版本：2026-09-20  
> 工作约定：`CAGE` 仅指 measurement apparatus，不是方法名；正式方法暂不命名、不预设。

## 1. 研究对象已经改变

本 proposal 不再把 `faithfulness evaluation + sensitivity metrics + paired loss` 当作论文主线。研究对象从输出层的“预测是否忠实”转为内部表示链路中的 **query control 如何传播、衰减并最终影响 point-level spatial decision**。

待检验现象是：

> 在三维几何保持不变时，不同有效 affordance query 有时可能无法驱动正确的 point-level mask switching。

内部链路写为：

`q -> E_q -> Fusion(P, E_q) -> Z_point -> Decoder -> Mask`

新的根问题是：

> **Query information 沿上述链路传播时，在哪里失去对空间决策的控制；该位置的信息变化是否对最终 mask switching 具有因果作用？**

“现象存在”“某层发生衰减”和“该层是决定性机制”目前均为 D 级假设，不写成研究发现。

## 2. 核心研究问题

### 主 RQ

> 当有效 query 改变而几何保持不变时，language-guided 3D affordance model 中的 query-dependent representation change 能否被传递到相关 point/token，并驱动正确的 mask switching？若不能，控制能力在何种计算环节丢失？

### 子问题

1. 行为层的 query-insensitive prediction 是否真实存在，且不能由语义歧义、mask overlap、尺度或 paraphrase noise 解释？
2. Query sensitivity 在 text encoding、cross-modal fusion、point representation 和 decoder readout 中如何变化？
3. 观察到的 sensitivity drop 是相关痕迹，还是对 mask switching 必要或具有恢复作用的计算机制？
4. 若机制成立，何种最小结构修改能直接修复该环节，而非泛化地增加监督损失？

## 3. 四个竞争性机制假设

四个假设不是已知事实，也不预设彼此互斥；D1/D2 必须允许多个环节共同失效。

### H1：Query collapse

不同有效 affordance query 在 text encoder 后已经过于相似，后端接收到的条件差异不足。

预期链路特征：`E(q_a) ~= E(q_b)`，且该相似不能仅由 paraphrase invariance 解释。

### H2：Fusion attenuation

Text representation 本来可区分，但经过 cross-modal fusion 后，query-dependent difference 被 geometry/object representation 显著衰减。

预期链路特征：`E(q_a) != E(q_b)`，但 `Z_fusion(P,q_a) ~= Z_fusion(P,q_b)`。

### H3：Point-level conditioning failure

Global multimodal state 随 query 改变，但变化未被路由到与目标功能相关的 point/token。

预期链路特征：global representation 可以解码 query difference；然而 pointwise change 与 GT mask difference 不对齐，相关点没有获得足以改变空间决策的条件信号。

这是优先检查的候选机制，但优先级不等于结论。

### H4：Decoder dominance / geometry shortcut

Query-dependent change 已经进入 point representation，甚至与正确区域切换相关，但最终 decoder 主要读取 geometry foreground prior 或 object-specific affordance prior，再次压低语言差异。

预期链路特征：`Z_point(P,q_a)` 与 `Z_point(P,q_b)` 存在空间对齐的差异，而最终 masks 仍趋同。

## 4. CAGE 的唯一地位：Measurement Apparatus

CAGE 仅提供定位故障所需的受控材料和测量工具：

- **Behaviour probes**：valid swap 为核心；null、shuffle、wrong-object 仅作压力测试。
- **Controlled pairs**：`CAGE-Pair` 用于同 shape 的不同有效 affordance；`CAGE-Para` 用于语义等价控制。
- **Sensitivity measurements**：衡量行为输出和中间表示对 query change 的响应。
- **Alternative-explanation controls**：mask overlap、scale、object class、paraphrase noise 和重复推理噪声。

CAGE 不承担论文核心创新，也不能单独支持“发现机制”的主张。`Counterfactual Swap Margin` 等量只作为仪器读数，不作为贡献本体。

## 5. 证据阶梯

| 层级 | 能支持的表述 | 不能支持的表述 |
|---|---|---|
| E0 行为差异 | 模型在受控 query pair 上未正确切换 mask | 内部哪个模块导致失败 |
| E1 表示关联 | 某相邻阶段之间出现 sensitivity drop | 该阶段是根因 |
| E2 定点干预 | 恢复/破坏该信号相应恢复/破坏 mask switching | 机制跨架构普遍成立 |
| E3 跨模型复现 | 同一计算机制在多个不同架构中成立 | 所有 3D grounding 模型均如此 |

论文的机制主张至少需要 E2。只有 E1 时必须使用 `candidate locus`，不得使用 root cause、causal mechanism 或 decisive bottleneck。

## 6. 四阶段研究设计

### D0 — Behavioural Existence

目标：确认 query-insensitive prediction 确实存在，并排除数据与评测伪象。

1. 审计同 shape 多 affordance 标注，建立语义关系 taxonomy：可区分、共享区域、可并存、蕴含/层级、歧义。
2. 主分析只保留语义有效且预期区域可区分的 pair；mask IoU 只能作几何过滤，不能替代语义判定。
3. 使用 valid query swap 检查 mask switching；null/shuffle 不作为主要存在性证据。
4. 用 paraphrase、尺度、mask overlap、object class 和重复推理噪声排除替代解释。
5. 在查看模型输出前，根据可用样本量、噪声和最小可检测效应冻结裁决标准，不沿用无依据的固定百分比。

**D0 SURVIVE：** 至少两个具有不同融合/解码设计的可复现 baseline，在语义有效 pair 上出现方向一致、置信区间可区分于噪声的 switching failure，且主要替代解释不能解释该现象。

**D0 KILL：** 数据不能构造有效 pair；或强 baseline 均能正确 switching；或 failure 主要由标注歧义、mask overlap、尺度或语言噪声解释。

### D1 — Representation Localization

目标：沿链路寻找 query sensitivity 衰减的候选区间，不宣称因果。

对每个可仪器化 baseline，保存同几何下 `q_a/q_b` 与 paraphrase control 的：

- text encoder 输出；
- fusion 前后 global/token representation；
- 各级 point/token representation；
- decoder 输入、pre-mask logits 与最终 mask。

分析必须同时回答：

1. **Difference exists?** 有效 query change 是否大于 paraphrase 与重复推理噪声？
2. **Difference survives?** 相邻阶段之间 query-dependent difference 是否系统性衰减？
3. **Difference is spatially relevant?** pointwise difference 是否落在两个 GT masks 的差异区域，而非均匀分布或无关点？
4. **Difference is readable?** 简单 readout 是否能识别当前 affordance；readout 成功只说明信息存在，不说明模型实际使用它。

Representation norm、cosine、CKA 或 probe accuracy 均只是分析量。不能用单一距离或训练 probe 的性能直接定位根因。

**D1 输出：** 每个模型的 candidate locus、跨模型一致性、与四个假设的支持/反对证据，以及仍存的替代解释。

### D2 — Causal Intervention

目标：判断 candidate locus 的 query signal 是否实际控制 mask switching。

统一模板：

`Observation -> Intervention -> Behavioural consequence -> Alternative explanation elimination`

#### Restoration direction

在保持几何和非目标路径不变时，通过 architecture-specific activation patching、bypass 或受控 injection 保留/恢复 candidate locus 的 query-dependent component，检查 mask 是否朝正确 counterfactual target 切换。

#### Destruction direction

对原本 switching 正确的样本，equalize、ablate 或替换 candidate locus 的 query-dependent component，检查正确 switching 是否被破坏。

#### 必要控制

- norm-matched random direction；
- paraphrase difference；
- 非候选层的同强度干预；
- geometry representation 的等强度扰动；
- 对原始 aIoU 和非目标区域副作用的检查。

**机制成立的最低条件：** restoration 与 destruction 至少形成方向一致的双向证据，并且效果对目标空间区域具有选择性，不能被简单 norm change、decoder saturation 或整体性能波动解释。

**止损规则：** 若某层 sensitivity drop 明显，但 restoration 不恢复 mask switching，或 destruction 不破坏 switching，则该层只是相关现象，不能围绕它设计方法；继续检查下游/上游环节或终止该机制。

### D3 — Mechanism-Derived Method

D2 通过前，本 proposal 不包含正式方法章节。

D2 通过后，方法必须满足：

1. 修改位置与已验证 candidate locus 一致；
2. 修改的计算作用直接对应已验证机制，而非通用 attention、contrastive learning 或更大 backbone；
3. 先证明内部 query signal 与空间路由恢复，再报告 mask 指标；
4. 用最小非机制性修补、参数量匹配和计算量匹配对照排除“只是容量更大”。

可能涉及 routing、binding、conditional modulation 或 point-query interaction，但这些词当前只表示设计空间，不是预定方案。

## 7. Paired Loss 的进一步降级

原 v2 的 paired loss 定位为 **non-mechanistic intervention control**：

- 若 generic paired supervision 同时恢复内部 sensitivity、空间对齐和 mask switching，则 failure 更可能是 supervision deficiency，不需要声称新的 representation mechanism。
- 若 paired loss 只改善训练/输出指标，却不恢复已定位的 routing/binding signal，则说明普通 loss 修补未解决候选机制。
- 无论结果如何，paired loss 都不是默认正式方法。

## 8. Baseline 选择原则

机制定位至少需要两个可复现且内部结构不同的模型，优先考虑：

- PointRefer：较早的 text-point fusion 起点；尚未在本项目运行。
- GEAL：多视图迁移与 granularity-adaptive fusion；尚未在本项目运行。
- GLANCE/CMAT：只有在官方代码、权重、层级输出和单卡成本审计通过后加入。

Baseline 是否适合不只取决于标准分数，还取决于能否清楚访问 `E_q`、fusion、point representation 和 decoder 输入。黑盒输出只能参加 D0，不能承担 D1/D2 的机制结论。

## 9. 新颖性边界

必须在进入 baseline 前完成最近邻全文主张核验：

- 是否已有工作逐层追踪 3D language grounding 的 query information flow；
- 是否已有 activation patching/bypass 用于 point-level affordance query control；
- GroundBench、BEACON3D、Ref-Adv 等是否已经提出相同的机制定位，而 3D 仅是场景迁移；
- 现有 3D affordance 方法是否已经显式解决 global-to-point query routing 或 query-part binding。

若最终差异仅是“把语言反事实评测迁移到 3D point mask”，G1 KILL。若只在一个具体架构中发现普通实现 bug，降格为架构诊断，不上升为领域机制。

## 10. 总止损条件

1. D0 不成立：停止该题。
2. D1 找不到跨样本稳定 candidate locus：不得硬造机制，最多保留内部分析记录。
3. D2 干预无行为后果：该 locus 不是决定性机制，禁止围绕它写方法。
4. Paired loss 已完整恢复内部链路与行为：优先解释为 supervision deficiency，重新评估论文上限。
5. 机制只在单模型或单 affordance type 成立：缩小主张或停止泛化叙事。
6. 最近邻全文已经覆盖相同定位与干预：G1 KILL。
7. D3 方法只提升 aIoU、不恢复内部 sensitivity 与 switching：不能支持机制论文。

## 11. 当前裁决

**条件保留，研究对象已重置；仍处于 IDEA / PENDING。**

当前唯一允许的主线是：先证明行为 failure，再定位 candidate locus，再用双向定点干预判断因果作用，最后才允许方法从机制中产生。CAGE 是显微镜和手术刀，不是论文主方法；正式方法保持空白。

