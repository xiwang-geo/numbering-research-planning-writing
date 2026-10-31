"""Tests for the plan checker. Synthetic fixtures only."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/numbering-research-planning-writing/scripts/check_plan.py'
spec = importlib.util.spec_from_file_location('check_plan', SCRIPT)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

GOOD_BLOCK = """
### R2-C01 固定问题并整理旧资料入口

要回答：有哪些已有资料能复用，哪些缺口来自新的类型字段？

做什么：
1. 建立本轮来源索引，登记旧UID与站点坐标。
2. 核对自然月与采样方法，标出采样期未知的记录。

已知锚点：开发期 576 条、历史 325 条。旧面板不能相加当独立样本。

产出：`01_问题与资料/UID与来源索引.csv`、`01_问题与资料/问题登记.md`。

完成标准：每条记录能追到原件及旧用途；本轮问题和旧主张分开。无需重跑旧模型。
"""

GOOD_PLAN = """# 本周研究规划

## 一 我对导师建议的理解

这一轮先做一个小问题。

## 二 云类型具体指什么

光学厚度不是云有多厚。

## 三 先核创新空间

| 最近研究 | 已有内容 |
| --- | --- |
| Wang2020 | 高云覆盖 |

## 四 本周逐项执行任务
""" + GOOD_BLOCK + """
### R2-C02 下载并核准分类

要回答：官方分类口径能否复现到可以进入正式面板的程度？

做什么：
1. 下载官方用户指南，固定分界值。
2. 核对字段名与比例分母。

产出：官方分类图与变量表、两月原件与哈希。

完成标准：另一人能依据官方标签与原件复算类型统计，并写明每个比例的分母。
""" + """
## 五 两轮核验

第一轮核公式、原件、UID、单位与计算。
第二轮核图件、文字、分析身份与结论。

## 六 阶段决定

继续，下一项检验是时间前推。
"""


def write(tmp, text):
    p = Path(tmp) / 'plan.md'
    p.write_text(text, encoding='utf-8')
    return p


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_good_plan_passes(self):
        p = write(self.tmp.name, GOOD_PLAN)
        findings, warnings, stats = cp.check_plan(p)
        self.assertEqual(findings, [], f'unexpected findings: {findings}')
        self.assertEqual(stats['tasks'], 2)
        self.assertEqual(stats['codes'], ['R2-C01', 'R2-C02'])

    def test_missing_required_field_is_reported(self):
        broken = GOOD_PLAN.replace('完成标准：每条记录能追到原件及旧用途；本轮问题和旧主张分开。无需重跑旧模型。', '')
        p = write(self.tmp.name, broken)
        findings, warnings, _ = cp.check_plan(p)
        self.assertTrue(any('完成标准' in f for f in findings), findings)

    def test_vague_completion_criterion_is_reported(self):
        broken = GOOD_PLAN.replace(
            '完成标准：每条记录能追到原件及旧用途；本轮问题和旧主张分开。无需重跑旧模型。',
            '完成标准：分析完成。')
        p = write(self.tmp.name, broken)
        findings, warnings, _ = cp.check_plan(p)
        self.assertTrue(any('unfalsifiable' in f for f in findings), findings)

    def test_artefact_without_path_is_reported(self):
        broken = GOOD_PLAN.replace(
            '产出：`01_问题与资料/UID与来源索引.csv`、`01_问题与资料/问题登记.md`。',
            '产出：结果。')
        p = write(self.tmp.name, broken)
        findings, warnings, _ = cp.check_plan(p)
        self.assertTrue(any('names no file or path' in w for w in warnings), warnings)

    def test_duplicate_task_code_is_reported(self):
        dup = GOOD_PLAN.replace('### R2-C02 下载并核准分类', '### R2-C01 下载并核准分类')
        p = write(self.tmp.name, dup)
        findings, warnings, _ = cp.check_plan(p)
        self.assertTrue(any('duplicate task code' in f for f in findings), findings)

    def test_missing_two_round_verification_is_reported(self):
        broken = GOOD_PLAN.replace('## 五 两轮核验', '## 五 补充说明')
        p = write(self.tmp.name, broken)
        findings, warnings, _ = cp.check_plan(p)
        self.assertTrue(any('two-round verification' in f for f in findings), findings)

    def test_missing_stage_decision_is_reported(self):
        broken = GOOD_PLAN.replace('## 六 阶段决定', '## 六 其他')
        p = write(self.tmp.name, broken)
        findings, warnings, _ = cp.check_plan(p)
        self.assertTrue(any('stage decision' in f for f in findings), findings)

    def test_document_without_task_blocks_is_skipped(self):
        # A progress summary or roadmap is not an execution plan: skip, not fail.
        p = write(self.tmp.name, '# 只有标题\n\n## 一 内容\n')
        findings, warnings, stats = cp.check_plan(p)
        self.assertEqual(findings, [])
        self.assertEqual(stats['kind'], 'not-an-execution-plan')

    def test_sub_step_operations_satisfy_the_operations_field(self):
        sub = GOOD_PLAN.replace(
            '做什么：\n1. 下载并阅读官方用户指南的分类图与变量表，固定气压与光学厚度的分界值。\n2. 首批固定两个月份的真实原件，所有下载与中转留在本轮目录内。\n3. 核对实际字段名、比例分母、缩放与缺失编码；对照合并映射。\n4. 做固定技术站区检查，只核几何、缺失与统计口径，不拟合关系。',
            '**C02-A 固定官方标准。** 下载并阅读官方用户指南的分类图与变量表。\n\n**C02-B 下载真实ISCCP样例。** 首批固定两个月份的真实原件。')
        p = write(self.tmp.name, sub)
        findings, warnings, _ = cp.check_plan(p)
        self.assertFalse(any('做什么' in f for f in findings), findings)

    def test_bold_field_markers_are_accepted(self):
        bold = GOOD_PLAN.replace('要回答：', '**要回答：**').replace('产出：', '**产出：**')
        p = write(self.tmp.name, bold)
        findings, warnings, _ = cp.check_plan(p)
        self.assertEqual(findings, [], f'unexpected findings: {findings}')

    def test_synonym_fields_are_accepted(self):
        syn = GOOD_PLAN.replace('做什么：', '具体操作：')
        p = write(self.tmp.name, syn)
        findings, warnings, _ = cp.check_plan(p)
        self.assertEqual(findings, [], f'unexpected findings: {findings}')

    def test_missing_file_is_reported(self):
        findings, warnings, _ = cp.check_plan(Path(self.tmp.name) / 'nope.md')
        self.assertTrue(findings and 'cannot read' in findings[0])


    def test_task_block_inside_a_code_fence_is_ignored(self):
        # A plan that shows an EXAMPLE block in a fence is not carrying it.
        fenced = '# 标题\n\n```markdown\n' + GOOD_BLOCK + '```\n\n## 五 两轮核验\n\n## 六 阶段决定\n'
        p = write(self.tmp.name, fenced)
        findings, warnings, stats = cp.check_plan(p)
        self.assertEqual(stats['tasks'], 0)
        self.assertEqual(stats['kind'], 'not-an-execution-plan')
        self.assertEqual(findings, [])


if __name__ == '__main__':
    unittest.main()
