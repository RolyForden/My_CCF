# Proposal v2 边界筛查报告

> 筛查对象：`FocalInspect_Proposal_v2.md` 与 `FocalInspect_Root_Problem_Diagnostic.md`  
> 判定边界：`docs/08_科研决策、Gap判断与论文实操汇编.md`
> 日期：2026-09-20  
> 性质：立项前红队审计，不是实验结果；所有分数均为审稿视角的 D 级判断。

## 1. 总裁决

**REVISE，暂不进入 baseline，也不应把 v2 原样当成 D0/D1 的最终预注册。**

v2 已经通过旧方案没有通过的第一层测试：它不再用无人机下游抬高视觉方法，也不再把 crop、cross-attention、蒸馏当作结构问题；它提出了一个可被否证的现象，并写明诊断失败即停。这个方向变化符合“先发现可量化 failure，再由机制推出方法”的边界。

但它还没有通过立项要求的第二层测试：**根问题的概念边界、数据构造效度和最近邻 novelty 尚未闭合，方法形式却已经提前落到 paired loss。** 当前更像“有潜力的诊断议题 + 一个自然的通用正则项”，还不是已经站住的 CCF-C 选题。

## 2. 阻断级问题

### C1. “因果可辨识”超出了当前设计能支持的主张

- v2 用同一几何下的 prompt 替换测试条件依赖，这是有价值的受控干预；但它没有给出因果图、可交换性假设、干预分布定义或混杂控制，不能据此声称“因果可辨识”。
- null、shuffle、错误 object prompt 还可能是分布外输入。输出变化既可能来自真实指令控制，也可能来自语言编码器对异常句子的脆弱性；输出不变化也可能来自提示格式失配，而非对象先验。
- 这会触发“题目包装高于证据”的拒稿点，也容易被误读为项目红线中的泛化“可信/忠实”方向。

**必须修正：** 在建立正式因果识别设计前，统一降格为 `instructional dependence`、`counterfactual sensitivity` 或“指令条件依赖”；明确本题不是置信度、拒识、风险校准。核心证据应优先来自同分布、语义最小变化的有效 prompt pair，null/shuffle 只作压力测试。

### C2. RQ 同时问“failure 是否存在”和“怎样用既定方法修复”，仍有先箭后靶痕迹

- 当前 RQ 前半是诊断，后半已问如何改善；随后方法立即落到 `L_inv + L_cf`。去术语后仍可被概括为“换问法应不变，换任务应改变，所以加一致性与排序损失”。
- 这正对应 gap 锋利度文档的去术语测试：如果每一步都容易想到，方法本身不是结构性机制。现有简单对照很多，也反向说明 proposal 正在防守“是不是普通 hard-negative / augmentation”，而不是已经证明该损失不可替代。

**必须修正：** 拆成 `RQ0：标准评测是否低估了模型对指令的不敏感？` 与条件式 `RQ1：若 RQ0 成立，哪一种机制缺陷导致它，最小干预是什么？`。D0/D1/D2 只能决定 RQ1，不得预先锁定 paired loss。若 paired loss 只是最好用的工程修复，应诚实定位为增量方法，不再称新机制。

### C3. 最近邻查重仍未达到立项证据标准

- v2 已主动承认 GroundBench 抢占了 counterfactual affordance shortcut 叙事，并列出 BEACON3D、Ref-Adv、ThinkAfford、SegWorld；但当前仍写明“需全文主张级查重”。
- 博士规则要求高度相关工作读取方法、实验和结论，形成 Similarity/Threat 与 Top-10 最近邻；仅凭任务载体从 2D/VLM 换成 dense 3D，可能是“题目新颖，不等于方法新颖”。
- 在最近邻边界未闭合前，无法判断这是“刚开始有人碰”的合适窗口，还是 GroundBench 思路的 3D 迁移。

**必须修正：** 至少把 GroundBench、BEACON3D/Ref-Adv、最接近的 3D affordance 工作提升到 A 级主张核验；逐篇回答“审稿人为什么不能说只是换成 3D point mask”。若唯一差异仍是数据模态与 mask 粒度，novelty 判为 WEAK/KILL。

### C4. `CAGE-Pair/CAGE-Para` 的构造效度尚不足，可能人为制造 failure

- 同一 shape 的 affordance mask 不互斥；grasp、lift、hold 等关系可能重叠、蕴含或共享部件。仅用 mask IoU 阈值不能证明两个问题构成语义反事实。
- LASO 的多问题改写是否都严格语义等价、是否泄露对象/部件/动作词，目前没有人工一致性或语义关系审计证据。
- 若 pair 定义不稳，CSM/PC 低只能证明切片有歧义，不能证明模型没有使用语言。

**必须修正：** 在 D0 前先冻结关系 taxonomy：互斥、可并存、蕴含/层级、共享区域、歧义；主分析只纳入“有效且预期区域可区分”的 pair。给出双人标注一致性、排除规则和盲审流程。IoU 只作几何过滤器，不能替代语义判定。

## 3. 重大但可修问题

### M1. 诊断阈值是预先写死的，但没有依据

`300 pairs`、`30% shapes`、`保留 80% aIoU`、`PC 60%/75%` 等阈值目前没有来自数据规模、重复推理方差、效应量或 power analysis 的依据。提前冻结能防止看结果改规则，却不能自动让规则科学。建议先用数据结构和官方模型重复推理噪声定义最小可检测效应；裁决以置信区间与跨模型一致性为主，固定百分比只作操作阈值并说明来源。

### M2. 论文的“唯一贡献”尚未选定

v2 同时包含新 failure、三套评测切片、多项指标和 paired training；v2-A 与 v2-B 实际是两种论文身份。按照“一篇论文只卖一个贡献”，当前应把唯一贡献暂写成：

> **一套能区分几何先验与真实指令控制的 dense 3D affordance 配对评测原则。**

只有当诊断成立且通用增强无法修复时，方法才可成为主贡献；否则不要同时把 benchmark、metric、loss 都包装成独立创新。

### M3. significance 仍回答了“怎么测”，没有完全回答“为什么值得测”

“模型是否受指令控制”直觉上重要，但 proposal 尚未指出错误控制会导致哪类已有任务结论失效、谁会复用该评测、为什么标准 aIoU 无法替代它。无需重新接无人机；应给一个同物体、多有效动作却要求不同区域的具体失败例子，并说明这会怎样误导模型比较或下游决策。应用例子用于解释意义，不得冒充方法贡献。

### M4. baseline 与单卡资源闭环未完成

PointRefer/GEAL 可作为诊断起点，但 GLANCE 代码稳定性、CMAT 权重与单卡成本仍未知，也没有训练时间/显存/存储预算表。规则要求开源 baseline、较新 baseline 和单卡周期可控。D1 可以先用官方权重；任何新训练开始前必须明确主 baseline、强 baseline、训练预算和失败时的降档路线。

### M5. 外部有效性偏弱

LASO 同时提供问题改写和标注，PIAD 又不能在复用 LASO 文本后被称为独立语言泛化。若最终只有单数据集内部切片，审稿人可能把结论限定为“LASO 的问句协议缺陷”。需要在立项时就区分：数据集审计结论、模型机制结论、跨数据集结论；不能从前者跳到后两者。

### M6. 对照项需要分层，避免再次落入“用大量消融证明不 trivial”

当前简单替代是必要的，但用途混在一起：null/shuffle 属于识别性诊断，crop/resolution 属于竞争解释，augmentation/contrastive 属于方法基线。建议分成三张表，并为每张表写一个唯一判定问题。这样保留严谨性，同时避免一长串防御性消融遮住主问题。

## 4. 已经做对的部分

1. **问题导向明显增强。** 先诊断 failure、再决定方法，符合“先有靶再射箭”。
2. **没有用下游工程抬高方法。** 暂缓 FlightBench/Aerial Gym，边界正确。
3. **证伪条件写得较诚实。** 数据不足、baseline 不失败、最近邻覆盖、简单增强解释收益都允许 KILL。
4. **关键简单基线意识合格。** 双样本、paraphrase augmentation、GT reweight、强 encoder 都能排除替代解释。
5. **复现与统计意识较完整。** 保留逐样本输出、按 shape 聚类 bootstrap、测试集不调参，符合 Quality/Soundness 要求。

## 5. 边界逐项判定

| 边界 | 当前判定 | 原因 |
|---|---|---|
| 方向红线 | `PASS WITH WARNING` | 不是置信度/拒识，但“忠实性”必须限定为输入条件依赖 |
| 一句话 gap | `WEAK-SURVIVE` | 能说清，但 failure 尚未被实证，且“因果”表述过强 |
| 结构性矛盾 | `PENDING` | 若多个强 baseline 在同分布有效 pair 上失败才成立 |
| 去术语测试 | `WEAK` | paired consistency + ranking loss 仍非常自然 |
| 最近邻查重 | `FAIL` | closest work 尚未完成 A 级主张核验 |
| 数据可诊断性 | `FAIL` | pair 数量、语义关系和 paraphrase 等价性未核验 |
| 单卡可行性 | `PENDING` | 诊断低成本，但方法训练预算未闭合 |
| 单一贡献 | `FAIL` | benchmark/metric/method 三种身份尚未收束 |
| 应用层边界 | `PASS` | 未用无人机验证冒充方法创新 |
| 止损设计 | `PASS` | 有明确 KILL 与收缩路线 |

## 6. 审稿视角暂评分

| 维度 | 分数 | 说明 |
|---|---:|---|
| Soundness | 2/4 | 有预注册骨架，但 causal claim、OOD controls、pair validity 未闭合 |
| Presentation | 3/4 | 结构清楚，术语仍把证据强度抬高了一档 |
| Contribution | 2/4 | 问题可能重要，但最近邻边界与唯一贡献未定 |
| Novelty | 5/10 | 3D dense setting 有差异，机制仍像通用 paired loss |
| Significance | 5/10 | 尚未证明 failure 普遍且会改变现有结论 |
| Technical feasibility | 7/10 | 诊断与损失实现本身可控 |
| Experimental feasibility | 6/10 | 受 pair 数量、强 baseline 和外部数据限制 |
| Incremental risk | 8/10 | 最大风险是“GroundBench 思路的 3D 迁移 + 普通 hard negative” |

按博士规则“Novelty 或 Significance 低于 6 原则上淘汰”，**当前不能判 SURVIVE**。这不是终局否定，而是说明 v2 还缺决定生死的证据。

## 7. 唯一推荐的最小下一步

**先做一个不运行模型的“v2.1 立项前收口包”，再决定是否执行 D0。** 该收口包只包含四项：

1. 把“因果忠实性”降为可被当前设计支持的“指令条件依赖/反事实敏感性”。
2. 将 RQ0 诊断与 RQ1 方法彻底拆开，删除对 paired loss 的预承诺。
3. 完成最近邻 A 级主张表，给出 3D dense setting 不是简单场景迁移的必要差异。
4. 冻结 pair 语义 taxonomy、同分布控制和有依据的裁决规则。

这四项如果无法同时收口，直接 KILL；如果能收口，再进入 D0 数据可诊断性审计。当前不建议写论文骨架、下载数据、搭环境或训练模型。

## 8. 边界来源定位

- `docs/08_科研决策、Gap判断与论文实操汇编.md`：方向红线、先靶后箭、结构性矛盾、去术语测试、开源与单卡可行性、Top-10 最近邻、Gap Survival，以及 Originality/Quality/Clarity/Significance 等审稿与写作边界。
