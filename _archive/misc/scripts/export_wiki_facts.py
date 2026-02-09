#!/usr/bin/env python3
"""Export Wikipedia facts from knowledge store to static KB format."""

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from adan.knowledge_store import get_knowledge_store

def export_facts():
    store = get_knowledge_store()
    facts = store.get_all()
    
    lines = []
    lines.append('')
    lines.append('# ═══════════════════════════════════════════════════════════════════════════════')
    lines.append('# WIKIPEDIA SCRAPED FACTS')  
    lines.append('# Auto-generated from Newton Wiki Scraper')
    lines.append('# Source: Wikipedia (CC BY-SA)')
    lines.append('# ═══════════════════════════════════════════════════════════════════════════════')
    lines.append('')
    lines.append('WIKIPEDIA_FACTS: Dict[str, tuple] = {')
    lines.append('    # Format: key: (fact, category, source_url)')
    
    seen_keys = set()
    for f in facts:
        # Clean key
        key = f.key.strip()
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)
        
        # Escape for Python string
        key_safe = key.replace('\\', '\\\\').replace('"', '\\"')
        fact_safe = f.fact.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')[:400]
        url = (f.source_url or '#').replace('\\', '\\\\').replace('"', '\\"')
        cat = f.category or 'General'
        
        lines.append(f'    "{key_safe}": ("{fact_safe}", "{cat}", "{url}"),')
    
    lines.append('}')
    lines.append('')
    
    return '\n'.join(lines), len(seen_keys)


if __name__ == "__main__":
    code, count = export_facts()
    
    # Write to a file
    output_path = Path(__file__).parent.parent / "adan" / "wikipedia_facts.py"
    
    header = '''#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
WIKIPEDIA FACTS DATABASE
Auto-scraped verified facts from Wikipedia

These facts extend the main knowledge base with Wikipedia content.
Scraped using Newton Wiki Scraper with diff-based deduplication.
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Dict

'''
    
    output_path.write_text(header + code, encoding='utf-8')
    print(f"Exported {count} facts to {output_path}")
