from __future__ import annotations
from typing import Any, Dict, List, Optional

def lookup_hardware(hw_db: List[Dict[str, Any]], hw_ids: List[str]) -> List[Dict[str, Any]]:
    index = {h["hw_id"]: h for h in hw_db}
    found: List[Dict[str, Any]] = []
    for hid in hw_ids:
        if hid in index:
            found.append(index[hid])
        else:
            found.append({"hw_id": hid, "missing": True})
    return found
