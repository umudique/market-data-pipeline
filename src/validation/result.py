"""Validation result aggregation — single consistent outcome per record/batch."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain import IssueSeverity, ValidationIssue, ValidationStatus


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)
    status: ValidationStatus = ValidationStatus.VALID


class ValidationResultAggregator:
    def aggregate(self, issues: list[ValidationIssue]) -> ValidationResult:
        if not issues:
            return ValidationResult(issues=[], status=ValidationStatus.VALID)
        if any(issue.severity is IssueSeverity.ERROR for issue in issues):
            return ValidationResult(issues=issues, status=ValidationStatus.INVALID)
        return ValidationResult(issues=issues, status=ValidationStatus.FLAGGED)
