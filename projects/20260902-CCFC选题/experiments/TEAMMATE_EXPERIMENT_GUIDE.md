# CAGE 实验总体设计与协作说明

更新日期：2026-09-21  
阅读对象：参与远端运行、代码实现和结果整理的辅助队友

这份文档只解释我们现在研究什么、实验为什么这样安排、你需要负责什么以及最终交付什么。你不需要阅读本地工作流、历史 proposal 或项目管理文件。

## 1. 我们现在研究什么

任务是 language-guided 3D affordance grounding：给定一个三维物体和一句功能查询，模型需要在点云上标出与查询对应的功能区域。

我们当前关心的问题不是“GEAL 的总体分割指标还能不能提高”，而是：

> 对同一个三维物体，只改变有效的 affordance query 时，模型能否把语言变化正确传递到应该改变的点，并让输出 mask 随之切换？

例如，同一扇门可以对应 `open`、`push` 和 `pull`。理想情况下，query 改变后，预测变化应集中在与新功能相关的区域，而不是继续输出近似相同的几何前景。

如果模型无法正确切换，我们还要继续问：

1. 不同 query 进入文本编码器后是否已经过于相似？
2. 文本差异是否在跨模态融合中被几何特征压弱？
3. 模型是否知道 query 变了，但变化没有送到相关点上？
4. 点级表示已经包含正确差异，但 decoder 最终仍按几何或类别先验输出？

目前没有预设答案，也没有预设要发明哪一种新模块。CAGE 只是这套测量和干预实验的工作名，不是已经成立的方法。

## 2. 已经完成了什么

GEAL 官方代码和 LASO seen checkpoint 已经在远端跑通：

- GEAL commit：`3048bb8c859b04b3d7569e2bc186f9880c7109ab`
- checkpoint SHA256：`0163519dcf732cf9c9a4db176f8df79b7c207e0ee14a1324988f714eb4b4191e`
- LASO seen test：2416 个 annotation、1035 个 shape
- BS8：aIoU `0.225`、AUC `0.868`、SIM `0.632`、MAE `0.096`
- BS32：aIoU `0.226`、AUC `0.869`、SIM `0.632`、MAE `0.096`
- 2416×2048 的 prediction 和 ground truth 已成功导出，无 NaN/Inf

这说明官方 evaluation 和逐点预测导出可以使用，后面不需要再次从零复现 baseline。

需要特别纠正：2416 是 annotation/sample 数，不是我们需要的 query pair 数。当前导出也只用了 test split 的 `Question0`，所以尚未运行 query switching、表示定位或因果干预。

## 3. 整体实验逻辑

接下来的实验依次回答四个问题。

### 3.1 数据能否支持问题

先确认 LASO 中是否真的存在足够多的“同一个 shape、不同 affordance、GT 区域有可比较差异”的样本。

这一部分不是为了追求一个漂亮的 pair 数，而是避免把以下情况误认为模型 failure：

- 两个 affordance 的 GT 本来几乎相同；
- 两个词在该物体上存在包含、层级或语义歧义；
- 某类 pair 只来自一个物体类别；
- annotation 重复或 shape 对齐错误；
- 官方自然语言实际上只是 affordance label 的固定模板。

### 3.2 改变 query 后，输出是否正确切换

在固定点云 `P` 上分别运行两个合法查询：

```text
(P, q_a) -> prediction_a
(P, q_b) -> prediction_b
```

我们先看单个 query 本来是否预测合格，再看 query 改变后输出是否朝正确区域变化。模型本来就预测错误的样本不能直接算作 query-control failure。

行为结果至少要区分：

- 应增强区域：从 affordance A 切到 B 后，B 对应区域是否提高；
- 应抑制区域：A 对应而 B 不对应的区域是否降低；
- 不应变化区域：无关点是否被大范围扰动；
- 双向切换：A→B 和 B→A 是否都合理；
- 语言形式：label、官方问题和同义改写是否表现一致。

### 3.3 Query 信息在哪个环节失去空间控制

只有确认稳定的行为现象后，才记录模型内部表示。观察位置按功能划分：

1. text encoder 输出；
2. cross-modal fusion 输出；
3. decoder 前的 point representation；
4. decoder 输入和输出。

这里不是简单比较“哪一层 cosine 更小”，而是看 query 引起的差异是否出现在 GT 应改变的点上，以及这种空间选择性从哪里开始消失。

最终可能出现五种情况：query 本身塌缩、融合后衰减、无法绑定到点、decoder 忽略，或者信息分散在多条路径中而没有单一位置。

### 3.4 定点改变内部信号，输出是否随之改变

如果上一部分找到明确候选位置，再做内部干预：

- 把 query B 的候选信号放入 query A 的运行中，看输出能否朝 B 的正确区域恢复；
- 做反方向 B→A；
- 在原本能正确切换的样本中破坏该信号，看正常行为是否受损；
- 与随机向量、同义改写和空间错位注入比较；
- 改变干预强度，观察效果是否稳定而非一次偶然。

恢复有效但破坏无效，只能说明这条路径足以改变结果，不能说明正常模型实际依赖它。我们需要把内部变化和最终点级行为联系起来，而不是只展示一张层间距离图。

## 4. 现在立刻要做的工作

当前应完成“数据分析与样本构建”，然后运行第一批行为实验。暂时不做 hook、activation patching、训练或新方法。

### 4.1 LASO 数据分析

只读处理 train、val、test 三个 split，输出：

- 每个 split 的 annotation、独立 shape、class 和 affordance 数量；
- shape、object 和 annotation 的对应关系；
- 重复项、缺失项以及跨 split 的 shape 重叠；
- 每个 shape 拥有的 affordance 集合；
- 同 shape 不同 affordance 的候选组合；
- 每组候选的 GT mask IoU、前景比例和 `mean(abs(mask_b-mask_a))`；
- 每种 affordance 组合覆盖多少独立 shape 和物体类别。

请保留全部候选，不要先按模型结果挑样本。对于高频组合，另外生成少量可视化或 point index 摘要，方便主研究者判断语义是否可比较。

### 4.2 语言内容分析

读取 `Affordance-Question.csv`，回答：

- object name 和 affordance label 是否直接出现在问题中；
- Question0–14 有多少独立模板；
- 去掉 object/affordance 槽位以后还剩多少句式；
- 同一 affordance 在不同 object 上是否只是重复模板；
- 官方问题是否包含超出闭集 label 的有效语言信息。

这一结果决定后面是否值得加入 paraphrase。不要现在用 LLM 批量生成改写。

### 4.3 构造实验清单

主研究者会根据上述分布确认哪些 pair 在语义上可比较。随后生成：

```text
pair_manifest.parquet
query_manifest.parquet
discovery20_shapes.json
discovery_full_shapes.json
confirmation_shapes.json
frozen_rules.yaml
```

建议用 val 做 discovery、test 做一次 confirmation。20% 子集按 shape 抽样并覆盖主要 affordance 组合，不能按 annotation 随机截取。test 结果不能用于反复修改阈值、pair 类型或排除规则。

### 4.4 第一批行为推理

清单确认后，每个 `(shape, query)` 只运行一次并保存逐点 prediction。四张 GPU 可以按 shape 分成互斥 shard，并在汇总时检查没有重复或遗漏。

查询输入分为：

- `Label`：只输入 affordance label；
- `Canonical`：LASO 官方问题；
- `Paraphrase`：只有语言分析表明值得研究时才加入；
- `Unsupported`：正确 object 加一个该 shape 不支持、但语法合法的 affordance，用来检查类别先验。

还要计算 object-only 或类别-affordance prior 作为参照，但不要把这些控制条件与合法 affordance switching 混成一个总分。

第一批先运行冻结的 20% discovery shapes。结果如果表现出稳定且跨 shape 的错误切换，再扩展到完整 discovery 和一次 confirmation；如果模型本身能正确切换，就不继续做内部机制实验。

## 5. 行为结果需要保存什么

逐样本结果至少包含：

```text
sample_id
shape_id
class
affordance_a / affordance_b
query_condition
query_text
prediction
ground_truth
point_count
checkpoint_sha256
geal_commit
```

汇总结果包括：

- 官方 aIoU、AUC、SIM、MAE；
- 每个 query 的单独表现；
- query A/B 的预测变化量；
- 双向切换是否正确；
- 应增强、应抑制和不应变化区域的定向变化；
- 近零预测变化比例及对应的 GT 变化量；
- 按 class、affordance pair、mask IoU 和区域大小分组的结果；
- Label、Canonical、Paraphrase 分开报告。

不要只交总体均值。后续需要从汇总表回到具体 shape、query 和逐点数组。

## 6. 两个人如何配合

主研究者负责：

- 确认哪些 affordance pair 在语义上可比较；
- 确认 discovery/confirmation、排除规则和输入条件；
- 解释实验结果并决定研究方向；
- 把最终确认的代码和结论提交到主仓库。

辅助队友负责：

- 在远端读取 LASO、实现数据统计和推理脚本；
- 使用固定的 GEAL commit、checkpoint、split 和 evaluator 运行；
- 保存真实命令、代码、配置、日志和机器可读结果；
- 报告实现错误、环境偏差和未完成项，不替主研究者选择最有利样本或解释论文结论。

你不需要 commit 或 push 主仓库。需要改 GEAL 时，优先使用外部薄包装器；如果确实修改官方文件，请保留 diff 并说明原因。

## 7. 算力安排

在五张 GPU 可用时，推荐这样分配：

| 资源 | 当前工作 | 行为现象确认后的工作 |
|---|---|---|
| CPU | 数据、语言、pair 和 manifest | 汇总统计与可视化 |
| GPU 0 | 完整 baseline 复核或导出一致性 | clean-run 复核 |
| GPU 1–4 | 20% / full behavior 的 shape shards | 分功能位置记录表示 |

不要为了让 GPU 保持占用而提前训练、扫层或运行第二模型。数据分析和清单没有确认前，GPU 可以空闲。

## 8. 本轮明确不做什么

- 不训练或微调 GEAL；
- 不修改 test split、GT mask 或官方 evaluator；
- 不根据模型输出重新抽取“更好看”的 20% 子集；
- 不提前生成大量 paraphrase；
- 不开始 activation hook、patching 或 layer sweep；
- 不加入 paired loss、router、binding module 或 decoder 改造；
- 不运行第二个 baseline；
- 不把 baseline 跑通写成 query-control 假设成立。

## 9. 最终交付给主研究者的内容

每轮任务结束后，请交付一个完整目录或压缩包。至少包括：

```text
DELIVERY.md               本轮做了什么、没做什么、出现了什么偏差
commands.sh               实际运行过的完整命令，包括环境变量
code/                     本轮新增的脚本
code_patch.diff           若修改过官方仓库；没有修改则附 git status
configs/                  实际使用的配置
manifests/                shape、pair、query 和 shard 清单
logs/                     stdout/stderr 原始日志
metrics/                  CSV/JSON/Parquet 等机器可读结果
sample_outputs/           少量可人工检查的 prediction/GT/可视化
remote_large_files.csv    未打包的大文件路径、大小、SHA256、保留期限
SHA256SUMS.txt            包内关键文件校验值
```

大型 prediction、activation、数据集和 checkpoint 可以留在远端，但必须在 `remote_large_files.csv` 写明绝对路径和保留期限。不要只交 Markdown 报告，也不要只发终端截图。

`DELIVERY.md` 用普通语言写清以下内容即可：

```text
完成的任务：
实际运行命令：
使用的代码、数据和 checkpoint：
主要数字与样本数：
输出文件位置：
失败、警告或协议偏差：
仍未完成的内容：
```

## 10. 如何理解接下来的结果

这轮实验可能得到几种不同答案：

- 数据无法构成可靠的同 shape 多 affordance 比较：当前问题需要换数据或停止；
- 数据可用，但语言只是 label 模板：研究对象应收缩为 prompt/label-conditioned spatial control；
- GEAL 能正确随 query 切换：不再围绕 GEAL 构造 failure；
- 只有特定类别或特定 pair 出错：先解释该混淆，不泛化成统一机制；
- 出现稳定且无法由 GT、类别或模板解释的错误切换：再进入内部表示和因果干预。

因此，当前最重要的不是尽快跑出一个方法，而是把“数据是否可答”和“行为现象是否真实”两件事做清楚。后面的表示分析、因果干预和方法设计都依赖这两步。
