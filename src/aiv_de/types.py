from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, TypedDict

UseCase = Literal["safety_line", "quality_inspection"]

class Veto(TypedDict):
    reason: str
    violated_rules: List[str]

class FeasibilityResult(TypedDict):
    is_possible: bool
    margin: Literal["low", "medium", "high"]
    bottlenecks: List[str]
    suggested_pipeline: List[str]

class PolicyResult(TypedDict):
    passed: bool
    violated_rules: List[str]
    required_controls: List[str]
    hitl_action: Optional[str]

class ArchitectureOption(TypedDict):
    option_id: str
    summary: str
    placement: Dict[str, str]  # component -> edge/onprem/hybrid
    pipeline: List[str]
    hardware: List[str]        # hw_ids
    pros: List[str]
    cons: List[str]
    risks: List[str]
    mitigations: List[str]

class ADR(TypedDict):
    adr_id: str
    title: str
    context: str
    decision: str
    alternatives: str
    assumptions: str
    tradeoffs: str
    risks_and_mitigations: str
    governance: str
    evidence: str
    rollout_plan: str
    consequences: str

class AIVDEState(TypedDict, total=False):
    # inputs
    site_profile: Dict[str, Any]
    hw_db: List[Dict[str, Any]]
    policies: Dict[str, Any]

    # agent outputs
    requirements: Dict[str, Any]
    options: List[ArchitectureOption]
    selected_option: Optional[ArchitectureOption]

    # validator outputs
    feasibility: Optional[FeasibilityResult]
    policy: Optional[PolicyResult]
    vetoes: List[Veto]

    # control
    retries: int
    max_retries: int
    hitl_required: bool

    # artifacts
    run_id: str
    adr: Optional[ADR]
    trace: List[Dict[str, Any]]
    metrics: Dict[str, Any]
