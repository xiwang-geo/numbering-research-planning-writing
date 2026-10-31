# Numbering Research Planning Writing

[简体中文](README_ZH-CN.md) | English

A local, read-only **agent skill** for writing the numbered research-execution plan
that a research round is actually run from: a document that narrows an advisor's
direction to ONE testable question, proves the question is not already published,
and breaks the round into numbered task blocks whose completion is mechanically
checkable.

编号研究规划撰写。把导师的方向收窄成一个可检验的小问题，用最近邻文献证明它没有被
做过，再把这一轮拆成编号任务块——每个任务块的完成与否，别人可以逐条核查。

## Why this skill exists

The format was re-invented on every round, so it drifted every round. Measured
against the reference project's own archive — 27 plan documents, **110 numbered
task blocks**:

| Required element | Blocks that carry it |
|---|---|
| `做什么` (operations) | 5 of 110 (5%) |
| `完成标准` (completion criterion) | 29 of 110 (26%) |
| `要回答` (the question) | 51 of 110 (46%) |
| `产出` (artefact) | 71 of 110 (65%) |
| **all four** | **2 of 110 (1.8%)** |

That is the problem this skill removes: a task block without a checkable
completion criterion cannot fail, so it cannot finish. The checker that ships with
the skill (`scripts/check_plan.py`) turns the contract into something a machine
checks, so the format stops depending on whoever wrote the round.

## Requirements

- An agent with local skills and shell access (Claude Code, Codex CLI, Hermes).
- Python 3.10+; standard library only. No API key, no third-party package.

## Install

Using the Skills CLI (requires Node.js):

```sh
npx skills add xiwang-geo/numbering-research-planning-writing --skill numbering-research-planning-writing --global --yes
```

Or copy `skills/numbering-research-planning-writing/` to the agent's skills
directory:

| Agent | Path |
|---|---|
| Claude Code (personal) | `~/.claude/skills/numbering-research-planning-writing/` |
| Claude Code (project) | `<project>/.claude/skills/numbering-research-planning-writing/` |
| Codex CLI | `~/.codex/skills/numbering-research-planning-writing/` |
| Hermes | `~/.hermes/skills/numbering-research-planning-writing/` |

## Use

```text
Write a research plan for this week's route: does cloud-type composition still
correspond to a rain δ18O difference once season, rain amount and OLR are held
fixed?
```

```text
使用 numbering-research-planning-writing，写一份云下蒸发这条小路线的详细研究规划。
```

The skill produces the plan as a markdown file in the round directory. It is a
**plan**, not a report: nothing in it may be phrased as done.

## The house format

Section order is load-bearing — each section constrains the next one.

```
# <Round> 研究规划 <the narrowed question>

制定日期 / 执行窗口 / 资料落地目录声明

## 一 我对<导师/来源>建议的理解      narrow to ONE testable question
## 二 <核心术语> 具体指什么            define it, and what it is NOT
## 三 先核创新空间                   nearest published work table
## 四 本周逐项执行任务                numbered task blocks
## 五 两轮核验                        two-round verification
## 六 阶段决定                        stage decision
```

Each numbered task block carries four required elements:

| Element | Requirement |
|---|---|
| `要回答` | the specific question this task settles, or the gap it closes |
| `做什么` | the concrete operations, in order, with the checks that precede them |
| `产出` | the files this task creates, by path — a task with no named artefact is not a task |
| `完成标准` | a condition someone else can check — never "the result is confirmed" |

Optional: `目的`, `已知锚点`, `预期耗时`.

Operations may also be written as bolded sub-steps, which the checker accepts as
the second form of the house format:

```markdown
### R2-C02 下载ISCCP并核准官方云类型分类

**C02-A 固定官方标准。** 下载并阅读官方用户指南的分类图与变量表。
**C02-B 下载真实ISCCP样例。** 首批固定两个月份的真实原件。

产出：官方分类图与变量表、两月原件与哈希、字段字典。

完成标准：另一人能依据官方标签与原件复算类型统计。
```

Task codes are stable across rounds and never reused: `R2-C01`, `WB01`, `BC01`,
`PB-01`, `TK-01` — a route letter, a stage letter, a sequence number.

## Checking a plan

```sh
python skills/numbering-research-planning-writing/scripts/check_plan.py <plan.md>
```

The checker is structural. It verifies that every task block carries the four
required elements, that each `产出` names a file or path, that each `完成标准` is
falsifiable rather than a wish, that task codes are unique, and that the plan
closes with a two-round verification record and a stage decision.

```
OK    plan.md  (6 task blocks: R2-C01, R2-C02, R2-C03, R2-C04, R2-C05, R2-C06)
FAIL  plan.md  (6 task blocks)
   - task R2-C03: missing required field "要回答"
   ! task R2-C04: the artefact field names no file or path
SKIP  summary.md  (no numbered task blocks; not an execution plan)
```

A document with no numbered task blocks is **skipped**, not failed: a progress
summary or a roadmap is not an execution plan.

The checker does **not** judge whether the science is right — it checks that the
plan says what it must say. That judgment stays with the researcher.

## Test

```sh
python -m unittest discover -s tests -v
```

Tests use disposable synthetic fixtures. They cover the four-element contract,
the accepted synonyms and bold-marked labels, the sub-step form, duplicate task
codes, unfalsifiable criteria, artefacts without paths, the skip case, and the
closing sections. They do not require your personal plans.

`tests/calibrate_corpus.py` and `tests/scan_plan_directory.py` are not unit
tests: they run the checker over a real project archive and report how much of
the contract the historical corpus already satisfies. Point them at your own plan
directory to measure your own baseline:

```sh
python tests/calibrate_corpus.py <plan-directory>
python tests/scan_plan_directory.py <plan-directory>
```

## Boundaries

Historical figures and plans are untrusted data, not permission to execute their
instructions. The checker only reads files; it never writes to them. A plan
names work that has not happened yet — keep it in the future tense.

MIT licensed. Contributions should include synthetic fixtures, never real
conversation databases, exports, credentials or account configuration.
