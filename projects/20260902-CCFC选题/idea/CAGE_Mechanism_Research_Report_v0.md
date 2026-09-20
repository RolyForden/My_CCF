# CAGE: Query Control 在三维功能区域定位中的传播、衰减与因果定位

> CAGE: Causal Analysis of Grounding and Encoding  
> 研究方案报告 - 导师讨论初稿  
> 版本：v0.1，2026-09-20  
> 状态：IDEA / PENDING；无实验结果；正式方法保持空白

## 一句话概括

本研究不再把 CAGE 当作新方法，而把它作为 measurement apparatus：先用同一几何下的有效 query pair 证明 point-level mask switching failure，再沿 `q -> E_q -> Fusion -> Z_point -> Decoder -> Mask` 定位 query control 的候选衰减区间，最后通过 activation patching、bypass、injection 和 ablation 的双向干预判断该位置是否真正控制最终空间决策。只有因果定位成立后，才允许方法从具体机制中产生。

## 1. 研究背景与问题变化

### 1.1 任务背景

Language-guided 3D affordance grounding 接收物体点云和任务问题，输出与当前功能相关的逐点 mask。同一把工具可能因“握持”“切割”“敲击”等有效 query 指向不同功能区域，因此模型不仅要识别物体和前景，还必须把 query 中的功能意图传递到正确的点级空间表示。

LASO/PointRefer 已通过多尺度 text-point fusion、question-conditioned affordance query 和动态 mask kernel 建立任务起点。GEAL 进一步引入多粒度融合和 2D-3D 一致性；GLANCE 使用中间层 cross-modal connector 和几何 query；CMAT/LAS 通过 2D semantic affinity pretraining 与 co-attentional fusion 提升 point representation。现有工作主要用最终分割指标证明模型更准，却没有直接回答：query change 在内部是否持续影响与目标区域相关的 point representation。

### 1.2 旧主线为什么停止

上一版把问题写成 instruction faithfulness，并以 controlled pairs、sensitivity metrics 和 paired loss 形成闭环。这个闭环可以完成一篇评测或增量优化工作，但诊断、指标和通用 loss 都是研究工具，不是表示机制贡献。它最多回答“模型是否随 query 改变”，不能回答“query control 在何处、因何丢失”。

因此研究对象改为：

> **为什么 language-guided 3D affordance model 在 query 改变时，内部表示没有发生足以驱动 point-level prediction 改变的变化？**

### 1.3 新的主线

待检验现象：同一几何下，不同有效 query 有时可能无法驱动正确的 point-level mask switching。

根问题：query information 沿下列链路传播时，在哪里失去对空间决策的控制？

`q -> E_q -> Fusion(P,E_q) -> Z_point -> Decoder -> Mask`

核心证据要求：不能只观察某层表示“变得相似”；必须定点恢复或破坏该层的 query-dependent component，并观察最终 mask switching 是否相应恢复或受损。

## 2. 工作定位与论文边界

### 2.1 CAGE 的定位

CAGE 只保留三类能力：

- 行为 probe：valid swap 为主，null/shuffle/wrong-object 为压力测试；
- controlled evaluation：CAGE-Pair 与 CAGE-Para；
- sensitivity measurement：测量输出与中间表示对 query change 的响应。

CAGE 是显微镜和手术刀，不是论文主方法。Counterfactual Swap Margin、representation distance、linear probe 等都是仪器读数，不能单独形成机制主张。

### 2.2 当前不包含正式方法

本报告取消预设方法章节。Routing、binding、conditional modulation 和 point-query interaction 只是潜在设计空间；D2 未证明具体机制以前，不命名、不实现、不声称任何一个是答案。

Paired loss 进一步降级为 non-mechanistic intervention control：如果普通 paired supervision 已同时恢复内部 query signal、空间对齐和 mask switching，failure 更可能来自监督不足，不需要提出新的 representation mechanism。

## 3. 最近邻机制工作查重

### 3.1 本轮检索范围

本轮针对四类最近邻进行定向查重：

1. language-guided 3D affordance segmentation 的 text encoder、fusion、point feature 和 decoder 结构；
2. controlled/counterfactual affordance evaluation；
3. multimodal representation dominance、cross-modal influence 和 input ablation；
4. activation patching、path patching 与 VLM causal tracing。

来源限于 CVF/ACL/NeurIPS/PMLR/OpenReview/arXiv 正文和官方 GitHub。该检索用于建立初稿边界，不宣称已经穷尽所有 2026 年工作；进入 baseline 前仍需补齐 Top-10 最近邻的全文主张表。

### 3.2 最近邻矩阵

| 工作 | 直接相关机制 | 对本题的威胁 | 当前边界 |
|---|---|---|---|
| LASO / PointRefer, CVPR 2024 | 三次语言注入、question-conditioned decoder、动态 mask kernel | 高 | 是首要被解释对象，但未做同几何 query pair 的层级因果定位 |
| GEAL, CVPR 2025 | 多层 GAFM、feature propagation、text decoder 与 point-wise map | 高 | 融合链更完整，仍以性能和跨模态一致性为主 |
| GLANCE, ICCV 2025 | intermediate connector 将 text/3D 中间层概念注入 point embedding | 高 | 已占据“中间层连接改善表示”；不能把 connector 本身当新贡献 |
| CMAT/LAS, CVPR 2026 | prompt/point projection、统一序列 co-attention、dense head | 高 | 代码直接暴露 prompt 与 fused point features，是强机制 baseline；未见 query-control causal localization |
| GroundBench, arXiv 2026 | factorized information conditions、same-image counterfactual re-ask | 极高 | 已占据 affordance counterfactual diagnosis；本题不能以行为评测作为核心新颖性 |
| Palit et al., ICCV Workshop 2023 | 将 causal tracing 适配到 BLIP，定位后层表示的因果相关性 | 高 | 已占据“把 causal tracing 用到 VLM”；本题必须依靠 point-level spatial control 和 3D 架构机制 |
| Same Task, Different Circuits, NeurIPS 2025 | circuit localization 与 later-to-earlier back-patching，恢复部分跨模态性能差距 | 极高 | 与“信息到得太晚、无法影响后续位置”高度相似；不能泛称首次研究 multimodal routing failure |
| Vision-Default, Prior-Override, arXiv 2026 | residual/head/MLP activation patching，区分 routing heads 与 writing heads | 极高 | 已有跨模型 component-level causal mechanism 范式；我们的贡献必须是 dense 3D query-to-point 机制而非 patching 工具 |
| Dual-Pathway Circuits, arXiv 2026 | 五个 VLM 的 activation patching、路径分析与定点 suppression | 高 | 证明“行为 -> 路径 -> 干预”叙事已成熟；本题需避免照搬到新任务 |
| Beyond Cross-Modal Alignment, ACL Findings 2026 | Modality Dominance Score 与 training-free feature editing | 中高 | 已占据 modality dominance 测量；不能把新的 sensitivity scalar 当主贡献 |
| Frank et al., EMNLP 2021 | cross-modal input ablation，发现视觉与文本影响不对称 | 中 | null/ablation 只能作为行为 probe，不能支持机制结论 |
| Zhang & Nanda, ICLR 2024 | 系统分析 activation patching 的 metric 与 corruption 选择 | 方法边界 | 提醒 patching 结论对度量和 corruption 敏感，协议必须多控制并预注册 |

### 3.3 查重后的真实空间

这条赛道不是空白：行为反事实、模态 dominance、activation patching、路径定位和 representation editing 都已有直接先例。因此，下列主张均不能作为本研究贡献：

- 首次用 counterfactual prompt 测模型是否使用语言；
- 首次分析 multimodal information flow；
- 首次把 activation patching 用到 vision-language model；
- 提出一个新的 query sensitivity metric；
- 发现多模态模型存在某种 modality dominance。

当前仍可能存活的窄空间是：

> **在 dense language-guided 3D affordance grounding 中，利用同一几何、不同有效 point mask 的天然对照，因果定位 query-dependent global state 无法路由到相关 point representation 的具体计算环节。**

这个差异是否足够形成论文尚未确认。尤其是 NeurIPS 2025 的 back-patching 工作已经提出“表示对齐发生得太晚，无法影响后续位置”，与 H3 的抽象叙事很接近。必须证明 point-level spatial selectivity、架构特定计算路径和 affordance mask switching 带来不可替代的新问题，而不是把同一方法迁移到 3D。

## 4. 四个竞争性机制假设

### H1 - Query collapse

不同有效 query 经 text encoder 后已经过于相似，后端接收不到足够的条件差异。

候选观察：`E(q_a) ~= E(q_b)`，且不同有效 query 的差异没有显著高于 paraphrase/noise floor。

### H2 - Fusion attenuation

Text representation 可区分，但经过 cross-modal fusion 后，被 geometry/object representation 淹没。

候选观察：`E(q_a) != E(q_b)`，但 fusion 后 query sensitivity 显著降低。

### H3 - Point-level conditioning failure

Global multimodal state 随 query 改变，但该变化没有传递到与两个 GT masks 差异相关的 point/token。

候选观察：global state 可读出 affordance 变化；pointwise representation delta 却无法定位 `y_a XOR y_b` 区域。

这是当前优先验证假设，但不是默认结论。

### H4 - Decoder dominance / geometry shortcut

Point representation 已含空间对齐的 query difference，最终 decoder 却主要读取 geometry foreground prior 或 object-specific affordance prior，使 masks 再次趋同。

候选观察：`Z_point(P,q_a)` 与 `Z_point(P,q_b)` 在目标差异区域有稳定变化，但 pre-mask/logit 或最终 mask 的 targeted switching 不足。

## 5. 总体证据阶梯

| 证据层 | 允许表述 | 禁止越界 |
|---|---|---|
| E0 行为 | 受控 pair 上存在 switching failure | 不能定位内部根因 |
| E1 表示 | 相邻阶段出现 sensitivity drop，得到 candidate locus | 不能称 causal mechanism |
| E2 干预 | restoration/destruction 改变 targeted mask switching | 不能自动泛化到其他架构 |
| E3 复现 | 同一机制在不同 fusion/decoder 架构重复成立 | 不能宣称所有 3D grounding 模型均如此 |

论文级机制主张至少需要 E2。D1 即使曲线很漂亮，也只能得到 candidate locus。

## 6. D0 - Behavioural Existence 可执行协议

### 6.1 目标

证明同一几何下的有效 query change 确实存在 point-level switching failure，并排除数据歧义、mask overlap、尺度、paraphrase noise 和评测阈值造成的伪象。

### 6.2 输入与冻结项

- LASO 官方 `anno_train.pkl`、`anno_val.pkl`、`anno_test.pkl`；
- `objects_*.pkl` 与 `Affordance-Question.csv`；
- 数据文件 hash、split、官方代码 commit；
- PointRefer 和 GEAL 官方 checkpoint；CMAT/LAS 仅在权重入口通过审计后加入；
- 统一 deterministic inference 配置。

### 6.3 D0-A：Pair inventory

1. 按 `split + shape_id` 聚合标注。
2. 枚举同 shape 不同 affordance 的 mask pair。
3. 计算 foreground ratio、mask IoU、交并差区域大小、object class 和 affordance transition。
4. 建立语义关系 taxonomy：`distinct`、`overlap-valid`、`co-required`、`entailment/hierarchy`、`ambiguous`。
5. 只有 `distinct` 且差异区域足以稳定评测的 pair 进入主分析；IoU 仅作几何过滤，不替代语义判定。
6. 双人盲审语义关系，保存分歧与最终裁决；不得在看模型结果后修改 pair。

必须输出：

- `artifacts/d0/pair_inventory.parquet`
- `artifacts/d0/pair_semantic_audit.csv`
- `artifacts/d0/excluded_pairs.csv`
- `artifacts/d0/dataset_summary.json`
- `artifacts/d0/data_hashes.json`

### 6.4 D0-B：Behaviour run manifest

每个合法 pair 运行：

- `(P,q_a)->p_a` 与 `(P,q_b)->p_b`；
- 每个 query 的 paraphrase control；
- object-only、null、shuffle 和 wrong-object 仅作压力测试，不进入主要存在性判定；
- 同一 point order、归一化和随机状态，不改变几何输入。

主要行为量：

`T(p;y_a,y_b) = S(p,y_b) - S(p,y_a)`

其中 `S` 使用预注册的 soft-IoU 或 mask similarity。成功 switching 要求从 `q_a` 到 `q_b` 时，`T` 朝 `y_b` 方向变化；同时报告标准 aIoU/AUC/SIM/MAE，避免新指标脱离原任务。

统计单位是 shape，不是 pair。置信区间按 shape cluster bootstrap；同一 shape 的多个 pair 不得作为独立样本。

### 6.5 D0 裁决

`SURVIVE`：至少两个融合/解码设计不同的可复现模型，在语义有效 pair 上出现方向一致且超过 paraphrase/noise floor 的 switching failure，并且 overlap、scale、class 和 prompt surface form 不能解释主要效应。

`WEAK`：只在单模型、单类别或单一 transition 上成立，允许一次预注册的扩样或实现核查。

`KILL`：无法形成可靠 pair；强 baseline 均能正确 switching；或 failure 主要由数据歧义、区域重叠、尺度或语言噪声解释。

## 7. D1 - Representation Localization 可执行协议

### 7.1 Hook map

PointRefer 首轮记录：

- `forward_text()` 的 resized token representation；
- 三次 `gpb` 前后 point features；
- `fp1` 后 dense `up_sample`；
- transformer decoder 后 `t_feat`；
- sigmoid 前 point-wise logits 与最终 mask。

GEAL 首轮记录：

- `forward_text()` 输出；
- 三次 `GAFM_block` 前后 features；
- `fp1` 与 multi-level fusion 后 `fused_feat`；
- `text_decoded`；
- sigmoid 前 `affordance_map` 与最终 mask。

CMAT/LAS 首轮记录：

- `prompt_features` 与 `prompt_features_proj`；
- `point_group_features`、projected/upsampled point features；
- `unified_sequence`；
- co-attention 后 `fused_prompt_features` 与 `fused_point_features`；
- segmentation head 各层和 logits。

先为每个 hook 写 shape/dtype/device manifest；只有语义一致的表示才能跨 query 比较。跨架构绝不直接比较 raw norm 大小。

### 7.2 每层三类读数

1. Global sensitivity：有效 query pair 的 representation difference，相对 paraphrase 与重复推理 noise floor 归一化。
2. Spatial relevance：对每个点计算 `Delta_l(i)=||z_l^a(i)-z_l^b(i)||`，检查其是否集中在 `y_a XOR y_b`，并与 common foreground、background 分开报告。
3. Readability：用冻结表示训练简单 linear readout 判断 affordance 或 pair direction。Readout 只证明信息存在，不证明原模型实际使用。

Cosine、CKA、RDM、probe accuracy 不设为唯一指标。必须检查结论是否对 metric choice 稳定，以避免 activation-patching 文献已经指出的度量敏感性。

### 7.3 Candidate locus 判定

某区间只能在同时满足以下条件时进入 D2：

- 有效 query difference 在相邻阶段出现可重复的下降；
- paraphrase control 没有同样下降模式；
- pointwise spatial relevance 同步降低，或 decoder readout 与 point signal 发生脱节；
- 模式跨 shape、affordance transition 和至少两个模型检查。

D1 输出：`layer_manifest.json`、逐样本 activation index、layerwise sensitivity 表、空间 delta map、candidate-locus report。Activation 原始文件使用 chunked tensor 格式并记录 checkpoint/hash，避免只保存汇总图。

## 8. D2 - Causal Intervention 可执行协议

### 8.1 基本单位

对同一 `(P,q_a,q_b,y_a,y_b)` 建立 source run 与 target run。两条 query 都是有效输入，不称“clean/corrupt”。干预只改变指定 activation 或计算路径，其他输入与权重保持不变。

### 8.2 Restoration

把 target-query run 的 candidate activation 或 query-dependent component patch 到 source-query run，测试输出是否朝 `y_b` 定向移动。先做整层/整路径 coarse patch 定位，再下钻到 token、point group、attention head 或 residual branch；不得从一开始大规模搜索所有组件。

主要效应：

`PatchEffect_l = T(patch_l(a<-b);y_a,y_b) - T(p_a;y_a,y_b)`

同时报告对 `y_a XOR y_b`、共同前景和背景的局部效应，防止整体 logit shift 被误当作正确 routing。

### 8.3 Destruction

对原本 switching 正确的 pair，equalize、ablate 或交换 candidate query-dependent component，测试 targeted switching 是否受损。只有 restoration 有效但 destruction 无效时，最多说明该路径具有替代性，不足以声称必要机制。

### 8.4 Path-specific tests

按候选假设选择路径，而非统一套模板：

- H1：text encoder token/state interchange；
- H2：text-to-fusion attention output 与 residual branch patch；
- H3：global state 到 point/token 的 cross-attention、ungroup 或 feature-propagation 路径 patch；
- H4：保持 `Z_point`，干预 decoder query/dynamic kernel/readout path。

### 8.5 必要控制

- norm-matched random activation；
- paraphrase activation patch；
- 非候选层同强度 patch；
- point permutation 与区域外 point patch；
- geometry-path 等强度扰动；
- 原始任务分数、非目标区域和数值稳定性检查；
- 双方向 `a<-b` 与 `b<-a`。

### 8.6 D2 裁决

`MECHANISM-SURVIVE`：restoration 与 destruction 形成方向一致的双向证据；行为变化集中在目标差异区域；random/paraphrase/non-candidate controls 不能复现效应；至少在一个第二架构中得到同类路径证据。

`CORRELATE-ONLY`：D1 有 sensitivity drop，但 restoration 不恢复或 destruction 不破坏 switching。该位置只能作为相关现象，继续查链路，禁止围绕它设计方法。

`ARCHITECTURE-SPECIFIC`：只在一个模型成立。可形成模型诊断，但不能上升为领域机制。

## 9. 最小执行顺序与产物

| 工作包 | 内容 | 完成定义 |
|---|---|---|
| P0 文献与代码冻结 | Top-10 主张表、仓库 commit、可 hook 层级图 | 最近邻边界与 hook map 可审计 |
| D0-A 数据审计 | pair inventory、semantic audit、power/noise plan | 决定数据能否回答问题 |
| D0-B 行为诊断 | 预训练模型推理、cluster bootstrap、失败切片 | 决定现象是否存在 |
| D1 层级定位 | activation capture、spatial delta、candidate locus | 只输出候选区间 |
| D2 定点干预 | coarse patch -> path/component patch -> controls | 决定是否存在机制证据 |
| D3 方法 | 仅在 D2 survive 后启动 | 修改点由已验证机制唯一约束 |

首轮不训练新模型。优先用官方 checkpoint 完成 D0-D2 的推理与干预；instrumentation smoke test 只证明 hook 和输出正确，不能算实验结果。

## 10. 风险、反对意见与止损

### 最强反对意见

1. 只是把 VLM activation patching 迁移到一个 3D 小模型和新任务。
2. LASO 的有效 pair 太少或语义关系不清，导致行为 failure 不可信。
3. Representation distance 的下降是归一化、token 数或 feature dimension 变化，不是信息丢失。
4. Activation patch 产生 off-manifold state，mask 改变只是数值扰动。
5. PointRefer、GEAL 和 CMAT 的 fusion 结构不同，没有共同的机制层级。
6. Candidate locus 能影响输出，但不是唯一或必要路径，机制主张被 redundancy 推翻。
7. 现象只发生在旧 baseline，强 encoder 已自然解决。

### 对应止损

- D0 不成立：停止本题。
- 最近邻已直接覆盖 dense 3D query-to-point causal localization：G1 KILL。
- D1 无稳定 candidate locus：不靠挑图继续故事。
- D2 无 targeted behavioural consequence：candidate locus 降为相关现象。
- Generic paired loss 完整恢复内部链路与行为：解释为 supervision deficiency，重新评估上限。
- 仅单模型成立：缩小为 architecture-specific diagnosis，不能宣称通用机制。
- 方法只提高 aIoU、不恢复内部 sensitivity 与 switching：不能支持机制论文。

## 11. 当前立项判断

当前方向比“诊断 + 指标 + loss”更有科学上限，但也明显更难。它已经具备一个可证伪的机制发现流程，却尚未拥有任何已验证的 failure、candidate locus 或 causal mechanism。

当前唯一值得投入的工作是：

1. 完成最近邻机制工作的全文主张级查重；
2. 冻结并执行 D0/D1/D2 协议。

在 D2 以前，不投入方法命名、复杂模块设计、无人机仿真或论文包装。

## 参考文献与代码入口

1. Li et al. LASO: Language-guided Affordance Segmentation on 3D Object. CVPR 2024. https://openaccess.thecvf.com/content/CVPR2024/html/Li_LASO_Language-guided_Affordance_Segmentation_on_3D_Object_CVPR_2024_paper.html
2. Lu et al. GEAL: Generalizable 3D Affordance Learning with Cross-Modal Consistency. CVPR 2025. https://openaccess.thecvf.com/content/CVPR2025/html/Lu_GEAL_Generalizable_3D_Affordance_Learning_with_Cross-Modal_Consistency_CVPR_2025_paper.html
3. Li et al. Intermediate Connectors and Geometric Priors for Language-Guided Affordance Segmentation on Unseen Object Categories. ICCV 2025. https://openaccess.thecvf.com/content/ICCV2025/html/Li_Intermediate_Connectors_and_Geometric_Priors_for_Language-Guided_Affordance_Segmentation_on_ICCV_2025_paper.html
4. Huang et al. Unlocking 3D Affordance Segmentation with 2D Semantic Knowledge. CVPR 2026. https://openaccess.thecvf.com/content/CVPR2026/html/Huang_Unlocking_3D_Affordance_Segmentation_with_2D_Semantic_Knowledge_CVPR_2026_paper.html
5. Sattigeri. GroundBench: A Factorized, Counterfactual Benchmark for Locating VLM Affordance Failures. arXiv 2026. https://arxiv.org/abs/2609.13308
6. Palit et al. Towards Vision-Language Mechanistic Interpretability: A Causal Tracing Tool for BLIP. ICCV Workshop 2023. https://openaccess.thecvf.com/content/ICCV2023W/CLVL/html/Palit_Towards_Vision-Language_Mechanistic_Interpretability_A_Causal_Tracing_Tool_for_BLIP_ICCVW_2023_paper.html
7. Nikankin et al. Same Task, Different Circuits: Disentangling Modality-Specific Mechanisms in VLMs. NeurIPS 2025. https://papers.nips.cc/paper_files/paper/2025/hash/5fcd540792da599adf1b932624e98f1f-Abstract-Conference.html
8. Lietzow et al. Vision-Default, Prior-Override: Causal Mechanisms of Perception-Knowledge Conflict in Vision-Language Models. arXiv 2026. https://arxiv.org/abs/2606.28273
9. Liu et al. Dual-Pathway Circuits of Object Hallucination in Vision-Language Models. arXiv 2026. https://arxiv.org/abs/2605.13156
10. Yan et al. Beyond Cross-Modal Alignment: Measuring and Leveraging Modality Gap in Vision-Language Models. Findings of ACL 2026. https://aclanthology.org/2026.findings-acl.588/
11. Frank et al. Vision-and-Language or Vision-for-Language? On Cross-Modal Influence in Multimodal Transformers. EMNLP 2021. https://aclanthology.org/2021.emnlp-main.775/
12. Zhang and Nanda. Towards Best Practices of Activation Patching in Language Models: Metrics and Methods. ICLR 2024. https://openreview.net/pdf?id=9eJv5PS27Q
13. PointRefer official code. https://github.com/yl3800/LASO
14. GEAL official code. https://github.com/DylanOrange/geal
15. CMAT/LAS official code. https://github.com/yellowfish0331/CMAT
