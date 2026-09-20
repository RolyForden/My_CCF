# CCFC 选题

## 当前问题

在 language-guided 3D affordance grounding 中，当几何保持不变、有效 query 改变时，query-dependent information 是否能传到相关点并驱动正确的 mask switching？如果不能，控制能力在哪个计算环节丢失，该位置是否对输出具有因果作用？

当前把 CAGE 视为测量装置，不是正式方法。正式方法在 failure 和因果位置得到证据前保持空白。

## 当前判断

- **已知**：现有工作已经覆盖多尺度融合、2D-3D consistency、中间层 connector、几何先验和编码器语义增强；“局部放大 + 全局语境 + 蒸馏”不足以构成强问题。
- **邻近风险**：counterfactual affordance diagnosis、VLM causal tracing、activation patching 和 modality routing 已有直接先例。可能剩余的空间是 dense 3D point-level spatial control 的任务特有机制，而不是 patching 工具本身。
- **未知**：LASO 是否有足量且语义有效的同 shape 多 affordance pair；预训练模型是否真实存在 query-insensitive switching failure；内部 query control 是否有稳定、可干预的衰减位置。
- **尚无结果**：没有运行数据审计、baseline 推理、表示定位或因果干预。
- **放弃条件**：数据不能形成可靠 pair；强 baseline 能正确切换；或表示变化与行为之间只能得到相关性、无法形成任务特有的机制结论。

## 约束

- 目标：2027-03 前形成一篇本人能够解释和答辩的投稿稿件，候选会议仍待官方核验。
- 资源：公开数据和代码优先，单卡 RTX 4090，先做无需训练的检查。
- 不做：为指标拼模块、在测试集调参、事后编造 gap、把诊断协议写成实验发现。

## 当前材料

- 当前方案：[Markdown](idea/CAGE_final-idea-report.md) / [PDF](idea/CAGE_final-idea-report.pdf)
- 关键证据：[EVIDENCE.md](EVIDENCE.md)
- 重大转向：[DECISIONS.md](DECISIONS.md)
- 旧 proposal、完整文献矩阵和旧流程文件均在 `archive/` 或根目录 `legacy_workflow/`，默认不读。

## 下一步

先用当前方案与导师讨论。确认研究问题值得继续后，只做 LASO pair 数据可答性审计；在这一步通过前不下载额外模型、不搭训练环境、不设计正式方法。
