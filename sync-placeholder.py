#!/usr/bin/env python3
"""
Syncs GROUPS_PLACEHOLDER and KNOCKOUT_PLACEHOLDER in dashboard.html
from the current dashboard_data.json.

Run after every update to dashboard_data.json that changes results,
analysisTips, or injuries — before git add/commit.

Usage: python3 sync-placeholder.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / 'dashboard_data.json'
HTML_FILE = ROOT / 'dashboard.html'


def js_val(v):
    """Convert a Python value to a JS literal (single-quoted strings)."""
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    # String: escape backslashes and single quotes
    s = str(v).replace('\\', '\\\\').replace("'", "\\'")
    return f"'{s}'"


def match_line(m, is_ko=False):
    """Render a single match object as a compact JS object literal."""
    fields = []
    if is_ko:
        fields.append(f"id:{js_val(m.get('id'))}")
    fields += [
        f"date:{js_val(m.get('date'))}",
        f"home:{js_val(m.get('home'))}",
        f"away:{js_val(m.get('away'))}",
        f"tip:{js_val(m.get('tip'))}",
        f"analysisTip:{js_val(m.get('analysisTip'))}",
        f"conf:{js_val(m.get('conf'))}",
        f"result:{js_val(m.get('result'))}",
        f"injuries:{js_val(m.get('injuries'))}",
        f"note:{js_val(m.get('note'))}",
    ]
    return '    { ' + ', '.join(fields) + ' },'


def build_groups_placeholder(groups):
    lines = ['const GROUPS_PLACEHOLDER = {']
    for key, grp in groups.items():
        # Escape any single quotes in the teams string
        teams = grp['teams'].replace("'", "\\'")
        lines.append(f"  {key}: {{ teams: '{teams}', matches: [")
        for m in grp['matches']:
            lines.append(match_line(m))
        lines.append('  ]},')
    lines.append('};')
    return '\n'.join(lines)


def build_knockout_placeholder(knockout):
    lines = ['const KNOCKOUT_PLACEHOLDER = {']
    for round_key, matches in knockout.items():
        lines.append(f'  {round_key}: [')
        for m in matches:
            lines.append(match_line(m, is_ko=True))
        lines.append('  ],')
    lines.append('};')
    return '\n'.join(lines)


def main():
    with open(DATA_FILE, encoding='utf-8') as f:
        data = json.load(f)

    groups_js   = build_groups_placeholder(data['groups'])
    knockout_js = build_knockout_placeholder(data['knockout'])

    html = HTML_FILE.read_text(encoding='utf-8')

    # Replace GROUPS_PLACEHOLDER block (lazy match, DOTALL)
    html, n_groups = re.subn(
        r'const GROUPS_PLACEHOLDER = \{.*?\n\};',
        groups_js,
        html,
        flags=re.DOTALL,
    )
    if n_groups != 1:
        print(f'ERROR: Expected 1 GROUPS_PLACEHOLDER match, got {n_groups}', file=sys.stderr)
        sys.exit(1)

    # Replace KNOCKOUT_PLACEHOLDER block
    html, n_ko = re.subn(
        r'const KNOCKOUT_PLACEHOLDER = \{.*?\n\};',
        knockout_js,
        html,
        flags=re.DOTALL,
    )
    if n_ko != 1:
        print(f'ERROR: Expected 1 KNOCKOUT_PLACEHOLDER match, got {n_ko}', file=sys.stderr)
        sys.exit(1)

    HTML_FILE.write_text(html, encoding='utf-8')
    print(f'✅ Placeholder sync complete  ({len(data["groups"])} Gruppen, {sum(len(v) for v in data["knockout"].values())} KO-Matches)')


if __name__ == '__main__':
    main()
