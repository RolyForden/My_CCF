# CCFC 选题

## 当前问题

在排除闭集标签识别、模板词汇和几何先验后，query 信息能否作为空间选择性的因果信号作用于应改变的三维点？当 mask switching 失败时，是信息消失、未完成点级空间绑定，还是被后续决策环节忽略？

当前把 CAGE 视为测量装置，不是正式方法。方法修复在 failure 和因果机制得到证据前保持空白，而且不是成文的强制条件。

## 当前判断

- **已知**：现有工作已经覆盖多尺度融合、2D-3D consistency、中间层 connector、几何先验和编码器语义增强；“局部放大 + 全局语境 + 蒸馏”不足以构成强问题。
- **邻近风险**：counterfactual affordance diagnosis、VLM causal tracing、activation patching 和 modality routing 已有直接先例。可能剩余的空间是无法被通用 routing 解释替代的 dense 3D point-level spatial control 机制，而不是 patching 工具本身。
- **未知**：LASO 是否有足量且语义有效的同 shape 多 affordance pair；语言是否超出标签模板；GEAL 是否真实存在 query-insensitive switching failure；内部 query 信息是消失、缺少空间绑定、被 decoder 忽略还是分布式冗余。
- **尚无结果**：没有运行数据审计、baseline 推理、表示定位或因果干预。
- **放弃条件**：数据不能形成可靠 pair；强 baseline 能正确切换；或表示变化与行为之间只能得到相关性、无法形成可验证且有预测力的空间机制。

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

先用交叉验证修订后的方案与导师讨论。确认研究问题值得继续后，只做 LASO pair 与语言模板的数据可答性审计；审计通过后优先使用已有官方权重的 GEAL 做行为验证。在这一步通过前不下载额外模型、不搭训练环境、不设计 CAGE-R 或其他正式方法。
