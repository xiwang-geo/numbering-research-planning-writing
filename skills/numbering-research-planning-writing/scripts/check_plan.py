#!/usr/bin/env python3
"""Check a numbered research plan against the task-block contract.

Usage:
    python check_plan.py <plan.md> [more.md ...]

Exit code 0 = every task block is well formed and the plan carries the required
closing sections. Exit code 1 = findings were reported. Exit code 2 = usage or
I/O error.

The checker is deliberately structural: it verifies that each numbered task
block names a question, an operation, an artefact and a checkable completion
condition, and that the plan closes with a two-round verification record and a
stage decision. It cannot judge whether the science is right.
"""
import argparse
import os
import re
import sys

# Field labels, with the accepted synonyms this house format actually uses.
FIELD_ALIASES = {
    'question': ('要回答', '重点回答', '这一项回答', '回答'),
    'operations': ('做什么', '具体操作', '操作', '方法'),
    'artefact': ('产出', '输出'),
    'criteria': ('完成标准', '完成条件', '验收标准', '通过条件'),
}
OPTIONAL_ALIASES = ('目的', '已知锚点', '预期耗时', '前置条件', '注意', '为什么做')

# A field line. The real documents use every one of these shapes:
#   做什么：...            (plain label, colon outside)
#   **要回答：** ...        (bold label, colon INSIDE the bold)
#   **产出：** ...          (bold label, colon inside)
#   - **重点回答** ...      (bold label, bullet, colon outside)
# so the colon is matched on either side of the closing bold marker.
# Every alias of a kind is one alternative inside one pattern — building one
# pattern per alias and overwriting by kind would silently keep only the last.
def _kind_pattern(kind):
    alternatives = '|'.join(re.escape(a) for a in FIELD_ALIASES[kind])
    return re.compile(r'^\s*(?:[-*+]\s*)?(?:\*\*)?(?:' + alternatives + r')(?:\*\*)?\s*[:：]')


FIELD_RE = {kind: _kind_pattern(kind) for kind in FIELD_ALIASES}
ANY_FIELD_RE = [_kind_pattern(kind) for kind in FIELD_ALIASES]
ANY_FIELD_RE += [re.compile(r'^\s*(?:[-*+]\s*)?(?:\*\*)?' + re.escape(a) + r'(?:\*\*)?\s*[:：]')
                 for a in OPTIONAL_ALIASES]

# A task-block heading. Real forms:
#   ### R2-C01 固定问题并整理旧资料入口
#   ### R2-Q01 把问题、样本用途和有限模型登记好
#   ### WB04 先看水预算是否说得通
#   ### PB-01：冻结来源并建立可追溯数据字典（第1天，约2小时）
TASK_HEADING = re.compile(
    r'^#{2,4}\s+(?P<code>[A-Za-z]{1,4}[0-9]{1,2}(?:-[A-Za-z0-9]{1,4})?)'
    r'[:：]?\s*(?P<title>\S.*)$')

# A sub-step marker is an alternative way to write the operations. Real form:
#   **C02-A 固定官方标准。** 下载并阅读NOAA用户指南...
#   **C02-B：** 下载真实ISCCP样例。...
SUB_STEP = re.compile(
    r'^\s*(?:[-*+]\s*)?(?:\*\*)?'
    r'(?:[A-Z]{1,3}[0-9]{1,2}-[A-Z0-9]{1,3}|[A-Z]{1,3}[0-9]{1,2})'
    r'(?:\*\*)?\s*[:：]?')

# A field line: optional bold markers, optional list marker, then "标签："
def field_pattern(label):
    return re.compile(r'^\s*(?:[-*]\s*)?(?:\*\*)?' + re.escape(label) + r'(?:\*\*)?\s*[:：]')

# Completion criteria that are unfalsifiable.
VAGUE_CRITERIA = ('分析完成', '结果合理', '做完了', '完成了', '分析做好', '结果正确',
                  '跑通即可', '得到结果', '完成分析')

# An artefact should look like a path or a file name.
ARTEFACT_PATH = re.compile(r'[\\/][^\s、，。；;]+|`[^`]+`|\b[\w.-]+\.(md|csv|xlsx|json|py|png|svg|pdf|docx)\b')


def parse_blocks(lines):
    """Return the task blocks found in a document.

    Lines inside fenced code blocks are ignored: a plan that shows an EXAMPLE
    task block in a fence is not itself carrying that block.
    """
    blocks, current = [], None
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_fence = not in_fence
            if current is not None:
                current['body'].append(line)
            continue
        if in_fence:
            if current is not None:
                current['body'].append(line)
            continue
        m = TASK_HEADING.match(line)
        if m:
            if current:
                current['end'] = i
                blocks.append(current)
            current = {'code': m.group('code'), 'title': m.group('title').strip(),
                       'start': i, 'end': len(lines), 'body': []}
        elif current is not None:
            current['body'].append(line)
    if current:
        blocks.append(current)
    return blocks


def fields_in(body, kind):
    """Indices of body lines that start a field of this kind.

    Every occurrence is returned: the continuation boundaries of one field are
    the start of the next field of ANY kind, so a single-kind scan is not
    enough to slice the body.
    """
    pattern = FIELD_RE[kind]
    return [(idx, kind) for idx, line in enumerate(body) if pattern.match(line)]


def field_text(body, hits):
    """Map kind -> concatenated text of that field (label line + continuations)."""
    out = {}
    for pos, (idx, kind) in enumerate(hits):
        end = hits[pos + 1][0] if pos + 1 < len(hits) else len(body)
        chunk = body[idx:end]
        text = chunk[0]
        for cont in chunk[1:]:
            if cont.strip() and not field_pattern_any(cont):
                text += ' ' + cont.strip()
        out.setdefault(kind, text.strip())
    return out


def field_pattern_any(line):
    return any(p.match(line) for p in ANY_FIELD_RE)


def check_plan(path):
    findings, warnings = [], []
    try:
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
    except OSError as exc:
        return [f'cannot read {path}: {exc}'], [], {}

    lines = text.splitlines()
    blocks = parse_blocks(lines)

    if not blocks:
        # Not an execution plan (a progress summary, a roadmap, a narrative
        # memo). There is nothing to enforce, so this is a skip, not a failure.
        return [], [], {'tasks': 0, 'codes': [], 'kind': 'not-an-execution-plan'}

    seen_codes = {}
    for b in blocks:
        code, where = b['code'], f"task {b['code']}"
        if code in seen_codes:
            findings.append(f'{where}: duplicate task code (also used at line {seen_codes[code] + 1})')
        else:
            seen_codes[code] = b['start']

        body = b['body']
        present = {}
        # Collect every field start in body order, then slice the body by them:
        # a field's text runs until the NEXT field of any kind starts.
        all_hits = []
        for kind in FIELD_ALIASES:
            all_hits.extend(fields_in(body, kind))
        all_hits.sort()
        for kind in FIELD_ALIASES:
            kind_hits = [h for h in all_hits if h[1] == kind]
            if kind_hits:
                present.update(field_text(body, kind_hits))
            elif kind == 'operations' and any(SUB_STEP.match(l) for l in body):
                # Operations written as bolded sub-steps (**C02-A 固定官方标准。**)
                # is the second accepted form of the house format.
                present['operations'] = '(sub-steps)'
            else:
                findings.append(f'{where}: missing required field '
                                f'"{FIELD_ALIASES[kind][0]}"')

        # The question must actually be a question, not a topic.
        q = present.get('question', '')
        if isinstance(q, dict):
            q = next(iter(q.values()), '')
        if q and len(re.sub(r'[^一-鿿A-Za-z0-9]', '', q)) < 6:
            findings.append(f'{where}: the question field is too short to be a real question: {q[:40]!r}')

        # The artefact field must name a file. In this house format 89 of 97
        # real 产出 fields carry an explicit path; the ones that do not are a
        # deviation worth flagging, but they are a warning rather than a
        # structural failure.
        art = present.get('artefact', '')
        if isinstance(art, dict):
            art = next(iter(art.values()), '')
        if art and not ARTEFACT_PATH.search(art):
            warnings.append(f'{where}: the artefact field names no file or path')

        # The completion criterion must be checkable, not a wish.
        crit = present.get('criteria', '')
        if isinstance(crit, dict):
            crit = next(iter(crit.values()), '')
        if crit:
            for bad in VAGUE_CRITERIA:
                if bad in crit and len(re.sub(r'[^一-鿿A-Za-z0-9]', '', crit)) < 12:
                    findings.append(f'{where}: completion criterion is unfalsifiable ({bad!r})')
                    break

    # Required closing sections.
    if not re.search(r'两轮核验|两轮自查|两轮检查', text):
        findings.append('plan has no two-round verification section (两轮核验)')
    if not re.search(r'阶段决定|阶段收尾|下一步决定', text):
        findings.append('plan has no stage decision section (阶段决定)')

    stats = {'tasks': len(blocks), 'codes': sorted(seen_codes)}
    return findings, warnings, stats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('plans', nargs='+', help='plan markdown file(s) to check')
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    total = 0
    for path in args.plans:
        findings, warnings, stats = check_plan(path)
        name = os.path.basename(path)
        if stats.get('kind') == 'not-an-execution-plan':
            print(f'SKIP  {name}  (no numbered task blocks; not an execution plan)')
            continue
        if findings:
            total += len(findings)
            print(f'FAIL  {name}  ({stats.get("tasks", 0)} task blocks)')
            for f in findings:
                print(f'   - {f}')
        else:
            print(f'OK    {name}  ({stats.get("tasks", 0)} task blocks: '
                  f'{", ".join(stats.get("codes", []))})')
        for w in warnings:
            print(f'   ! {w}')
    return 1 if total else 0


if __name__ == '__main__':
    raise SystemExit(main())
