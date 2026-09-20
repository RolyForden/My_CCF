# CAGE: 三维功能区域定位中 Query-to-Point Control 的因果测量

中文题目：CAGE——三维功能区域定位中查询到点控制的因果测量
一句话概括：不把 CAGE 当新方法，而把它当作测量装置——先确认 query 是否正确改变 point-level mask，再区分 query 信息消失、保留但未空间绑定、或被后端忽略等候选机制，最后用双向因果干预检验被定位的计算路径；机制成立后再决定是否需要方法修复。
版本：导师讨论稿 v0.4，2026-09-21。本文给出候选研究对象和最小验证路线；尚无数据审计、baseline 或本方法实验结果，不预设正式方法。

## 1. 引言

### 1.1 背景

语言引导三维功能部位定位的任务是：给定物体点云和任务描述，输出与当前功能相关的逐点热图。同一件工具，在"握持""切割""敲击"等不同任务下，应当指向不同的功能区域。因此模型不仅要知道物体是什么、前景在哪里，还必须把 query 里的功能意图传递到正确的点级空间表示上。

这一任务经历了几步推进：LASO / PointRefer 引入自然语言，用多尺度文本-点云融合和 question-conditioned decoder 建立起点；GEAL 用多视图迁移和粒度自适应融合提升泛化；GLANCE 用中间层跨模态连接和几何先验改善未见类别；CMAT 把瓶颈归到三维编码器的语义表征能力，用二维语义先验学习细粒度边界。LMAffordance3D 的补充材料还已经展示了保持图像和点云不变、只改变语言指令时输出不同 affordance 区域。因此，“固定几何改变语言”不是本文的新贡献；真正未决的是这种输出切换是否系统可靠，以及 query effect 通过什么内部路径控制逐点决策。

### 1.2 现有方法留下的问题

上一版方案把问题写成"全局多视图压缩细小区域，所以加局部重渲染、全局语境和选择性蒸馏"。核验全文和代码后，这条主张被直接覆盖：PointRefer 已做多尺度，GEAL 已做粒度自适应融合，GLANCE 已做全局语义加局部几何，CMAT 已从编码器语义容量解释细粒度边界。crop/zoom、cross-attention、选择性蒸馏即使有效，也很难单独构成结构性新问题。

更关键的是，现有工作的评测方式本身有盲区：标准 object-affordance 配对协议奖励"正确 mask"，却无法区分这个 mask 是由**当前 query 决定的**，还是由**对象类别、几何和 object-affordance 共现先验猜中的**。同时，LASO 的语言可能高度模板化，模型也可能只是把 `grasp / cut / open` 当作闭集 affordance label，而没有使用自然语言表达结构。前者是 point-level conditional control 问题，后者只是标签条件分割；两者必须先分开。

但这一区分本身不能作为本文贡献：3D-AffordanceLLM 已明确区分预定义标签分割与 instruction reasoning，CompassAD 已系统构造同一组合下的 query-dependent mask、未见查询与无目标查询，AffordAny 也已评测未见指令改写。因此 Label / Canonical / Paraphrase、有效 query pair 与 unsupported query 都只能作为混淆控制或诊断材料。本文仍可能成立的空间，必须收紧到自然语言信号是否以**空间选择性的因果方式**控制三维点级决策。

由此形成本文的核心问题：

> **在排除闭集标签识别、模板词汇和几何先验后，query 信息能否作为空间选择性的因果信号作用于应改变的三维点？当 mask switching 失败时，是 query 信息消失，还是信息仍然存在但未完成点级空间绑定，或被后续决策环节忽略？**

### 1.3 核心思路

本文不再把 CAGE 当作新方法，而把它当作测量装置：先用同一几何、不同有效功能 mask 的天然对照证明 failure 存在，再沿计算链区分信息消失、空间绑定失败、后端忽略和分布式冗余，最后用双向干预判断候选路径是否因果控制空间决策。机制发现可以独立成立；方法修复只是机制自然导出的可选延伸，不作为立项前提。

## 2. CAGE 方法（测量装置，非主方法）

### 2.1 总体定位

研究链路固定为：

`query q → 文本编码 E_q → 跨模态融合 Fusion(P, E_q) → 点表示 Z_point → 解码器 Decoder → 逐点 mask`

CAGE 只提供定位故障所需的受控材料和测量工具，不承担论文核心创新，也不能单独支持"发现机制"的主张。它像一个显微镜和一把手术刀：显微镜观察 query control 在各功能阶段如何变化，手术刀做定点干预验证因果。

### 2.2 受控配对

- **CAGE-Pair**：同一 shape、两个不同有效 affordance、mask 低重叠的配对，用于验证 mask switching。
- **CAGE-Para**：同一 shape、同一 affordance、不同问题改写，用于验证语义等价不变性。

配对由现有标注确定性生成；语义关系（互斥 / 共享区域 / 可并存 / 蕴含层级 / 歧义）由双人盲审冻结，IoU 只做几何过滤、不替代语义判定。统计与置信区间以独立 shape 为单位，不能把同一 shape 产生的多个 pair 当成独立样本。测试 pair 不参与任何超参数选择。

每个 affordance 同时构造三层条件输入：

1. **Label**：只输入 `grasp / cut / open` 等 affordance label；
2. **Canonical**：长度和句式尽量匹配的标准问题；
3. **Paraphrase**：语义等价但表面形式变化的自然改写。

若 Label 与 Canonical 表现相近、Paraphrase 明显下降，首先说明语言表面泛化不足；若三者都无法驱动正确切换，才支持 point-level conditional routing failure。object-only、query-only 和类别先验预测器用于估计捷径上限；shuffle 与 null 只作为分布外压力测试，不进入主要存在性结论。

经 taxonomy 与人工语义审计的 unsupported query 仅保留为附录压力测试。它没有合法目标 mask，不进入主结果、双向 switching 或单查询准确性统计；“不支持”也不能由数据中缺少某个标注直接推出，以免把缺标误当成负例。

### 2.3 行为诊断

对每个合法 pair 跑 `(P, q_a) → p_a` 和 `(P, q_b) → p_b`。评价拆成三个互不替代的读数：

1. **单查询准确性**：分别报告 `S(p_a,y_a)` 与 `S(p_b,y_b)`，以及标准 aIoU/AUC/SIM/MAE；
2. **双向选择正确性**：要求 `S(p_a,y_a) > S(p_a,y_b)` 且 `S(p_b,y_b) > S(p_b,y_a)`，同时报告两个 margin，禁止用平均值让一侧补偿另一侧；
3. **空间选择性**：令 `Δy=y_b-y_a`、`Δp=p_b-p_a`，对取值在 `[0,1]` 的软热图分别用 `[Δy]+`、`[-Δy]+` 和 `1-|Δy|` 作为 `D+`（应增强）、`D-`（应抑制）和 `D0`（应保持）的连续权重。分别报告 `D+` 上的正确增强、`D-` 上的正确抑制和 `D0` 上的附带扰动；`||Δp|| / (||Δy|| + ε)` 只作辅助幅度读数，不能替代空间方向判断。

不同 affordance pair 与 paraphrase pair 必须分开解释。前者只有在 `||Δy||` 明确非零的子集上，才能把 `D+ / D-` 几乎没有定向变化称为 **counterfactual silence**；后者的 `Δy=0`，近零预测变化本来就是期望行为，反而应报告 **paraphrase instability**，即语义不变时预测发生了多少非必要变化。这样既避免把 pair 本身过弱误读成模型失去 query control，也避免把整张 mask 的无差别变化误判成正确 switching。

这些读数是测量工具，不作为论文创新。结果必须同时展示标准分割性能与 query-control 表现，区分“准确且正确切换”“准确但依赖先验”“敏感但切错”和“整体失败”。

### 2.4 表示定位

沿链路记录各层表示，回答四个问题：query 差异是否仍可读、是否在某处消失、是否空间集中到 `D+ / D-` 而非扩散到 `D0`、是否最终被 decoder 使用。先按模块做 coarse localization，再按具体架构下钻到 query token、fusion block、attention/path、point group 或 feature subspace；不机械要求所有架构都存在 attention head。readout 成功只说明信息存在，不说明模型实际使用；全局可读但在点级缺少选择性，是待检验的 **spatial binding failure**，不能预写成发现。任何单一距离（cosine、CKA、probe accuracy）都不能直接定位根因，必须检查结论对度量选择的稳定性。

### 2.5 因果干预

对 candidate locus 做双向干预：**restoration**（把 target-query 的 query-dependent 分量 patch 到 source-query run，看 mask 是否朝正确方向切换）和 **destruction**（对原本切换正确的样本破坏该分量，看切换是否受损）。交换只发生在同 shape 的合法 query run 之间，并保持张量位置、LayerNorm 前后状态和尺度一致；除 norm-matched 随机方向、paraphrase 差异、非候选层同强度、query-token shuffle、空间错位 patch、geometry 等强度扰动外，还需报告从零到完整 patch 的剂量曲线。candidate locus 在 discovery shapes 上确定，再到未参与搜索的 shape 和 affordance-pair 类型上确认，禁止在同一测试集找最佳层又汇报效果。多位置搜索时进行多重比较校正。

最终允许的结论是：“该路径在指定模型和干预条件下介导了可测的 query effect。”整层 patch 成功只证明充分性线索；restoration 有效但 destruction 无效时，最多说明该路径具有替代性，不能宣称唯一或必要机制。

## 3. 拟贡献

若前置诊断与因果证据成立，本研究只卖一个贡献：**揭示并验证 dense language-guided 3D affordance grounding 中介导 query 语义到点级空间决策的计算机制，解释它何时能选择性增强 `D+`、抑制 `D-` 并保持 `D0`，以及 switching failure 究竟来自信息消失、空间绑定失败还是后端忽略。**

其三个子点（一个贡献的三个子点，不是三个独立贡献）：

1. **行为存在性证据**：受控 pair 上存在 query-insensitive prediction，并排除标签识别、模板词汇、语义歧义、mask 重叠和几何先验。
2. **空间机制证据**：内部 query 信息的可读性与其在 `D+ / D- / D0` 上的空间选择性发生可解释分离。
3. **因果与预测证据**：双向定点干预验证候选路径的介导作用，并使该机制能够在未参与定位的 shape 和 affordance-pair 类型上预测 failure。

Label / Canonical / Paraphrase、CAGE-Pair、unsupported query 和 activation patching 都是控制或工具，不进入核心贡献。最小修复不是成立条件；若机制自然指向可检验的结构修改，再把修复作为增强证据。如果数据或行为 failure 不成立，本题应停止或仅保留为内部负结果；若只复现通用 cross-modal routing 机制，novelty 降级为领域验证。

## 4. Baseline 与开源代码

| 模型或组合 | 用途 | 开源情况 |
|---|---|---|
| GEAL | 阶段 A 的首个 discovery 模型 | 官方代码、LASO/PIAD 权重与评测入口已核验 |
| PointRefer / LASO | 同任务结构验证候选 | 官方代码与数据；任务 checkpoint 未核验，可能需要自行训练 |
| LMAffordance3D | 固定图像与点云、改变语言的直接行为近邻 | CVPR 2025 正式论文与项目页；系统指标和内部因果定位未见 |
| GLANCE | 中间层跨模态连接的强邻居 | ICCV 2025 正式论文与代码入口已核；本地可运行性待验证 |
| CMAT / LAS | 2026 强基线，直接暴露 prompt 与 fused point features | 官方仓库已公开；权重、本地复现和单卡成本待验证 |

行为层必须与 LMAffordance3D、3D-AffordanceLLM、CompassAD 和 AffordAny 明确区分，不能声称首次固定输入改变语言、首次区分标签与自然语言或首次评测改写敏感性。阶段 A 先用唯一已核验任务权重和评测入口的 GEAL 做 discovery；PointRefer 只有在获得可核验权重或完成受控训练后才加入结构验证。跨模型结论比较功能阶段，不要求相同层号或 attention head。黑盒输出只能参加行为诊断，不能承担表示定位与因果干预结论。

## 5. 数据集

| 数据集 | 规模与特点 | 建议用途 |
|---|---|---|
| LASO | 19,751 个点云-问题对，8,434 个形状，23 类，17 种功能；这些总量不能推出同 shape 多 affordance 的可用规模 | 候选主数据；必须先审计后才能确认可答性 |
| PIAD | 7,012 个点云实例 | 只有在能建立等价语言与同对象多 affordance 映射时作外部验证；不复用 LASO 文本后宣称独立语言泛化 |

功能标签是软热图，不改写成精确抓取接触标签。LASO 的 seen/unseen 划分按被比较工作的协议固定，避免同 shape 泄漏。所有 pair 数之外必须同时报告独立 shape 数、affordance-pair 类型数及每类独立 shape 数。

## 6. 分阶段实验路线

### 阶段 A：证明现象存在（不训练）

先做数据审计：按 split 与 shape 聚合标注，报告可配对独立 shape 数、每个 shape 的不同 affordance 数、affordance-pair 类型及其独立 shape 数、mask IoU、前景比例、面积差和类别共现分布。原先的“30% shape / 300 pair / IoU < 0.5”没有数据或 power analysis 支撑，全部取消；也不接受用“500 shape / 8 类 pair / 每类 30 shape”等另一组任意门槛替代。

审计后再根据真实分布判断三个问题：是否存在足够的独立 shape 支撑主要比较；核心 pair 是否被少数类别或 affordance 垄断；按 shape 划分后是否仍能形成 train/validation/test 隔离。若只能得到少量、单类别或高度相关的 pair，LASO 不能支撑该 RQ，本题停止。

审计必须同时检查 Question0–14 是自然改写还是模板替换、是否泄漏 object 名称或直接 affordance 词，以及能否按 shape 和 pair type 隔离 discovery / confirmation。若语言基本只是标签模板，研究对象降级为 **prompt-conditioned spatial control**，不得宣称自然语言理解机制。

数据可答后，先用 GEAL 官方权重跑 Label、Canonical、Paraphrase 三层输入，并加入 object-only、query-only 与类别先验。阶段 A 依次回答：模型是否只识别 affordance label；标准性能较高时是否仍存在双向 switching failure；该 failure 是否不能被 mask overlap、标签面积、类别共现、词频或改写噪声解释。不同 affordance pair 只在 GT effect 明确非零时统计 counterfactual silence；paraphrase pair 单独统计 paraphrase instability；unsupported query 仅进入附录压力测试。PointRefer 不再假定有官方任务权重。

### 阶段 B：定位表示与空间绑定（不训练）

沿链路记录表示，先做模块级粗定位，再按架构下钻到最小可解释路径，区分 query 信息消失、全局可读但未选择性进入 `D+ / D-`、decoder 忽略以及分布式冗余。此阶段只输出 candidate locus，不宣称因果，也不提前命名“语义广播但空间绑定失败”。

### 阶段 C：因果干预

对 candidate locus 做 restoration、destruction、path-specific 和联合路径干预，判断它是可测 query effect 的介导路径、替代路径还是相关痕迹。这是机制主张的最低门槛。随后单独裁决 novelty：若所定位路径只是已有 STDC / back-patching 一类通用 cross-modal routing 机制在本任务上的复现，则贡献降级为领域验证；只有额外证明机制与点级空间选择、同几何多 affordance mask 或三维特征传播存在不可由通用机制覆盖的联系，才允许使用“任务特异性”表述。“首次在本任务观察到”不等于“任务特有”。

### 阶段 D：可选修复（仅在 C 通过且机制自然导出时）

修复不是立项或成文的强制条件。只有已验证机制自然指向结构修改时才进入本阶段：修改位置与 locus 一致，计算作用对应机制而非通用 loss，先恢复内部空间选择性再报 mask 指标，并用最小非机制修补和算力匹配对照排除"只是容量更大"。当前不采用预设的 CAGE-R、QER loss、低秩 router 或教师学生结构。

## 7. 算力与周期

阶段 A–C 全部使用官方预训练权重做推理与干预，不训练新模型，单张 RTX 4090 足够。只有阶段 D 才涉及训练，且训练预算在 C 通过后才评估。首轮不下载无关模态，不启动完整训练。真实训练时间以 4090 短跑实测为准，不提前承诺固定天数。

## 8. 立项判断

这是一个比“诊断 + 指标 + loss”更值得验证、但尚未完成立项的数据依赖型方向。它现在只有可证伪的问题和实验顺序，没有已验证的 pair 规模、language-vs-label 区分、switching failure、candidate locus 或因果机制。

最关键的四项成立条件是：

1. 数据能在独立 shape 层面形成分布不过度偏斜、语义有效的多功能配对；
2. Label / Canonical / Paraphrase 分层能够排除“只是闭集 affordance 分类”的解释；
3. 至少两个结构不同的 baseline 暴露一致的 switching failure，且不能被几何、标签面积、类别共现和改写噪声解释；
4. 因果干预能定位 query-to-point 介导路径，且该机制能在独立 shape 和新 affordance-pair 类型上预测 failure；是否存在机制导出的有效修复另行检验，不作为预设前提。

若前两项任一不成立，本题停止或改写为更低层次的 affordance-label conditioning 问题；若行为 failure 成立但因果定位失败，只保留负结果。若定位成功但只得到已知的通用 routing 机制，则按领域验证降级，不包装成任务特有机制论文。

最终研究主线：先证明 query control 确实失效，再区分信息消失、空间绑定失败与后端忽略，并因果验证决定性环节；若需要修复，也只修复被验证的机制，而不是堆更多通用模块。

## 9. 本轮交叉验证后的关键近邻

- LASO / PointRefer，CVPR 2024：https://openaccess.thecvf.com/content/CVPR2024/html/Li_LASO_Language-guided_Affordance_Segmentation_on_3D_Object_CVPR_2024_paper.html
- LMAffordance3D，CVPR 2025：https://sites.google.com/view/lmaffordance3d
- 3D-AffordanceLLM，2025：https://arxiv.org/abs/2502.20041
- CompassAD，2026：https://arxiv.org/abs/2604.02060
- AffordAny，2026：https://arxiv.org/abs/2608.20720
- GLANCE，ICCV 2025：https://openaccess.thecvf.com/content/ICCV2025/html/Li_Intermediate_Connectors_and_Geometric_Priors_for_Language-Guided_Affordance_Segmentation_on_ICCV_2025_paper.html
- CMAT / LAS 官方仓库：https://github.com/yellowfish0331/CMAT
