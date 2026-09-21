# 当前进度说明

更新日期：2026-09-21

## 一句话结论

我们原本想研究“GEAL 在 query 改变后，point-level prediction 仍然不变”的机制问题。第一轮真实实验显示：**GEAL 通常能够随 query 正确改变预测，这个核心现象没有成立。**

因此当前最合理的动作是停止 CAGE/query-insensitive mechanism 方向，而不是继续做内部表示分析或为少数错误追加模块。

## 原来想验证什么

我们怀疑同一个三维物体面对不同 affordance query 时，模型可能主要依赖物体几何和类别先验，导致 query 从文本编码器传到 point-level mask 的过程中失去控制力。

例如，对同一把刀分别询问 `grasp` 和 `cut`：

- 正常情况：预测应分别切换到手柄和刀刃；
- 假设中的失败：query 虽然改变，预测却几乎不变。

只有先观察到这种失败，后续研究“信息在哪一层消失”才有意义。

## 已经完成的工作

### 1. 官方 GEAL baseline 已跑通

- 使用 GEAL 官方代码 commit `3048bb8`；
- 使用官方 LASO seen checkpoint；
- 完成完整 test evaluation 和逐点预测导出；
- 结果约为 aIoU `0.226`、AUC `0.869`、SIM `0.632`、MAE `0.096`；
- 这一步证明模型、数据、checkpoint 和推理链路能够正常工作。

### 2. LASO 数据已经审计

- train/val/test 分别有 `6,883 / 516 / 1,035` 个 shape；
- 三个 split 没有 shape ID 重叠；
- val/test 最初得到 `986 / 1,953` 个同 shape、不同 affordance 候选 pair；
- 约三分之一候选 pair 的两个 GT 区域几乎没有空间差异，不能用于判断模型是否切换。

因此在查看任何 switching 结果前，我们固定了两个数据条件：

```text
两个 GT 的平均绝对差异 >= 0.05
两个二值 GT mask 的 IoU <= 0.95
```

过滤后保留：

- val：650 个 pair、370 个 shape；
- test：1,278 个 pair、719 个 shape。

### 3. 已完成 20% val 行为筛查

为了快速判断课题是否值得继续，我们从 val 固定出：

- 74 个 shape；
- 133 个有效 pair；
- 193 个不同的 shape-affordance 输入；
- 每个输入分别运行 `Label` 和官方自然语言 `Canonical`，共 386 条 query。

这里没有使用 test，也没有根据预测结果重新选择样本。

## 实验结果怎么理解

我们主要看两个直观问题。

### 预测有没有随着 query 改变

`response ratio` 表示“预测变化量 / GT 变化量”。如果它接近 0，说明 GT 要求换区域，但模型预测几乎没动。

结果：

| Query 条件 | response ratio 中位数 | 接近零的 pair |
|---|---:|---:|
| Label | 0.75 | 0 / 133 |
| Canonical | 1.19 | 0 / 133 |

也就是说，模型不仅在变化，而且变化幅度并不小。

### 改变后的预测方向是否正确

BCA 的直观含义是：询问 A 时预测更接近 A 的 GT，询问 B 时预测更接近 B 的 GT。

只看两个单 query 本身都预测尚可（两端 `SIM >= 0.5`）的 pair：

| Query 条件 | 合格 pair | 正确切换 | BCA |
|---|---:|---:|---:|
| Label | 94 | 90 | 95.7% |
| Canonical | 90 | 87 | 96.7% |

剩余错误只有 Label 4 对、Canonical 3 对，集中在少量 bottle、chair 和 table shape。它们的预测也发生了明显变化，只是没有正确对应两个 GT，因此更像局部预测错误或两个目标区域相似，而不是“模型没有接收到 query”。

## 这意味着什么

当前证据不支持下面这条论文主线：

> GEAL 中的 query information 在某个内部环节系统性衰减，导致 point-level mask 无法随 query 切换。

如果继续做逐层 probing、activation patching 或新 routing 模块，就会变成先决定做机制方法，再从少量错误中寻找理由。这正是我们此前希望避免的研究方式。

这次结果不是论文结果，也不能证明所有模型都没有 query-control 问题。它只说明：**在当前 LASO + GEAL 组合上，这个现象不够强，不能支撑我们继续投入。**

## 尚未做的工作

以下工作是有意停止，而不是遗漏：

- 没有运行完整 val switching；
- 没有查看 test confirmation；
- 没有做内部表示逐层追踪；
- 没有做 activation patching 或其他因果干预；
- 没有设计新的 loss、routing 或 decoder；
- 没有形成可投稿的新方法。

原因是最便宜的前置现象检查已经没有通过。继续这些工作预计不会提高研究价值，只会增加时间成本。

## 现在还需要做什么

当前方向不需要补实验。下一步需要的是研究决策，而不是继续运行：

1. 确认接受这次负结果，正式关闭 CAGE/query-insensitive mechanism 主线；
2. 保留 GEAL 环境、LASO 数据审计、pair 构建和 switching 脚本，供后续新问题复用；
3. 重新寻找一个先有可观察 failure、再谈机制和方法的新问题。

不推荐为了挽救当前方向去跑完整 val 或 test，也不推荐围绕 3-4 个错误样本重新包装故事。

## 可复用资产

- `experiments/data_prep/`：LASO 数据、语言和 pair 审计工具；
- `experiments/run_switching_minimal.py`：最小 GEAL switching 推理脚本；
- `experiments/results/geal_switching20_summary.json`：本轮核心结果；
- `experiments/runs/laso_data_query_20260921/`：完整数据审计产物，本地忽略目录；
- `experiments/runs/switching20_20260921/`：逐点预测、逐 query 指标和逐 pair 结果，本地忽略目录；
- `Z:\科研总控台opencode-local-cache\switching20_result.zip`：远端回收包。

## 当前等待的决定

你只需要判断一件事：是否接受“当前核心现象没有成立，因此停止该方向”。在这个判断确认前，不再启动新的实验。
