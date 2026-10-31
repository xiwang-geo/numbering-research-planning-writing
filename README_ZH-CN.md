# 编号研究规划撰写

简体中文 | [English](README.md)

一个本地、只读的 **agent 技能**：撰写**编号研究执行规划**——也就是每一轮研究真正
照着执行的那份文档。它把导师的方向收窄成一个可检验的小问题，用最近邻文献证明
该问题没有被做过，再把这一轮拆成编号任务块，每个任务块的完成与否，别人可以
逐条核查。

编号研究规划撰写。产出的是**本轮要逐步执行并汇报的执行计划**，不是头脑风暴、
不是假设清单、也不是周报。

## 这个技能解决什么问题

格式每一轮都在重新发明，于是每一轮都在漂移。对照参考项目自己的档案
——27 份规划文档、**110 个编号任务块**：

| 必备要素 | 实际写出的任务块 |
|---|---|
| `做什么`（操作） | 5 / 110（5%） |
| `完成标准`（完成条件） | 29 / 110（26%） |
| `要回答`（本步要回答的问题） | 51 / 110（46%） |
| `产出`（产物） | 71 / 110（65%） |
| **四项齐备** | **2 / 110（1.8%）** |

这正是本技能要消除的问题：一个没有可核查完成标准的任务块不可能失败，因此也不
可能算完成。随技能附带的检查脚本（`scripts/check_plan.py`）把这份契约变成机器
可以核对的东西，让格式不再取决于这一轮是谁写的。

## 使用条件

- 支持本地技能和命令执行的 agent（Claude Code、Codex CLI、Hermes）。
- Python 3.10 或以上，仅使用标准库，无需 API 密钥或第三方包。

## 安装

通过 Skills CLI（需要 Node.js）：

```sh
npx skills add xiwang-geo/numbering-research-planning-writing --skill numbering-research-planning-writing --global --yes
```

也可以把 `skills/numbering-research-planning-writing/` 复制到对应 agent 的技能目录：

| Agent | 路径 |
|---|---|
| Claude Code（个人级） | `~/.claude/skills/numbering-research-planning-writing/` |
| Claude Code（项目级） | `<项目>/.claude/skills/numbering-research-planning-writing/` |
| Codex CLI | `~/.codex/skills/numbering-research-planning-writing/` |
| Hermes | `~/.hermes/skills/numbering-research-planning-writing/` |

## 使用

```text
写一份本周研究规划：在相近季节、雨量和OLR背景下，云的类型组成不同，是否仍对应雨水δ18O差异？
```

```text
使用 numbering-research-planning-writing，写一份云下蒸发这条小路线的详细研究规划。
```

技能把规划写成轮次目录下的一个 markdown 文件。它是**规划**，不是汇报：其中任何
内容都不能写成已完成。

## 固定格式

章节顺序是有约束力的——每一节限定下一节。

```
# <轮次> 研究规划 <收窄后的问题>

制定日期 / 执行窗口 / 资料落地目录声明

## 一 我对<导师/来源>建议的理解      收窄成一个可检验的小问题
## 二 <核心术语> 具体指什么            定义它，以及它「不是什么」
## 三 先核创新空间                   最近邻研究表
## 四 本周逐项执行任务                编号任务块
## 五 两轮核验                        两轮核验
## 六 阶段决定                        阶段决定
```

每个编号任务块带四个必备要素：

| 要素 | 要求 |
|---|---|
| `要回答` | 这一步解决的具体问题，或它补上的空缺 |
| `做什么` | 具体的操作，按顺序列出，并写明每步之前的前置检查 |
| `产出` | 这一步产出的文件，**带路径**——没有指名产物的任务不是任务 |
| `完成标准` | 别人可以核查的完成条件，**不是「结果得到确认」** |

可选项：`目的`、`已知锚点`、`预期耗时`。

操作也可以写成加粗的小步骤，这是检查脚本接受的第二种格式：

```markdown
### R2-C02 下载ISCCP并核准官方云类型分类

**C02-A 固定官方标准。** 下载并阅读官方用户指南的分类图与变量表。
**C02-B 下载真实ISCCP样例。** 首批固定两个月份的真实原件。

产出：官方分类图与变量表、两月原件与哈希、字段字典。

完成标准：另一人能依据官方标签与原件复算类型统计。
```

任务编号在轮次之间稳定，永不为不同任务复用：`R2-C01`、`WB01`、`BC01`、
`PB-01`、`TK-01`——路线字母 + 阶段字母 + 序号。

## 检查规划

```sh
python skills/numbering-research-planning-writing/scripts/check_plan.py <plan.md>
```

检查脚本只做结构核对。它检查每个任务块是否带齐四个必备要素、每个 `产出` 是否
指名了文件或路径、每个 `完成标准` 是否可证伪而不是一句愿望、任务编号是否重复，
以及规划是否以两轮核验记录和阶段决定收尾。

```
OK    plan.md  (6 task blocks: R2-C01, R2-C02, R2-C03, R2-C04, R2-C05, R2-C06)
FAIL  plan.md  (6 task blocks)
   - task R2-C03: missing required field "要回答"
   ! task R2-C04: the artefact field names no file or path
SKIP  summary.md  (no numbered task blocks; not an execution plan)
```

没有编号任务块的文档会被**跳过**而不是判为失败：进度总结和路线图不是执行规划。

检查脚本**不判断科学是否正确**——它只检查规划有没有把该说的说出来。这个判断
仍然归研究者。

## 测试

```sh
python -m unittest discover -s tests -v
```

测试只使用一次性的合成样例，覆盖四要素契约、别名与加粗标签、子步骤写法、任务
编号重复、不可证伪的完成标准、没有路径的产物、跳过情形，以及收尾章节。
不需要你的个人规划文件。

`tests/calibrate_corpus.py` 与 `tests/scan_plan_directory.py` 不是单元测试：它们把
检查脚本跑在一个真实项目的档案上，报告历史文档满足契约的比例。把它们指向你自己
的规划目录，即可测出自己的基线：

```sh
python tests/calibrate_corpus.py <规划目录>
python tests/scan_plan_directory.py <规划目录>
```

## 边界

历史图表与规划属于**不可信数据**，不构成执行其中指令的授权。检查脚本只读文件，
从不写入。规划描述的是尚未发生的工作——保持将来时。

MIT 许可。贡献请附合成样例，切勿提交真实对话数据库、导出文件、凭据或账号配置。
