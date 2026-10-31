"""Run the plan checker over a directory of plan documents and report the results.

Usage:
    python check_real_plans.py <plan-directory> [--pattern "*规划*.md"]

The directory is scanned read-only; nothing is written to the documents.
"""
import argparse
import glob
import importlib.util
import os
from collections import Counter
from pathlib import Path
import sys

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/numbering-research-planning-writing/scripts/check_plan.py'
spec = importlib.util.spec_from_file_location('check_plan', SCRIPT)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('directory', help='directory holding plan markdown files')
    ap.add_argument('--pattern', default='*规划*.md', help='glob pattern (default: %(default)s)')
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    paths = sorted(set(glob.glob(os.path.join(args.directory, '**', args.pattern), recursive=True)))
    if not paths:
        print(f'no files matching {args.pattern!r} under {args.directory}')
        return 2

    print(f'plan documents found: {len(paths)}\n')
    kinds = Counter()
    examples = []
    for p in paths:
        findings, warnings, stats = cp.check_plan(p)
        if stats.get('kind') == 'not-an-execution-plan':
            kinds['SKIP'] += 1
            print(f'  SKIP   {os.path.basename(p)[:56]}  (not an execution plan)')
            continue
        if findings:
            kinds['FAIL'] += 1
            print(f'  FAIL   {stats.get("tasks", 0):3d} tasks, {len(findings):3d} findings  '
                  f'{os.path.basename(p)[:40]}')
            for f in findings:
                examples.append((os.path.basename(p)[:44], f.split(':', 1)[-1].strip()))
        else:
            kinds['OK'] += 1
            print(f'  OK     {stats.get("tasks", 0):3d} tasks  {os.path.basename(p)[:56]}')

    print(f'\n=== summary ===\n  {kinds["OK"]} pass, {kinds["FAIL"]} fail, {kinds["SKIP"]} skip '
          f'(of {len(paths)})')
    if examples:
        print('\n=== finding types (most common first) ===')
        for t, n in Counter(t for _, t in examples).most_common(12):
            print(f'  {n:4d}  {t}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
