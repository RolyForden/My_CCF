# CCFC 选题

> 状态：已冻结（2026-09-22）。核心行为假设未成立，不再追加实验；可复用资产和负结果继续保留。

## 当前问题

当前 CAGE 机制主线停止，不进入表示定位或因果干预。冻结的 20% val discovery 上，GEAL 能随 Label/Canonical query 明显切换 point-level mask，没有发现支撑“query control 系统性丢失”的行为现象。

CAGE 仍可作为一次数据与行为测量记录保留，但不再作为当前论文方向。

## 当前判断

- **已知**：现有工作已经覆盖多尺度融合、2D-3D consistency、中间层 connector、几何先验和编码器语义增强；“局部放大 + 全局语境 + 蒸馏”不足以构成强问题。
- **邻近风险**：counterfactual affordance diagnosis、VLM causal tracing、activation patching 和 modality routing 已有直接先例。可能剩余的空间是无法被通用 routing 解释替代的 dense 3D point-level spatial control 机制，而不是 patching 工具本身。
- **行为结论**：冻结的 74 个 val shape、133 个 pair 共运行 386 条 query。预测变化相对 GT 变化的中位比例为 Label `0.75`、Canonical `1.19`，两种条件均无 response ratio `<0.1` 的近零变化 pair。两端单 query 均达到 `SIM >= 0.5` 时，BCA 分别为 `95.7%`（90/94）和 `96.7%`（87/90）。
- **剩余错误**：合格 pair 中只剩 Label 4 对、Canonical 3 对 BCA 失败，集中于少量 bottle/chair/table shape，且预测变化并不接近零。这更像局部预测错误或目标相似性问题，不能支撑系统性的 query-insensitive mechanism。
- **已有实验结果**：GEAL commit `3048bb8` 与官方 LASO seen checkpoint 已完成完整 test evaluation。2416 个 annotation、1035 个 shape 的 BS8/BS32 指标分别为 aIoU `0.225/0.226`、AUC `0.868/0.869`、SIM `0.632/0.632`、MAE `0.096/0.096`；2416×2048 的逐点 prediction/GT 已导出，直接重算 MAE 一致，交付清单 20/20 哈希通过。该结果只支持“官方 evaluation 与导出链路可用”，不支持 query switching failure 或任何机制结论。
- **数据审计结果**：官方 LASO train/val/test 共 `16,120/1,215/2,416` 条 annotation、`6,883/516/1,035` 个独立 shape，split 间无 shape ID 重叠。val/test 原始同 shape 多 affordance 候选为 `986/1,953` 对；在任何 switching 输出产生前，已冻结 `mean_abs_gt_diff >= 0.05` 且二值 mask IoU `<= 0.95`，得到 val discovery `650` 对、test confirmation `1,278` 对。20% discovery 固定为 74 个 val shape、133 对，覆盖 26 种 affordance pair type 和 18 个类。870 条问题中有 654 条不同原文、260 种归一化模板，affordance label 显式出现率为 `39.9%`；因此首轮 manifest 同时保留 Label 与官方 Canonical 条件。
- **复现边界**：旧 baseline 报告把 2416 个 annotation 误称为 pair；当前 pair 已由独立数据审计重新构建，本轮 val discovery 也已按新 manifest 重新推理。test confirmation 从未读取，完整 val 未运行，因为 20% 筛查已触发停止条件。
- **停止决定**：强 baseline 在冻结 discovery 上能够正确切换，已触发预先写明的停止条件。不运行完整 val、test confirmation、D1/D2 或方法修复。

## 约束

- 目标：2027-03 前形成一篇本人能够解释和答辩的投稿稿件，候选会议仍待官方核验。
- 资源：公开数据和代码优先；今天可集中使用 5 张 GPU，优先并行完成 20% 筛选、全量确认和条件性机制实验。
- 不做：为指标拼模块、在测试集调参、事后编造 gap、把诊断协议写成实验发现。
- 交付：辅助队友和外部算力只负责运行与打包，不 commit/push；原始交付物由主研究者带回本仓库，经讨论确认后再提交。

## 当前材料

- 当前进度说明：[CURRENT_STATUS.md](CURRENT_STATUS.md)
- 当前方案：[Markdown](idea/CAGE_final-idea-report.md) / [PDF](idea/CAGE_final-idea-report.pdf)
- 当前实验协议与交付要求：[experiments/README.md](experiments/README.md)
- 队友实验总览：[TEAMMATE_EXPERIMENT_GUIDE.md](experiments/TEAMMATE_EXPERIMENT_GUIDE.md)
- 当前数据与 manifest 任务：[LASO_DATA_QUERY_EXECUTION.md](experiments/LASO_DATA_QUERY_EXECUTION.md)
- 关键证据：[EVIDENCE.md](EVIDENCE.md)
- 重大转向：[DECISIONS.md](DECISIONS.md)
- 完整文献矩阵和旧证据账本在 `archive/research_history/`，默认不读；旧 proposal 与旧流程由 Git 历史保存。
- 原始实验交付包另存于 `Z:\科研总控台opencode-archive\projects\20260902-CCFC选题\CAGE_20260922\`，不进入 Git。

## 下一步

关闭 CAGE/query-insensitive mechanism 主线，保留数据审计、冻结 manifest 和负结果。下一轮从新的可观察问题重新选题，不围绕这 3-4 个局部错误追加指标或模块。
