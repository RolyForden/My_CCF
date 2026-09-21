# LASO 数据、Pair 与 Query Manifest 执行任务

执行对象：远端算力上的辅助队友  
本轮目标：完成 LASO train/val/test 数据和语言分析，构建真实的同 shape affordance pair，并冻结 val discovery、test confirmation 和第一版 query manifest。

这轮只处理数据，不运行 GEAL 推理，不使用 GPU，也不观察 switching 结果。

## 1. 需要收到的文件

主研究者会把整个 `data_prep/` 目录发给你，其中包含：

```text
audit_laso.py
freeze_manifests.py
laso_tools.py
rules_template.json
tests/
```

远端已有 LASO 数据目录：

```text
/root/autodl-tmp/laso/raw/
```

该目录应包含：

```text
Affordance-Question.csv
anno_train.pkl
anno_val.pkl
anno_test.pkl
objects_train.pkl
objects_val.pkl
objects_test.pkl
```

脚本只读这些文件，不会改写 pickle 或 CSV。

## 2. 放置位置

建议放到：

```bash
/root/autodl-tmp/cage/data_prep/
```

创建本轮输出目录：

```bash
mkdir -p /root/autodl-tmp/cage/data_query_run/audit
mkdir -p /root/autodl-tmp/cage/data_query_run/frozen
```

## 3. 先验证脚本

```bash
cd /root/autodl-tmp/cage/data_prep
python -m unittest discover -s tests -v \
  |& tee /root/autodl-tmp/cage/data_query_run/tests.log
```

预期是 7 个测试全部通过。若测试失败，保留完整日志并停止，不要直接修改测试来获得通过。

## 4. 运行数据和语言分析

```bash
cd /root/autodl-tmp/cage/data_prep
python audit_laso.py \
  --data-root /root/autodl-tmp/laso/raw \
  --output /root/autodl-tmp/cage/data_query_run/audit \
  |& tee /root/autodl-tmp/cage/data_query_run/audit.log
```

脚本会读取三个 split 并生成：

```text
audit/
  source_manifest.json
  schema.json
  split_summary.csv
  annotations.csv
  pairs_all.csv
  pair_type_summary.csv
  pair_review_template.csv
  question_inventory.csv
  template_summary.csv
  issues.csv
  run_summary.json
```

各文件含义：

- `source_manifest.json`：七个原始文件的大小和 SHA256。
- `split_summary.csv`：每个 split 的 annotation、shape、class、affordance 和候选 pair 数。
- `annotations.csv`：每条 annotation 的 shape、类别、affordance、mask 范围和前景比例，不包含原始点数组。
- `pairs_all.csv`：同一 shape 下不同 affordance 的所有候选组合及 GT 差异。
- `pair_type_summary.csv`：每个 class + affordance pair 覆盖的 pair 和独立 shape 数。
- `pair_review_template.csv`：主研究者需要填写的语义组合表，不要求逐样本人工审阅。
- `question_inventory.csv`：Question0–14 的文本、长度、object/affordance 显式出现情况和模板归一化结果。
- `template_summary.csv`：去掉 object/affordance 槽位后的模板统计。
- `issues.csv`：重复 annotation、缺失 object、mask 长度不一致、跨 split shape 重叠等实际问题。

注意：`pairs_all.csv` 是候选组合，不等于最终实验 pair。不要自行删除 mask 相似、样本少或结果看起来异常的组合。

## 5. 第一批回传

数据分析完成后，先把以下内容发回主研究者：

```text
tests.log
audit.log
audit/source_manifest.json
audit/schema.json
audit/split_summary.csv
audit/pair_type_summary.csv
audit/pair_review_template.csv
audit/question_inventory.csv
audit/template_summary.csv
audit/issues.csv
audit/run_summary.json
```

`pairs_all.csv` 和 `annotations.csv` 也要保留在远端；若体积不大，一并打包。不要只发截图或口头总结。

主研究者会根据实际分布返回两个文件：

```text
pair_review.csv
rules.json
```

`pair_review.csv` 以 `class + pair_type` 为单位填写是否纳入以及原因。`rules.json` 记录是否采用 mask 差异阈值、IoU 上限或排除某类 pair。数值为 `null` 表示不按该指标排除。

在收到这两个文件前，不运行 `freeze_manifests.py`，也不启动 query switching。

## 6. 冻结 pair、shape 和 query manifest

收到主研究者返回的文件后，将它们放到：

```text
/root/autodl-tmp/cage/data_query_run/pair_review.csv
/root/autodl-tmp/cage/data_query_run/rules.json
```

然后运行：

```bash
cd /root/autodl-tmp/cage/data_prep
python freeze_manifests.py \
  --audit-dir /root/autodl-tmp/cage/data_query_run/audit \
  --pair-review /root/autodl-tmp/cage/data_query_run/pair_review.csv \
  --rules /root/autodl-tmp/cage/data_query_run/rules.json \
  --output /root/autodl-tmp/cage/data_query_run/frozen \
  --fraction 0.20 \
  --seed 42 \
  |& tee /root/autodl-tmp/cage/data_query_run/freeze.log
```

输出：

```text
frozen/
  pair_manifest.csv
  query_manifest.csv
  discovery20_shapes.json
  discovery_full_shapes.json
  confirmation_shapes.json
  frozen_rules.json
```

其中：

- `pair_manifest.csv` 只包含确认纳入的 val/test pair。
- `discovery20_shapes.json` 是覆盖主要 pair type 的确定性 20% val shape 子集。
- `discovery_full_shapes.json` 是完整 val discovery shape。
- `confirmation_shapes.json` 是 test confirmation shape，只在 discovery 分析完成后使用一次。
- `query_manifest.csv` 为每个纳入的 shape-affordance 生成 `Label` 和 `Canonical` 两种输入，并保存 GEAL 实际需要的 12 个 viewpoint-prefixed strings。
- `frozen_rules.json` 保存输入文件哈希、seed、比例、规则和最终数量，后续行为脚本直接读取它。

第一版 query manifest 暂不加入 paraphrase 和 unsupported query。是否加入 paraphrase 由语言统计决定；unsupported query 需要单独确认“未标注”是否真的表示该 shape 不支持，不能自动假设。

这个 20% 子集用于尽快暴露跨 pair type 的行为问题，不是对真实 failure prevalence 的无偏估计。比例性结论只能使用完整 discovery 结果。

## 7. 需要人工查看的几个数字

完成数据分析后，请在回传说明里直接抄出：

1. train/val/test 的 annotation 数和独立 shape 数；
2. val/test 中拥有至少两个 affordance 的 shape 数；
3. val/test 候选 pair 数以及 class + pair type 数；
4. mask IoU 和 `mean_abs_gt_diff` 的分位数；
5. Question0–14 的独立模板数；
6. object name 和 affordance label 的显式出现率；
7. `issues.csv` 中每种问题的数量；
8. train/val/test 是否存在 shape ID 重叠。

这些数字必须来自生成文件，不要手工估算。

## 8. 本轮不要做的事情

- 不运行 GEAL 或修改 checkpoint；
- 不查看 query switching 输出；
- 不按预测好坏选择 pair；
- 不把 2416 annotation 写成 2416 pair；
- 不自动把所有“未标注 affordance”当作负 query；
- 不生成 paraphrase；
- 不修改 train/val/test；
- 不把 val 和 test 合并后重新随机划分。

## 9. 最终交付

冻结完成后交付：

```text
LASO_DATA_QUERY_DELIVERY/
  DELIVERY.md
  commands.sh
  code/
  tests.log
  audit.log
  freeze.log
  audit/
  pair_review.csv
  rules.json
  frozen/
  SHA256SUMS.txt
```

`commands.sh` 必须是实际运行命令，不是从文档复制但未执行的计划。`DELIVERY.md` 只写完成内容、实际数字、异常和文件位置。最后对交付目录生成 SHA256 清单并打包返回主研究者。
