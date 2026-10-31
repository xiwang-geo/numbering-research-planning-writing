# Task blocks, anchors, and the two-round verification

Depth for the task-block contract. Read this when writing or reviewing task
blocks, when a sample count is disputed, or when setting up the verification
record.

## The four required elements

A task block is finished when it can answer: what question, what operations,
which files, and what "done" means.

### A good task block

```markdown
### R2-C02 下载ISCCP并核准官方云类型分类

要回答：云类型组成能否用官方分类口径复现，核准到可以进入正式面板的程度？

做什么：
1. 下载并阅读官方用户指南的分类图与变量表，固定气压与光学厚度的分界值。
2. 首批固定两个月份的真实原件，所有下载与中转留在本轮目录内。
3. 核对实际字段名、比例分母、缩放与缺失编码；对照合并映射。
4. 做固定技术站区检查，只核几何、缺失与统计口径，不拟合关系。

已知锚点：开发期 576 条、历史 325 条；另有曾检查过的 912 条。旧面板不能相加当
独立样本，以上也不是新共同集的保证数量。

产出：官方分类图与变量表、两月原件与哈希、字段字典、合并映射、站月支持表。

完成标准：另一人能依据官方标签与原件复算类型统计，并写明每个比例的分母及其
观测/估计身份。定义、标签或关键支持未核准时，不进入下一步的正式面板。
```

Note what each element does:

- **要回答** states a question that can be settled by this task, not a topic.
- **做什么** numbers the operations AND the check that precedes each one
  ("核对…对照…"), so a reader can tell whether step 3 was skipped.
- **已知锚点** gives the starting counts and, in the same breath, why they are
  not the expected sample size.
- **产出** names files.
- **完成标准** describes a state another person could verify, and it ends with
  a *gate* — what must NOT happen before the next task may start.

### A broken task block

```markdown
### R2-C02 下载ISCCP并核准官方云类型分类

要回答：云类型数据。
做什么：下载数据并做分析。
产出：结果。
完成标准：分析完成。
```

Why each failure matters:

- "云类型数据" names no question — the task cannot fail, so it cannot finish.
- "下载数据并做分析" has no order and no check, so a reader cannot tell what
  "做分析" covers or what was verified.
- "结果" names no file. A task with no artefact leaves nothing to audit and
  nothing for the next task to build on.
- "分析完成" is unfalsifiable. There is no condition someone else can check.

The checker in `scripts/check_plan.py` rejects all four of these.

## Anchors are not sample sizes

An anchor is a count from a previous round, cited so the next task knows where
it starts. It is not a promise about what the new data will contain.

Three rules:

1. **Do not add anchors across rounds.** Panels built for different questions,
   with different filters, overlap. Their sum is not an independent sample.
2. **State what could reduce the count** in the same sentence as the number:
   records dropped by the new classification, common-set restriction, sampling
   windows that are not yet known.
3. **Never let an anchor become the claim.** "912 条" is a fact about a past
   check; "we have 912 records" is a claim about this round's data.

If the round's data changes the count, the plan says so explicitly and the
difference is reported — "若类型资料删去记录，所有对照在同一新共同集比较，并报告
新旧结果的样本差异".

## Freezing before results

The comparison, the model set, the scoring rule, and the cut-off are written
into the task block BEFORE the numbers exist. Moving a cut-off because the fit
is poor is fitting to the split.

- State the time cut-off as a date and note that the training period is
  everything up to it.
- State the pond/station folds or the holdout rule explicitly (e.g. levels
  1–9 split into {1,4,7} {2,5,8} {3,6,9}).
- Fix the primary endpoint as a continuous quantity, and keep a secondary
  endpoint separate rather than promoting it after the fact.

## The two-round verification record

Two rounds, two different questions, one file.

### Round 1 — mechanics

| Check | How |
|---|---|
| Formulas | re-derive each headline number from the frozen inputs, independently of the analysis script |
| Original files | confirm the source file exists, with its hash, and that the right variable/version was read |
| Record IDs (UID) | confirm every row in the output traces to a source UID; no invented, dropped, or silently-joined ids |
| Units | confirm every stated quantity is in the declared unit, and that the conversion was applied once |
| Computation | re-run the script; compare to the stored output |

Round 1 answers: *is the number correct?*

### Round 2 — identity

| Check | How |
|---|---|
| Figures | every figure regenerates from a script in this round; axes and units match the text |
| Prose | each claim in the write-up matches the computed output — read them side by side |
| Analysis identity | the analysis described is the analysis that ran; the model set, the comparison, the scoring rule are the ones specified in the plan |
| Conclusions | no conclusion is stronger than its interval; an interval crossing zero is 未决, never rounded into "improved" |

Round 2 answers: *does the delivery describe what was actually computed?*

### Rules that apply to both

- **Two rounds means two passes.** Re-reading the same material once and
  describing it as two rounds is not verification.
- **Never let a completion criterion require a favourable result.** The record
  documents what happened; it does not decide whether the hypothesis survived.
  "Not significant" and "reverse of expected" are legitimate, complete outcomes.
- **A gap is a finding.** If a UID cannot be traced, write that it cannot be
  traced — do not quietly drop the row.
- **Record what was NOT verified.** An unverified path listed as unverified is
  honest; an unverified path omitted is a false claim of completeness.

## Figure walkthrough

Every figure produced under the plan gets a walkthrough stating:

- what it **explains**;
- what it **cannot explain** — boundary conditions, sample sparsity, which
  mechanism the plot cannot distinguish;
- the **visual elements** — axis labels, legend entries, colorbar meaning.

Headline numbers without the walkthrough are not a finished deliverable.

## Common review findings

- "分析完成" / "结果合理" as a completion criterion.
- An anchor written as a sample size, or two rounds' anchors summed.
- A cut-off that moved after the fit was seen.
- Task blocks missing 产出, so the round ends with no auditable artefact.
- The verification record that checks only round 1 — numbers correct, prose
  overclaiming, never noticed.
- A stage decision phrased as "significant / not significant" instead of
  "continue / stop / switch", with no next check named.
