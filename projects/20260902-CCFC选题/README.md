# CCFC 选题

## 当前问题

在排除闭集标签识别、模板词汇和几何先验后，query 信息能否作为空间选择性的因果信号作用于应改变的三维点？当 mask switching 失败时，是信息消失、未完成点级空间绑定，还是被后续决策环节忽略？

当前把 CAGE 视为测量装置，不是正式方法。方法修复在 failure 和因果机制得到证据前保持空白，而且不是成文的强制条件。

## 当前判断

- **已知**：现有工作已经覆盖多尺度融合、2D-3D consistency、中间层 connector、几何先验和编码器语义增强；“局部放大 + 全局语境 + 蒸馏”不足以构成强问题。
- **邻近风险**：counterfactual affordance diagnosis、VLM causal tracing、activation patching 和 modality routing 已有直接先例。可能剩余的空间是无法被通用 routing 解释替代的 dense 3D point-level spatial control 机制，而不是 patching 工具本身。
- **未知**：LASO 是否有足量且语义有效的同 shape 多 affordance pair；语言是否超出标签模板；GEAL 是否真实存在 query-insensitive switching failure；内部 query 信息是消失、缺少空间绑定、被 decoder 忽略还是分布式冗余。
- **已有初步结果**：辅助队友已回传 GEAL + LASO seen 的 20% 子集报告；493/2416 pair 的推理链路成功完成，重复运行指标一致。该结果按博士经验记为工程筛选通过；原始日志和产物仍需归档，尚未运行 query switching、表示定位或因果干预。
- **放弃条件**：数据不能形成可靠 pair；强 baseline 能正确切换；或表示变化与行为之间只能得到相关性、无法形成可验证且有预测力的空间机制。

## 约束

- 目标：2027-03 前形成一篇本人能够解释和答辩的投稿稿件，候选会议仍待官方核验。
- 资源：公开数据和代码优先；今天可集中使用 5 张 GPU，优先并行完成 20% 筛选、全量确认和条件性机制实验。
- 不做：为指标拼模块、在测试集调参、事后编造 gap、把诊断协议写成实验发现。
- 交付：辅助队友和外部算力只负责运行与打包，不 commit/push；原始交付物由主研究者带回本仓库，经讨论确认后再提交。

## 当前材料

- 当前方案：[Markdown](idea/CAGE_final-idea-report.md) / [PDF](idea/CAGE_final-idea-report.pdf)
- 当前实验协议与交付要求：[experiments/README.md](experiments/README.md)
- 关键证据：[EVIDENCE.md](EVIDENCE.md)
- 重大转向：[DECISIONS.md](DECISIONS.md)
- 完整文献矩阵和旧证据账本在 `archive/research_history/`，默认不读；旧 proposal 与旧流程由 Git 历史保存。

## 下一步

按今日五卡任务书先归档 20% baseline 原始产物，同时完成 LASO pair/语言审计和逐点预测导出；随后用冻结的 20% shape 子集筛选 query switching。20% 现象通过后才跑全量 discovery/confirmation，行为确认后才进入表示定位和因果干预。
