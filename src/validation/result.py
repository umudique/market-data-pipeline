"""Validation result aggregation — single consistent outcome per record/batch."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain import ValidationIssue, ValidationStatus


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)
    status: ValidationStatus = ValidationStatus.VALID


class ValidationResultAggregator:
    def aggregate(self, issues: list[ValidationIssue]) -> ValidationResult:
        raise NotImplementedError
