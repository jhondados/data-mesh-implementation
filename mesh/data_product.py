"""Data Product base class for Data Mesh."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from great_expectations.core import ExpectationSuite

@dataclass
class DataContract:
    schema_version: str
    fields: List[Dict]  # [{name, type, nullable, description}]
    sla_freshness_hours: int = 24
    sla_quality_score: float = 0.99
    owner_team: str = ""
    consumers: List[str] = field(default_factory=list)

@dataclass  
class DataProduct:
    name: str
    domain: str
    description: str
    contract: DataContract
    bigquery_table: str
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)

    def validate_contract(self, df) -> Dict:
        """Validate data against contract using Great Expectations."""
        import great_expectations as gx
        context = gx.get_context()
        suite = context.add_expectation_suite(f"{self.name}_suite")
        results = {"product": self.name, "validation_time": str(datetime.now()),
                   "passed": True, "issues": []}
        for field_def in self.contract.fields:
            if not field_def.get("nullable", True):
                null_count = df[field_def["name"]].isnull().sum()
                if null_count > 0:
                    results["issues"].append(f"{field_def['name']}: {null_count} nulls (not allowed)")
                    results["passed"] = False
        return results
