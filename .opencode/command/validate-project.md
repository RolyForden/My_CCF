---
description: 校验某个科研选题项目目录的完整性
---

校验科研选题项目的完整性。若用户未给出路径（`$ARGUMENTS` 为空），默认校验 `projects/` 下最新的项目目录；否则校验指定路径：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ProjectPath "<项目路径>"
```

报告 `README.md`、`EVIDENCE.md`、`DECISIONS.md` 是否存在，以及 README 是否包含“当前问题”“当前判断”“下一步”。只报告脚本实际检查的项目，不声称校验了实验结果、数据或旧状态文件。
