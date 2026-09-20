# 工作流状态说明

每个选题项目都有一个 `STATE.yaml`。`stage` 只能使用：

- `INTAKE`
- `LANDSCAPE`
- `IDEA`
- `BASELINE`
- `PILOT`
- `FULL_EXPERIMENT`
- `WRITING`
- `REVIEW`
- `ARCHIVE`

推进阶段时，同时更新：

1. `gate_status`：当前闸门是否通过。
2. `evidence_snapshot`：A/B/C/D 证据数量。
3. `last_decision`：对应 `DECISIONS.md` 中的决策编号。
4. `artifacts`：本阶段新增文件。
5. `blockers`：阻塞项与 owner。

状态文件不是装饰。opencode 每次进入项目应先读它，每次结束应更新它。
