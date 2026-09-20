# Evidence Ledger

> 当前账本服务于 FocalInspect 根问题重审。`VERIFIED` 只表示来源和对应主张已核，不表示候选 RQ 或方法有效。

| ID | 主张 | 等级 | 来源 | 已读范围 | 直接支持内容 | 日期 | 状态 |
|---|---|---|---|---|---|---|---|
| E-001 | LASO 问题按 58 个 object-affordance 组合构造，每组合 15 个问题 | A | [LASO paper](https://openaccess.thecvf.com/content/CVPR2024/papers/Li_LASO_Language-guided_Affordance_Segmentation_on_3D_Object_CVPR_2024_paper.pdf) | 全文；Sec. 3.1-3.2 | 数据构造、问题数量和固定评测配对 | 2026-09-20 | VERIFIED |
| E-002 | LASO/GEAL 官方 loader 训练随机选择 Question1-14，测试固定 Question0 | A | [LASO code](https://github.com/yl3800/LASO)；[GEAL code](https://github.com/DylanOrange/GEAL) | `data_utils/shapenetpart.py:64-88`；`dataset/laso.py:59-112` | 直接核对问题查找键和 train/test 选择逻辑 | 2026-09-20 | VERIFIED |
| E-003 | PointRefer 已显式处理 affordance region 的多尺度和形状变化 | A | LASO paper | 全文；Sec. 4/4.1 | AFM 在不同解码尺度注入文本并细化点特征 | 2026-09-20 | VERIFIED |
| E-004 | GEAL 已使用 granularity-adaptive fusion 与 2D-3D consistency | A | [GEAL paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Lu_GEAL_Generalizable_3D_Affordance_Learning_with_Cross-Modal_Consistency_CVPR_2025_paper.pdf)；官方代码 | 全文；Sec. 1/3；README 训练评测入口 | 覆盖多粒度、多视图 2D-3D 迁移，且权重与评测入口公开 | 2026-09-20 | VERIFIED |
| E-005 | GLANCE 指出既有 LASO 方法会记忆 category-specific cues，并以 2D mask 几何 query 改善 unseen transfer | A | [GLANCE paper](https://openaccess.thecvf.com/content/ICCV2025/papers/Li_Intermediate_Connectors_and_Geometric_Priors_for_Language-Guided_Affordance_Segmentation_on_ICCV_2025_paper.pdf) | 全文；Intro/Sec. 3/4 | 对旧 global-local 主张构成直接近邻，也提供 shortcut 风险线索 | 2026-09-20 | VERIFIED |
| E-006 | CMAT 将瓶颈定位为 3D encoder 的语义表征能力，并已评测细粒度边界 | A | [CMAT paper](https://openaccess.thecvf.com/content/CVPR2026/papers/Huang_Unlocking_3D_Affordance_Segmentation_with_2D_Semantic_Knowledge_CVPR_2026_paper.pdf)；[code](https://github.com/yellowfish0331/CMAT) | 全文；Intro/Sec. 4 | 旧 proposal 的“加局部语境”不是唯一或最深解释 | 2026-09-20 | VERIFIED |
| E-007 | LMAffordance3D 已研究 full/partial/rotation observation 下的语言多模态 affordance grounding | B | [CVPR 2025 page](https://openaccess.thecvf.com/content/CVPR2025/html/Zhu_Grounding_3D_Object_Affordance_with_Language_Instructions_Visual_Observations_and_CVPR_2025_paper.html) | 官方摘要与实验页面 | partial observation 不能直接作为新 gap | 2026-09-20 | VERIFIED |
| E-008 | GREAT 已研究 open-vocabulary geometry-intention inference | B | [CVPR 2025 page](https://openaccess.thecvf.com/content/CVPR2025/html/Shao_GREAT_Geometry-Intention_Collaborative_Inference_for_Open-Vocabulary_3D_Object_Affordance_Grounding_CVPR_2025_paper.html) | 官方摘要 | intention/geometric reasoning 已拥挤 | 2026-09-20 | VERIFIED |
| E-009 | QueryMe 已使用 adaptive spatial anchors 与 multimodal queries 定位 affordance region | B | [CVPR 2026 page](https://openaccess.thecvf.com/content/CVPR2026/html/Zhao_QueryMe_Query-Driven_Open-Vocabulary_3D_Object_Affordances_Grounding_from_Multimodal_Evidence_CVPR_2026_paper.html) | 官方摘要 | adaptive sampling/query 不是空白 | 2026-09-20 | VERIFIED |
| E-010 | SeqAfford 已把单步/序列指令推理引入 3D affordance segmentation | B | [CVPR 2025 page](https://openaccess.thecvf.com/content/CVPR2025/html/Yu_SeqAfford_Sequential_3D_Affordance_Reasoning_via_Multimodal_Large_Language_Model_CVPR_2025_paper.html) | 官方摘要 | “更复杂语言”本身不能作为新贡献 | 2026-09-20 | VERIFIED |
| E-011 | ThinkAfford 同时针对区域粒度与关系指令混淆 | B | [arXiv:2608.10981](https://arxiv.org/abs/2608.10981) | 官方元数据与摘要 | 是 FocalInspect/SceneFun3D 路线的高风险近邻 | 2026-09-20 | VERIFIED |
| E-012 | SegWorld 区分 target-referential 与 intent-level instruction | B | [arXiv:2605.27764](https://arxiv.org/abs/2605.27764) | 官方元数据与摘要 | 新 RQ 不能泛化宣称“首次研究 intent” | 2026-09-20 | VERIFIED |
| E-013 | BEACON3D 用语言变化和跨任务一致性揭示 3D-VL shortcut | B | [CVPR 2025 paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Huang_Unveiling_the_Mist_over_3D_Vision-Language_Understanding_Object-centric_Evaluation_with_CVPR_2025_paper.pdf) | 官方论文摘要/方法说明 | 支持采用一致性诊断，但任务不是 affordance mask | 2026-09-20 | VERIFIED |
| E-014 | Ref-Adv 表明标准 grounding benchmark 可能不要求语言结构并可用目标改变扰动诊断 | A | [ACL 2020](https://aclanthology.org/2020.acl-main.586/) | 全文 | 反事实语言诊断有成熟先例 | 2026-09-20 | VERIFIED |
| E-015 | GroundBench 已用 factorized inputs 与 counterfactual re-ask 定位 VLM affordance shortcut | A | [arXiv:2609.13308](https://arxiv.org/abs/2609.13308) | 全文；Sec. 3-5 | 已直接占据 affordance 行为反事实诊断，但未分析内部表示链路 | 2026-09-20 | VERIFIED |
| E-016 | 标准 LASO 分数可能无法证明模型因当前指令而选中 mask | D | 由 E-001/E-002 推导 | 待诊断 | 协议可疑不等于模型确实走 shortcut | 2026-09-20 | OPEN |
| E-017 | LASO 可构造足量同 shape、多 affordance、非同质 mask 的反事实配对 | D | 数据规模和 loader 结构线索 | 待数据审计 | 必须统计真实可用 pair 数后确认 | 2026-09-20 | OPEN |
| E-018 | 旧 FocalInspect proposal 科学问题不够尖，应先区分分辨率不足与结构性冲突 | C | 用户提供的导师评价 | 完整评价文本 | 是研究决策输入，不是现象证据 | 2026-09-20 | VERIFIED |
| E-019 | VLM causal tracing 已可通过恢复中间 activation 测试特定状态对输出的因果相关性 | A | [Palit et al., ICCVW 2023](https://openaccess.thecvf.com/content/ICCV2023W/CLVL/html/Palit_Towards_Vision-Language_Mechanistic_Interpretability_A_Causal_Tracing_Tool_for_BLIP_ICCVW_2023_paper.html)；[official code](https://github.com/vedantpalit/Towards-Vision-Language-Mechanistic-Interpretability) | 全文与官方代码入口 | “把 causal tracing 用到 VLM”不是本题的新颖性 | 2026-09-20 | VERIFIED |
| E-020 | Same Task Different Circuits 用 circuit localization 和 later-to-earlier back-patching 发现视觉表示对齐过晚并恢复部分性能差距 | A | [NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/hash/5fcd540792da599adf1b932624e98f1f-Abstract-Conference.html)；[official code](https://github.com/technion-cs-nlp/vlm-circuits-analysis) | 全文；方法、实验与结论 | 与“query signal 到得太晚、无法影响后续位置”抽象叙事高度相邻 | 2026-09-20 | VERIFIED |
| E-021 | Vision-Default 通过 residual/head/MLP activation patching 和 ablation 区分 VLM 中 routing 与 writing components | A | [arXiv:2606.28273](https://arxiv.org/abs/2606.28273)；[official code](https://github.com/nlietzow/vision-default-prior-override) | 全文；Methods/Results | component-level multimodal causal mechanism 已有直接范式 | 2026-09-20 | VERIFIED |
| E-022 | Dual-Pathway Circuits 已跨五个 VLM 用 activation patching、路径分析与 targeted suppression 建立行为到机制干预链 | A | [arXiv:2605.13156](https://arxiv.org/abs/2605.13156) | 全文；方法与结果 | 新工作不能仅靠“行为诊断 + patching”宣称机制新颖性 | 2026-09-20 | VERIFIED |
| E-023 | Modality dominance 已有专门量化指标和 training-free feature editing | A | [Findings ACL 2026](https://aclanthology.org/2026.findings-acl.588/) | 全文 | 新 sensitivity scalar 或 modality dominance 不是核心贡献 | 2026-09-20 | VERIFIED |
| E-024 | Cross-modal input ablation 已被用于测量多模态 transformer 的非对称模态影响 | A | [EMNLP 2021](https://aclanthology.org/2021.emnlp-main.775/) | 全文 | null/ablation 属于成熟行为诊断，不能单独支持内部机制 | 2026-09-20 | VERIFIED |
| E-025 | Activation patching 的定位结论会随评价 metric 与 corruption 方法显著变化 | A | [Zhang and Nanda, ICLR 2024](https://openreview.net/pdf?id=9eJv5PS27Q) | 全文；方法与实验 | D2 必须预注册 metric、patch direction 与多类控制 | 2026-09-20 | VERIFIED |

## 规则

- `A`：全文或官方代码已核，并定位到支持当前主张的章节/实现。
- `B`：官方元数据、摘要或 proceedings 页面已核，尚未完成全文主张级核验。
- `C`：导师意见、转写、截图或二手材料，只作决策线索。
- `D`：待检验假设。
- 仅有 `B/C/D` 的主张不得写成已发现的 failure，也不得据此进入完整实验。
