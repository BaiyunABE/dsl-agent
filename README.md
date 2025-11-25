# DSL Agent

本仓库为一个轻量的 Python 原型工程，实现了一个简单的领域专用语言（DSL）执行器与示例代理。仓库包含 DSL 引擎、与 LLM 的客户端接口、示例脚本以及测试用例，便于实验与扩展。

项目结构

- `src/`
  - `dsl_engine.py` — DSL 的解析与执行核心逻辑
  - `llm_client.py` — 与语言模型（LLM）交互的简易封装
  - `main.py` — 示例运行入口 / 可用作 CLI
  - `script.dsl` — 示例 DSL 脚本
  - `test_dsl_engine.py` — 引擎单元测试
  - `test_dsl_engine_e2e.py` — 端到端测试

快速开始

先决条件

- Python 3.10 及以上（推荐）
- `pip`

创建虚拟环境并安装依赖（如有）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # 如果仓库中提供了 requirements.txt
pip install -U pytest
```

运行示例程序：

```powershell
python src\main.py
```

如果 `main.py` 需要额外参数，请查看文件顶部的说明或直接打开文件阅读用法说明。

运行测试：

```powershell
pytest -q
# 或运行单个测试文件
pytest src\test_dsl_engine.py -q
```

使用说明

- `script.dsl` 是示例脚本，可用于快速验证引擎行为。
- 若要扩展语法或增加新指令，请优先阅读并修改 `dsl_engine.py`。
- `llm_client.py` 为一个可替换的轻量接口：根据你使用的 LLM 服务（例如 OpenAI、Hugging Face、私有模型）调整实现与密钥管理方式。

贡献指南

- 有想法或遇到问题请先打开 issue 讨论。
- 提交代码变更请 fork 仓库，新建分支并提交包含测试的 PR。

许可证

- 本仓库当前未包含许可证文件。请选择适合的开源许可证并添加 `LICENSE` 文件（例如 MIT、Apache-2.0 等）。

作者与联系方式

- 仓库拥有者：`BaiyunABE`

可选改进（我可以替你完成）：
- 根据源码分析生成 `requirements.txt` 并添加到仓库；
- 添加 GitHub Actions 工作流以在 push 时自动运行 `pytest`；
- 为 `src\main.py` 增加 `--help` 或更完善的 CLI 帮助信息。

如果你希望我继续其中一项，请告诉我你想先做哪一项。
