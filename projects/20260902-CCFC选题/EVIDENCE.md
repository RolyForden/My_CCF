# Evidence

这里只保留会改变当前选题判断的证据。完整的 20 篇文献矩阵和旧证据账本在 `archive/research_history/`。

## 已核实

| 证据 | 核验范围 | 对当前方向的影响 |
|---|---|---|
| [LASO / PointRefer, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Li_LASO_Language-guided_Affordance_Segmentation_on_3D_Object_CVPR_2024_paper.html) 与 [官方代码](https://github.com/yl3800/LASO) | 论文正文和关键实现 | 数据按 object-affordance 构造，模型已有多尺度 text-point fusion；需先审计同 shape 多 affordance pair 是否真实可用。 |
| [GEAL, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Lu_GEAL_Generalizable_3D_Affordance_Learning_with_Cross-Modal_Consistency_CVPR_2025_paper.html) 与 [官方代码](https://github.com/DylanOrange/GEAL) | 论文正文和关键实现 | 已覆盖多粒度融合与 2D-3D consistency，旧“局部补分辨率”主线不够新。 |
| [LMAffordance3D, CVPR 2025](https://sites.google.com/view/lmaffordance3d) | 正式论文与官方项目页；补充材料 Figure 5 | 已展示保持图像与点云不变、只改变语言指令的 affordance multiplicity；“首次固定几何改变语言”不能成立。 |
| [GLANCE, ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/html/Li_Intermediate_Connectors_and_Geometric_Priors_for_Language-Guided_Affordance_Segmentation_on_ICCV_2025_paper.html) | 论文正文 | 中间层 connector、几何 query 和类别捷径已有研究，不能把 local-global connector 当核心贡献。 |
| [CMAT/LAS, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Huang_Unlocking_3D_Affordance_Segmentation_with_2D_Semantic_Knowledge_CVPR_2026_paper.html) 与 [官方代码](https://github.com/yellowfish0331/CMAT) | 论文正文和关键实现 | 已把瓶颈指向 3D encoder 的语义能力，并提供 prompt、融合点特征和输出层的候选观察位置。 |
| [GroundBench, 2026](https://arxiv.org/abs/2609.13308) | 全文 | 已直接研究 affordance counterfactual diagnosis，因此 CAGE-Pair 和行为指标只能是工具。 |
| [Palit et al., ICCVW 2023](https://openaccess.thecvf.com/content/ICCV2023W/CLVL/html/Palit_Towards_Vision-Language_Mechanistic_Interpretability_A_Causal_Tracing_Tool_for_BLIP_ICCVW_2023_paper.html) | 全文与官方代码入口 | causal tracing 用于 VLM 不是新贡献。 |
| [Same Task, Different Circuits, NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/hash/5fcd540792da599adf1b932624e98f1f-Abstract-Conference.html) | 全文 | “信息到得过晚而无法影响后续位置”的机制叙事已有强近邻，必须证明 point-level spatial selectivity 的不可替代性。 |
| [Vision-Default, Prior-Override, 2026](https://arxiv.org/abs/2606.28273) | 全文 | component-level routing、activation patching 和行为恢复已有范式，不能只搬工具。 |
| [Zhang and Nanda, ICLR 2024](https://openreview.net/pdf?id=9eJv5PS27Q) | 全文 | patching 结论对 metric 与 corruption 选择敏感，因果干预必须包含方向、强度和随机控制。 |

## 尚缺的证据

- LASO test split 中可用 pair 的真实数量、语义关系和 mask overlap 分布。
- Label、Canonical query 与 Natural paraphrase 是否暴露不同 failure；模型是否只做闭集 affordance-label conditioning。
- PointRefer 与 GEAL 官方 checkpoint 在受控 pair 上的 switching 行为。
- query sensitivity 是否在相邻层之间稳定下降，且变化集中在目标差异点集。
- restoration 与 destruction 是否能双向改变 targeted mask switching。
- 2026 年高风险近邻 ThinkAfford、SegWorld 等工作的全文主张级复核。
