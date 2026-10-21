"""Source-level guardrails for the public navigation and search interactions."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'src' / 'components' / 'Site.tsx').read_text(encoding='utf-8')
checks = {
    'desktop menu expanded state': 'aria-expanded={openMenu === item.label}',
    'desktop menu opens on keyboard focus': 'onFocus={() => setOpenMenu(item.label)}',
    'desktop menu Escape and trigger focus': "event.key === 'Escape'",
    'mobile toggle expanded state': 'aria-expanded={mobileOpen}',
    'mobile navigation landmark': 'role="navigation" aria-label="Mobile navigation"',
    'mobile Escape handling': 'setMobileOpen(false)',
    'mobile focus entry': "mobileNavRef.current?.querySelector<HTMLAnchorElement>('a')?.focus()",
    'mobile focus restoration': 'mobileTriggerRef.current?.focus()',
    'search dialog semantics': 'role="dialog" aria-modal="true" aria-labelledby="site-search-title"',
    'search focus entry': 'searchInputRef.current?.focus()',
    'search focus restoration': 'searchTriggerRef.current?.focus()',
    'search focus loop': 'querySelectorAll<HTMLElement>',
    'Escape listener': "document.addEventListener('keydown', handleEscape)",
}
missing = [label for label, snippet in checks.items() if snippet not in source]
if missing:
    for label in missing:
        print(f'FAIL: {label}')
    sys.exit(1)
print(f'PASS: {len(checks)} source-level keyboard and accessibility guardrails.')
print('Runtime keyboard behavior still requires a browser interaction check.')
