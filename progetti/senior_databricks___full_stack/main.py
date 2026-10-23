# Task: Senior Databricks & Full-Stack Engineer: Build Rule-Based Vendor Account Placement Engine

from dataclasses import dataclass
from typing import List, Callable, Optional

@dataclass
class Vendor:
    vendor_id: str
    region: str
    category: str
    monthly_volume: float
    is_compliant: bool

@dataclass
class PlacementResult:
    vendor_id: str
    account_id: str
    reason: str

class RuleBasedPlacementEngine:
    def __init__(self):
        self.rules: List[Callable[[Vendor], Optional[str]]] = []

    def add_rule(self, rule: Callable[[Vendor], Optional[str]]) -> None:
        self.rules.append(rule)

    def evaluate(self, vendor: Vendor) -> PlacementResult:
        if not vendor.is_compliant:
            return PlacementResult(vendor.vendor_id, "QUARANTINE_ACC", "Non-compliant vendor")
        
        for rule in self.rules:
            result = rule(vendor)
            if result:
                return PlacementResult(vendor.vendor_id, result, f"Matched rule: {rule.__name__}")
        
        return PlacementResult(vendor.vendor_id, "DEFAULT_ACC", "No specific rules matched")

def high_volume_eu_rule(vendor: Vendor) -> Optional[str]:
    if vendor.region == "EU" and vendor.monthly_volume > 100000:
        return "EU_PREMIUM_ACC"
    return None

def tech_category_rule(vendor: Vendor) -> Optional[str]:
    if vendor.category == "Technology":
        return "TECH_SPECIALTY_ACC"
    return None

def process_vendors(vendors: List[Vendor]) -> List[PlacementResult]:
    engine = RuleBasedPlacementEngine()
    engine.add_rule(high_volume_eu_rule)
    engine.add_rule(tech_category_rule)
    
    return [engine.evaluate(v) for v in vendors]
