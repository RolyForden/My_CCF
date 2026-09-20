---
description: 初始化一个新的科研选题项目目录
---

用户想新建一个科研选题。请先确认（或从参数 `$ARGUMENTS` 推断）选题名称、目标会议、截止日期，然后运行：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\new_topic.ps1 -Name "<名称>" -Venue "<会议>" -Deadline "<YYYY-MM-DD>"
```

创建成功后，读取生成项目的 README.md、STATE.yaml、RESEARCH_CHARTER.md，报告当前阶段、Gate 状态和下一步最小行动。
