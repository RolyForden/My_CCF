# CAGE: 三维功能区域定位中的 Query Control 传播与因果定位

中文题目：CAGE——面向语言引导三维功能部位定位的查询控制传播机制分析
一句话概括：不把 CAGE 当新方法，而把它当作"测量装置"——先用同一几何下的有效 query pair 证明 point-level mask switching failure，再沿 query → 文本编码 → 跨模态融合 → 点表示 → 解码器这条链路定位 query control 在哪里丢失，最后用双向因果干预判断该位置是否真正控制空间决策；只有因果定位成立，才允许方法从机制中产生。
版本：导师讨论稿 v0.2，2026-09-20。本文给出候选研究对象和最小验证路线；尚无数据审计、baseline 或本方法实验结果，正式方法保持空白。

## 1. 引言

### 1.1 背景

语言引导三维功能部位定位的任务是：给定物体点云和任务描述，输出与当前功能相关的逐点热图。同一件工具，在"握持""切割""敲击"等不同任务下，应当指向不同的功能区域。因此模型不仅要知道物体是什么、前景在哪里，还必须把 query 里的功能意图传递到正确的点级空间表示上。

这一任务经历了几步推进：LASO / PointRefer 引入自然语言，用多尺度文本-点云融合和 question-conditioned decoder 建立起点；GEAL 用多视图迁移和粒度自适应融合提升泛化；GLANCE 用中间层跨模态连接和几何先验改善未见类别；CMAT 把瓶颈归到三维编码器的语义表征能力，用二维语义先验学习细粒度边界。LMAffordance3D 的补充材料还已经展示了保持图像和点云不变、只改变语言指令时输出不同 affordance 区域。因此，“固定几何改变语言”不是本文的新贡献；真正未决的是这种输出切换是否系统可靠，以及 query effect 通过什么内部路径控制逐点决策。

### 1.2 现有方法留下的问题

上一版方案把问题写成"全局多视图压缩细小区域，所以加局部重渲染、全局语境和选择性蒸馏"。核验全文和代码后，这条主张被直接覆盖：PointRefer 已做多尺度，GEAL 已做粒度自适应融合，GLANCE 已做全局语义加局部几何，CMAT 已从编码器语义容量解释细粒度边界。crop/zoom、cross-attention、选择性蒸馏即使有效，也很难单独构成结构性新问题。

更关键的是，现有工作的评测方式本身有盲区：标准 object-affordance 配对协议奖励"正确 mask"，却无法区分这个 mask 是由**当前 query 决定的**，还是由**对象类别、几何和 object-affordance 共现先验猜中的**。同时，LASO 的语言可能高度模板化，模型也可能只是把 `grasp / cut / open` 当作闭集 affordance label，而没有使用自然语言表达结构。前者是 point-level conditional control 问题，后者只是标签条件分割；两者必须先分开。

由此形成本文的核心问题：

> **当几何保持不变、任务条件改变时，模型是在执行自然语言条件控制，还是只识别闭集 affordance label？排除这一混淆后，query-dependent 变化能否传递到相关点并驱动正确的 mask 切换；如果不能，控制能力在哪个计算环节丢失？**

### 1.3 核心思路

本文不再把 CAGE 当作新方法，而把它当作测量装置：先用同一几何、不同有效功能 mask 的天然对照证明 failure 存在，再沿传播链路定位衰减区间，最后用双向干预判断该位置是否因果控制空间决策。只有因果定位成立，才允许方法从具体机制中产生，而不是预先缝一个通用模块。

## 2. CAGE 方法（测量装置，非主方法）

### 2.1 总体定位

研究链路固定为：

`query q → 文本编码 E_q → 跨模态融合 Fusion(P, E_q) → 点表示 Z_point → 解码器 Decoder → 逐点 mask`

CAGE 只提供定位故障所需的受控材料和测量工具，不承担论文核心创新，也不能单独支持"发现机制"的主张。它像一个显微镜和一把手术刀：显微镜看 query control 在哪一层衰减，手术刀做定点干预验证因果。

### 2.2 受控配对

- **CAGE-Pair**：同一 shape、两个不同有效 affordance、mask 低重叠的配对，用于验证 mask switching。
- **CAGE-Para**：同一 shape、同一 affordance、不同问题改写，用于验证语义等价不变性。

配对由现有标注确定性生成；语义关系（互斥 / 共享区域 / 可并存 / 蕴含层级 / 歧义）由双人盲审冻结，IoU 只做几何过滤、不替代语义判定。统计与置信区间以独立 shape 为单位，不能把同一 shape 产生的多个 pair 当成独立样本。测试 pair 不参与任何超参数选择。

每个 affordance 同时构造三层条件输入：

1. **Label**：只输入 `grasp / cut / open` 等 affordance label；
2. **Canonical**：长度和句式尽量匹配的标准问题；
3. **Paraphrase**：语义等价但表面形式变化的自然改写。

若 Label 与 Canonical 表现相近、Paraphrase 明显下降，首先说明语言表面泛化不足；若三者都无法驱动正确切换，才支持 point-level conditional routing failure。object-only、query-only 和类别先验预测器用于估计捷径上限；shuffle 与 null 只作为分布外压力测试，不进入主要存在性结论。

### 2.3 行为诊断

对每个合法 pair 跑 `(P, q_a) → p_a` 和 `(P, q_b) → p_b`。评价拆成三个互不替代的读数：

1. **单查询准确性**：分别报告 `S(p_a,y_a)` 与 `S(p_b,y_b)`，以及标准 aIoU/AUC/SIM/MAE；
2. **双向选择正确性**：要求 `S(p_a,y_a) > S(p_a,y_b)` 且 `S(p_b,y_b) > S(p_b,y_a)`，同时报告两个 margin，禁止用平均值让一侧补偿另一侧；
3. **空间变化方向**：比较 `p_b-p_a` 与 `y_b-y_a` 的方向一致性，并单独报告变化幅度和近零变化比例，避免 cosine 在预测几乎不变时产生误导。

这些读数是测量工具，不作为论文创新。结果必须同时展示标准分割性能与 query-control 表现，区分“准确且正确切换”“准确但依赖先验”“敏感但切错”和“整体失败”。

### 2.4 表示定位

沿链路记录各层表示，回答四个问题：差异是否存在、差异是否衰减、差异是否落在 `y_a XOR y_b` 的目标区域、差异是否可被 readout 读出。先按模块做 coarse localization，再按具体架构下钻到 query token、fusion block、attention/path、point group 或 feature subspace；不机械要求所有架构都存在 attention head。注意 readout 成功只说明信息存在，不说明模型实际使用。任何单一距离（cosine、CKA、probe accuracy）都不能直接定位根因，必须检查结论对度量选择的稳定性。

### 2.5 因果干预

对 candidate locus 做双向干预：**restoration**（把 target-query 的 query-dependent 分量 patch 到 source-query run，看 mask 是否朝正确方向切换）和 **destruction**（对原本切换正确的样本破坏该分量，看切换是否受损）。必要控制包括 norm-matched 随机方向、paraphrase 差异、非候选层同强度、query-token shuffle、空间错位 patch、geometry 等强度扰动，以及单路径与联合路径破坏。多位置搜索时进行多重比较校正。

最终允许的结论是：“该路径在指定模型和干预条件下介导了可测的 query effect。”整层 patch 成功只证明充分性线索；restoration 有效但 destruction 无效时，最多说明该路径具有替代性，不能宣称唯一或必要机制。

## 3. 拟贡献

若前置诊断成立，本研究只卖一个贡献：**在 dense language-guided 3D affordance grounding 中，区分闭集 affordance-label conditioning 与自然语言条件控制，并用同一几何、不同有效功能 mask 的天然对照，定位 query effect 无法控制点级空间决策的任务特有路径。**

其三个子点（一个贡献的三个子点，不是三个独立贡献）：

1. **行为存在性证据**：受控 pair 上存在 query-insensitive prediction，并排除语义歧义、mask 重叠、尺度和改写噪声。
2. **因果定位证据**：CAGE 的双向定点干预定位候选路径，并检验其在指定模型中的介导作用。
3. **机制结论与最小修复**：被定位机制跨至少两个架构复现，且最小结构修改（非通用 loss）能恢复 query control。

如果数据、行为 failure 或任务特有路径任一不成立，论文贡献可能不成立，本题应停止或仅保留为内部负结果；不预设“无论哪种结果都有论文”。

## 4. Baseline 与开源代码

| 模型或组合 | 用途 | 开源情况 |
|---|---|---|
| PointRefer / LASO | 最早的文字-点融合起点，首要被解释对象 | 官方代码与数据 |
| GEAL | 多粒度融合与 2D-3D 一致性的主基线 | 官方代码、LASO/PIAD 权重与评测入口 |
| LMAffordance3D | 固定图像与点云、改变语言的直接行为近邻 | CVPR 2025 正式论文与项目页；系统指标和内部因果定位未见 |
| GLANCE | 中间层跨模态连接的强邻居 | ICCV 2025 正式论文与代码入口已核；本地可运行性待验证 |
| CMAT / LAS | 2026 强基线，直接暴露 prompt 与 fused point features | 官方仓库已公开；权重、本地复现和单卡成本待验证 |

行为层必须与 LMAffordance3D 的 affordance multiplicity 展示明确区分，不能声称首次固定输入改变语言。机制定位至少需要两个内部结构不同且实际复现成功的模型，优先 PointRefer 和 GEAL。黑盒输出只能参加行为诊断，不能承担表示定位与因果干预结论。代码仓库存在不等于可复现；CMAT/GLANCE 只在 checkpoint、依赖和 hook 入口实际核验后加入。

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

数据可答后，用官方预训练 PointRefer 和 GEAL 分别跑 Label、Canonical、Paraphrase 三层输入，并加入 object-only、query-only 与类别先验基线。阶段 A 依次回答：模型是否只识别 affordance label；标准性能较高时是否仍存在双向 switching failure；该 failure 是否不能被 mask overlap、标签面积、类别共现、词频或改写噪声解释。

### 阶段 B：定位衰减区间（不训练）

沿链路记录表示，先做模块级粗定位，再按架构下钻到最小可解释路径，回答差异在哪里衰减、是否落在目标差异区域。此阶段只输出 candidate locus，不宣称因果。

### 阶段 C：因果干预

对 candidate locus 做 restoration、destruction、path-specific 和联合路径干预，判断它是可测 query effect 的介导路径、替代路径还是相关痕迹。这是机制主张的最低门槛。

### 阶段 D：方法（仅在 C 通过后）

方法从已验证机制中产生：修改位置与 locus 一致，计算作用对应机制而非通用 loss，先恢复内部 signal 再报 mask 指标，并用最小非机制修补和算力匹配对照排除"只是容量更大"。当前不采用预设的 CAGE-R、QER loss、低秩 router 或教师学生结构；它们最多是机制成立后的普通对照，不能替代机制发现。

## 7. 算力与周期

阶段 A–C 全部使用官方预训练权重做推理与干预，不训练新模型，单张 RTX 4090 足够。只有阶段 D 才涉及训练，且训练预算在 C 通过后才评估。首轮不下载无关模态，不启动完整训练。真实训练时间以 4090 短跑实测为准，不提前承诺固定天数。

## 8. 立项判断

这是一个比“诊断 + 指标 + loss”更值得验证、但尚未完成立项的数据依赖型方向。它现在只有可证伪的问题和实验顺序，没有已验证的 pair 规模、language-vs-label 区分、switching failure、candidate locus 或因果机制。

最关键的三项成立条件是：

1. 数据能在独立 shape 层面形成分布不过度偏斜、语义有效的多功能配对；
2. Label / Canonical / Paraphrase 分层能够排除“只是闭集 affordance 分类”的解释；
3. 至少两个结构不同的 baseline 暴露一致的 switching failure，且不能被几何、标签面积、类别共现和改写噪声解释；
4. 因果干预能定位任务特有的 query-to-point 介导路径，且最小结构修改能恢复 query control。

若前两项任一不成立，本题停止或改写为更低层次的 affordance-label conditioning 问题；若行为 failure 成立但没有任务特有的介导路径，只保留负结果，不自动包装成诊断论文。

最终研究主线：先证明 query control 确实丢失，再定位它在哪丢失、因何丢失，最后只修复那个被因果验证的环节——而不是堆更多通用模块。

## 9. 本轮交叉验证后的关键近邻

- LASO / PointRefer，CVPR 2024：https://openaccess.thecvf.com/content/CVPR2024/html/Li_LASO_Language-guided_Affordance_Segmentation_on_3D_Object_CVPR_2024_paper.html
- LMAffordance3D，CVPR 2025：https://sites.google.com/view/lmaffordance3d
- GLANCE，ICCV 2025：https://openaccess.thecvf.com/content/ICCV2025/html/Li_Intermediate_Connectors_and_Geometric_Priors_for_Language-Guided_Affordance_Segmentation_on_ICCV_2025_paper.html
- CMAT / LAS 官方仓库：https://github.com/yellowfish0331/CMAT
- Winoground，CVPR 2022：https://openaccess.thecvf.com/content/CVPR2022/html/Thrush_Winoground_Probing_Vision_and_Language_Models_for_Visio-Linguistic_Compositionality_CVPR_2022_paper.html
- CLEVR-Ref+，CVPR 2019：https://openaccess.thecvf.com/content_CVPR_2019/html/Liu_CLEVR-Ref_Diagnosing_Visual_Reasoning_With_Referring_Expressions_CVPR_2019_paper.html
