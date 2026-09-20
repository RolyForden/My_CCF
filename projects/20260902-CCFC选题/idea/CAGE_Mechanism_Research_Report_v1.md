# CAGE v1：Query Control 在三维功能区域定位中的传播、衰减与因果定位

> CAGE: Causal Analysis of Grounding and Encoding
> 研究方案报告 - 修订版
> 版本：v1，2026-09-20（相对 v0 的关键修订见 §0）
> 状态：IDEA / PENDING；无实验结果；正式方法保持空白

## 0. 相对 v0 的关键修订

本版不改 v0 的机制发现框架（H1–H4、E0–E3、D0–D2），只补上五个 v0 缺失的立项要件。对应关系：

| # | v0 的问题 | v1 的修订 | 依据边界 |
|---|---|---|---|
| 0.1 | 论文"卖什么"空缺（三重否定锁死） | §1 补唯一贡献 + §2 成果形态树 | 全网经验汇编「一篇论文一个贡献」 |
| 0.2 | 数据前提未验证，D0 缺 pair 数硬阈值 | §6 补 0 号动作：数据可行性审计 | 博士规则「20% 子集先验存活」「先单样本」 |
| 0.3 | H3 与 STDC back-patching 撞车，无不可替代判据 | §5 补三条不可替代判据 | 导师选题思路「reviewer 连环问」 |
| 0.4 | 三套框架 hook 工程量黑洞，无退路 | §8 补两模型主线 + 第三模型退路 | 博士规则「开源 baseline」「周期可控」 |
| 0.5 | 形态违背博士八股文，未让导师拍板 | §11 补待裁决清单，形态冲突列为第一项 | 博士规则「模型名+冒号」「三贡献点」 |

## 1. 唯一贡献（v0 缺失，本版补上）

本论文只卖一个贡献，写成一句话：

> **在 dense language-guided 3D affordance grounding 中，用同一几何、不同有效功能 mask 的天然对照，因果定位「query control 在哪一步失去对 point-level 空间决策的控制」，并给出该环节的最小机制修复。**

它的三个子点（对应博士"三个贡献点"，是一个贡献的三个子点，不是三个独立贡献）：

1. **行为存在性证据**（E0–E1）：受控 pair 上存在 query-insensitive prediction，且排除语义歧义、mask overlap、尺度、paraphrase 噪声。
2. **因果定位 apparatus**（E2）：CAGE 的双向定点干预（restoration/destruction）定位候选环节，并证明其因果作用。
3. **机制结论 + 最小修复**（E3–D3）：被定位机制跨至少两个架构复现，且最小结构修改（非通用 loss）能恢复 query control。

如果 D2 只到 `CORRELATE-ONLY`，则贡献退化为第 1 子点（一套评测协议），形态见 §2。**无论哪种结果，贡献不再空缺。**

## 2. 成果形态树（v0 缺失，本版补上）

把"这篇论文长什么样"按诊断结果分情形写死，消除"方法推迟到 D2 后、成果形态悬空"的死穴：

| 情形 | 论文形态 | 唯一贡献 | 投稿档位预估 |
|---|---|---|---|
| D2 → MECHANISM-SURVIVE | 机制发现 + 最小修复方法 | 被定位机制 + 由机制推出的修复 | CCF-C 主投 |
| D2 → CORRELATE-ONLY | 诊断评测论文 | CAGE-Pair/CAGE-Para 协议 + 行为存在性发现，不宣称机制 | 降档 / 审慎投 |
| D1 → 无稳定 locus | 现象报告 | 行为存在性 + 失败切片，不宣称机制 | 大概率不投，转内部记录 |
| D0 → KILL | 无 | 无 | 停止 |

**关键结论：只要 D0 与 D1 有 SURVIVE，即使 D2 失败，也有一篇"诊断评测"论文兜底。** 这是 v0 缺的"退路"。

## 3. 研究对象与根问题（沿用 v0）

待检验现象：同一几何下，不同有效 query 有时无法驱动正确的 point-level mask switching。

链路：`q -> E_q -> Fusion(P, E_q) -> Z_point -> Decoder -> Mask`

根问题：

> Query information 沿链路传播时，在哪里失去对空间决策的控制；该位置的信息变化是否对最终 mask switching 具有因果作用？

措辞注意：研究对象是 **query control 的传播与衰减**，不是"置信度、可信、风险校准、拒识"。后者是博士红线，本方案不触碰。

## 4. 四个竞争性机制假设（沿用 v0，略）

- H1 Query collapse：`E(q_a) ~= E(q_b)`，text encoder 后条件差异不足。
- H2 Fusion attenuation：`E(q_a) != E(q_b)` 但 `Z_fusion` 后差异被 geometry 淹没。
- H3 Point-level conditioning failure：global state 随 query 变，但未路由到相关 point/token（当前优先检查，非结论）。
- H4 Decoder dominance：`Z_point` 已含对齐差异，decoder 却读 geometry prior 使 mask 趋同。

四个假设不预设互斥；D1/D2 允许多环节共同失效。

## 5. H3 与最近邻的不可替代判据（v0 缺失，本版补上）

STDC（NeurIPS 2025）已提出"信息到得太晚、无法影响后续位置"，与 H3 抽象叙事接近。为避免 reviewer 一句"不就是把 causal tracing 搬到 3D 小模型"，本版预写三条不可替代判据，D1 时必须逐条验证：

1. **point-level spatial selectivity**：本方案考察的是 query-dependent signal 是否路由到 `y_a XOR y_b` 的**具体点集**，并测量其空间选择性；STDC 的 back-patching 是 token/circuit 级，不验证 dense 3D 点的空间对齐。
2. **同几何多 affordance 的天然对照**：本方案用同一 shape 的多功能 mask 作受控对照，不引入"clean/corrupt"的对抗输入；STDC 的跨模态差距不建立在"同一几何、多个有效 GT"这一 affordance 特有结构上。
3. **affordance mask switching 的后果**：本方案的行为后果是 point-level mask switching（安全相关：选错功能区域即事故），不是分类 token 的标签翻转。

若这三条在 D1 中一条都不成立，则 novelty 判 WEAK/KILL，不进入 baseline。

## 6. 0 号动作：数据可行性审计（v0 缺失，本版补上并前置）

在 D0 之前，先执行一次不运行模型的数据审计，回答"数据能否支撑这个 RQ"。这是所有讨论的前提。

**硬门槛（预注册，看模型输出前冻结）**：

- test 中至少 30% 的 shape 能形成「同 shape、≥2 个有效 affordance、两 mask IoU < 0.5」的 pair；
- 且总 pair 数 ≥ 300。

> 注意：v2 曾写死 300/30%，SCREENING 的 M1 已指出其无依据。本版把 300/30% 降为**初始操作阈值**，并强制在审计后按"真实 pair 数 + 官方模型重复推理方差"推导最小可检测效应，再冻结最终阈值。阈值必须有依据，不能在看结果后改，也不能无依据写死。

产出：`pair_inventory.parquet`、`pair_semantic_audit.csv`、`excluded_pairs.csv`、`dataset_summary.json`、`data_hashes.json`。

**KILL 条件**：pair 数远低于阈值，或同 shape 多 affordance 的 mask 普遍高重叠、无法构成有效反事实。此时停止，不再投入 D1。

## 7. 证据阶梯（沿用 v0）

| 层 | 能支持 | 不能支持 |
|---|---|---|
| E0 行为差异 | 受控 pair 上未正确切换 | 内部哪一步导致 |
| E1 表示关联 | 相邻阶段 sensitivity drop | 该阶段是根因 |
| E2 定点干预 | 恢复/破坏信号相应恢复/破坏 switching | 机制跨架构普遍 |
| E3 跨模型复现 | 同一机制在多架构成立 | 所有模型均如此 |

机制主张至少需要 E2；只有 E1 时只能称 `candidate locus`，不得称 root cause / causal mechanism。

## 8. Baseline 与 hook 退路（v0 缺失退路，本版补上）

**主线：两个内部结构不同的可复现模型 = PointRefer + GEAL。** 两模型足以支撑 E2 主结论（机制主张要求"至少一个第二架构的同类路径证据"）。

**第三模型（CMAT/GLANCE）是 E3 的充分条件，不是 D2 的必要条件。** 若其官方权重/hook 入口审计不过，不影响主线推进，只影响 E3 的普遍性宣称——此时把结论限定为"两架构成立"，不宣称领域普遍机制。

hook 入口优先级：text encoder 输出 > fusion 前后 > point representation > decoder 输入。黑盒输出只能参加 D0，不能承担 D1/D2 的机制结论。

## 9. D0/D1/D2 裁决（沿用 v0，补 pair 阈值）

- D0 SURVIVE：至少两个结构不同的 baseline 在语义有效 pair 上出现方向一致、置信区间可区分于噪声的 switching failure，且主要替代解释（mask overlap、尺度、class、paraphrase）不能解释。
- D0 KILL：数据不能构造有效 pair（见 §6 阈值），或强 baseline 均能正确 switching，或 failure 由数据歧义/重叠/尺度/语言噪声解释。
- D1：定位 candidate locus，不宣称因果；输出跨模型一致性 + 四个假设的支持/反对证据 + 残留替代解释。
- D2：restoration + destruction 双向干预 + 必要控制（norm-matched random、paraphrase、非候选层同强度、geometry 等强度、aIoU 副作用）。`MECHANISM-SURVIVE` / `CORRELATE-ONLY` / `ARCHITECTURE-SPECIFIC`。
- D3：D2 通过前不写方法；通过后方法必须（a）修改位置与已验证 locus 一致，（b）计算作用对应已验证机制而非通用 attention/contrastive/大 backbone，（c）先证明内部 signal 恢复再报 mask 指标，（d）用最小非机制修补 + 参数量/计算量匹配对照排除"只是容量更大"。

## 10. 总止损条件（沿用 v0）

1. D0 不成立（含数据 pair 不足）→ 停止。
2. D1 无跨样本稳定 locus → 不硬造机制。
3. D2 干预无行为后果 → 该 locus 非决定性机制，禁止围绕它写方法。
4. generic paired loss 已完整恢复内部链路与行为 → 解释为 supervision deficiency，重估上限。
5. 机制只在单模型/单 affordance type 成立 → 缩小主张或停止泛化。
6. 最近邻全文已覆盖相同定位与干预 → G1 KILL。
7. D3 方法只提 aIoU、不恢复内部 sensitivity 与 switching → 不支持机制论文。

## 11. 待导师裁决清单（v0 缺失，本版补上）

按优先级，前两项是 CAGE 能否立项的前提：

1. **论文形态**：是否接受"机制发现 / causal localization"论文形态（违背博士"模型名+冒号、三贡献点、方法论文"八股文）？还是必须回到"方法 + 三贡献点"？（若否，CAGE 需重新包装成方法论文，或放弃）
2. **兜底成果**：若 D2 只到 CORRELATE-ONLY，接受"诊断评测论文"作为兜底形态吗？（这决定 §2 形态树是否成立）
3. **数据审计优先级**：同意把"0 号动作：LASO pair 数统计"作为 D0 之前的第一动作吗？
4. **pair 阈值**：300/30% 作为初始操作值是否可接受，还是导师另有依据？

## 12. 当前裁决

**条件保留，未立项。** 相对 v0 的修订不改变机制发现主线，只补齐唯一贡献、成果形态树、数据硬阈值、不可替代判据、hook 退路和待裁决清单。§11 前两项未获导师裁决前，不进入 D0，不写方法，不下载数据、搭环境或训练模型。
