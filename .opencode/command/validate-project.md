---
description: 校验某个科研选题项目目录的完整性
---

校验科研选题项目的完整性。若用户未给出路径（`$ARGUMENTS` 为空），默认校验 `projects/` 下最新的项目目录；否则校验指定路径：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ProjectPath "<项目路径>"
```

报告缺失文件、STATE.yaml 阶段合法性、CSV 表头是否匹配 schema，以及是否通过校验。
