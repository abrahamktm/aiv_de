from __future__ import annotations
from typing import Any, Dict, List, Tuple

def _power_ok(site_power_w: int, hw: Dict[str, Any]) -> bool:
    # coarse check: interpret "15-30" as upper bound 30
    pc = hw.get("power_class_w", "0-0")
    try:
        upper = int(str(pc).split("-")[1])
    except Exception:
        upper = 9999
    return upper <= site_power_w

def validate_feasibility(site_profile: Dict[str, Any], selected_option: Dict[str, Any], hw_db: List[Dict[str, Any]]) -> Dict[str, Any]:
    latency = int(site_profile.get("latency_budget_ms", 120))
    use_case = site_profile.get("use_case", "quality_inspection")
    power_budget = int(site_profile.get("power_budget_w", 50))
    cams = int(site_profile.get("line_profile", {}).get("camera_count", 1))
    fps = int(site_profile.get("line_profile", {}).get("fps", 15))
    res = site_profile.get("line_profile", {}).get("resolution_class", "medium")

    hw_index = {h["hw_id"]: h for h in hw_db}
    hw_ids = selected_option.get("hardware", [])
    hw = [hw_index.get(x, {"hw_id": x, "missing": True}) for x in hw_ids]

    bottlenecks: List[str] = []
    if any(h.get("missing") for h in hw):
        bottlenecks.append("unknown_hardware_id")

    if not hw_ids:
        bottlenecks.append("no_hardware_selected")

    # Power feasibility (edge-only cases)
    if any(h.get("class") == "edge" for h in hw):
        if not all(_power_ok(power_budget, h) for h in hw if h.get("class") == "edge"):
            bottlenecks.append("power_budget_exceeded_for_edge_hw")

    # Latency heuristics: very rough
    # Safety_line with <=50ms usually needs edge inference, avoid WAN dependency
    placement = selected_option.get("placement", {})
    if use_case == "safety_line" and latency <= 50:
        if any(v in ["cloud", "hybrid_cloud"] for v in placement.values()):
            bottlenecks.append("safety_latency_incompatible_with_cloud_dependency")

    # Multi-cam high-fps high-res constraints
    if cams >= 12 and fps >= 30 and res == "high" and power_budget <= 30:
        bottlenecks.append("multi_cam_high_res_high_fps_underpowered")

    is_possible = len(bottlenecks) == 0
    margin = "high"
    if not is_possible:
        margin = "low"
    else:
        if (use_case == "safety_line" and latency <= 50 and power_budget <= 30) or (cams >= 10 and res == "high"):
            margin = "medium"

    # Suggested pipeline pattern
    pipeline = selected_option.get("pipeline", [])
    suggested_pipeline = pipeline or ["roi_detection", "tiling_or_downsample", "local_inference", "local_buffer", "telemetry_only"]

    return {
        "is_possible": is_possible,
        "margin": margin,
        "bottlenecks": bottlenecks,
        "suggested_pipeline": suggested_pipeline,
    }
