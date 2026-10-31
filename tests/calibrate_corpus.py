"""Calibrate the plan checker against a real archive of plan documents.

Usage:
    python calibrate_against_corpus.py <plan-directory> [--pattern "*规划*.md"]

Real documents are read-only inputs. This measures how much of the house
contract the historical corpus already satisfies, which is the baseline the
skill is meant to raise. Point it at your own plan directory to measure your
own baseline.
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

    blocks_total = blocks_full = 0
    doc_pass = doc_fail = doc_skip = 0
    missing = Counter()

    for p in paths:
        findings, warnings, stats = cp.check_plan(p)
        if stats.get('kind') == 'not-an-execution-plan':
            doc_skip += 1
            continue
        doc_fail += 1 if findings else 0
        doc_pass += 0 if findings else 1

        lines = open(p, encoding='utf-8', errors='replace').read().splitlines()
        for b in cp.parse_blocks(lines):
            blocks_total += 1
            have = {k for k in cp.FIELD_ALIASES if cp.fields_in(b['body'], k)}
            if 'operations' not in have and any(cp.SUB_STEP.match(l) for l in b['body']):
                have.add('operations')
            if len(have) == 4:
                blocks_full += 1
            else:
                for k in ('question', 'operations', 'artefact', 'criteria'):
                    if k not in have:
                        missing[k] += 1

    print(f'plan documents scanned: {len(paths)}  '
          f'({doc_skip} are not execution plans and were skipped)')
    print(f'execution plans: {doc_pass + doc_fail}   passing the checker: {doc_pass}')
    print(f'total task blocks: {blocks_total}')
    print(f'blocks satisfying all four required elements: {blocks_full} '
          f'({100.0 * blocks_full / max(blocks_total, 1):.1f}%)')
    print('\nmissing-element frequency across all task blocks:')
    for k, v in missing.most_common():
        print(f'  {k:12} absent in {v:4d} of {blocks_total} blocks '
              f'({100.0 * v / max(blocks_total, 1):.1f}%)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
