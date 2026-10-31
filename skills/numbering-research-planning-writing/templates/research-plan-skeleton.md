# Research plan skeleton / 研究规划骨架

A fill-in skeleton for one round's research-execution plan. Copy it, replace the
bracketed prompts, delete the prompts you do not answer — but keep the section
ORDER. The order is load-bearing: each section constrains the next one.

```markdown
# <Round> 研究规划 <the narrowed question>

制定日期：<YYYY-MM-DD>。执行窗口：<start> 至 <end>，可按资料到达情况顺延。

<One or two sentences: what changed since last round, and what this round tests.
If a definition or data source was corrected, say so here and name the v2 change.>

按用户要求，本轮新增资料、代码、结果和核验都保存在 `<round-dir>/`。旧原件及冻结
分析保留在原处，以来源路径和哈希引用，不搬动、不覆盖。

## 一 我对<导师/来源>建议的理解

这一轮先做一个小问题：**<the question, one sentence, with the comparison explicit>**

<What the previous round established. What it did NOT establish — the gap this
question sits in.>

<If several suggestions are on the table: which one this round takes, and why
the others are deferred. One short paragraph.>

## 二 <The central term> 具体指什么

<What it denotes. The source that defines it, with a link.>

<What it does NOT denote — at least one line. The substitutions a reader might
make that would change the conclusion.>

<If the term is a product or a classification: the boundary conditions that
limit it, and what cannot be inferred from it.>

## 三 先核创新空间 不把<method/分类>本身当创新

| 最近研究 | 已有内容 | 我们要避开的重复 | 本轮需要补核 |
| --- | --- | --- | --- |
| <Author year, Journal, DOI> | <what they did> | <what we must not redo> | <what we must read/verify> |

<Direct links to each source.>

**候选贡献只有一项：<one sentence>.** 是否具有发表价值，要看文献核读、资料支持、
效应幅度与稳定性，不能提前保证。

## 四 本周逐项执行任务

### <ROUTE>-<STAGE><NN> <short task name>

要回答：<the specific question this task settles, or the gap it closes.>

做什么：
1. <operation, with the check that must precede it>
2. <operation>

已知锚点：<counts and anchors this task starts from — as anchors, not as
guaranteed sample sizes. What may reduce them.>

产出：<file paths this task creates.>

完成标准：<the checkable condition under which this task is done. Not "the
result is confirmed".>

### <ROUTE>-<STAGE><NN> <short task name>

<...>

## 五 两轮核验

第一轮核：<formula, original files, record IDs, units, computation.>
第二轮核：<figures, prose, analysis identity, conclusions.>

产出：`<round-dir>/03_核验/两轮核验记录.md`

## 六 阶段决定

<The decision: continue (name the next check), stop (state why), or switch
(evidence shown). Not "significant" / "not significant".>
```

## Notes on filling it / 填写说明

- **Section 一 is where the work happens.** If you cannot write the question in
  one sentence with the comparison explicit, you have not narrowed far enough.
  Go back and narrow.
- **Section 三's contribution sentence is conditional on purpose.** If it promises
  publication value, it is wrong — the value is unknown until the literature
  check, the data support, and the effect size are known.
- **Each 产出 names a path.** A task block with no named artefact is a wish, not
  a task.
- **完成标准 is checkable by someone else.** Write the condition, not the hope.
- **Keep the previous version.** When a definition or source changes, the revision
  goes in a `版本记录/` sibling so the earlier plan stays readable.

## Checking the filled plan / 检查填好的规划

```bash
python scripts/check_plan.py <plan.md>
```

The checker verifies structure: every task block carries 要回答 / 做什么 / 产出 /
完成标准, each 产出 names a file, each 完成标准 is falsifiable, task codes are
unique, and the plan closes with 两轮核验 and 阶段决定. Fix what it reports and
run it again. It does not judge whether the science is correct.
