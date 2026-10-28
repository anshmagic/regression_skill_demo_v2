# select-regression-tests/SKILL.md

## Purpose
Select the minimum safe regression test set for an enterprise application change using business impact, criticality, dependencies, historical defects, and existing test coverage.

## When to use
Use after an SAP transport, application release, configuration change, API change, or defect fix has been identified and before regression execution begins.

## Inputs
- Change ID and change description
- Changed component or SAP object, when known
- Business process
- Existing test inventory
- Test criticality
- Automation status
- Historical defects, when available
- Dependency and integration information, when available

## Procedure
1. Summarize the change in business terms.
2. Identify directly affected business processes and components.
3. Identify meaningful upstream and downstream dependencies.
4. Determine business risk: Critical, High, Medium, or Low.
5. Review the deterministic pre-score supplied for each existing test.
6. Select existing tests that cover directly affected functionality, critical downstream processes, high-risk integrations, financial controls, and historical defect areas.
7. Defer tests with no meaningful relationship to the change, but explain exclusions for Critical or High tests.
8. Identify important business risks with no adequate test coverage.
9. Recommend new scenarios for identified coverage gaps.
10. Route selected tests:
   - AUTOMATED -> TOSCA
   - MANUAL -> MANUAL
   - HYBRID -> HYBRID
11. Produce a concise regression recommendation with evidence and a confidence score.

## Selection rules
Always include a test when one or more of the following is true unless there is clear evidence it is irrelevant:
- The changed component is directly covered.
- The test protects a Critical business process.
- The change can affect pricing, billing, revenue, accounting, payment, or another financial control.
- A downstream dependency is High or Critical risk.
- Similar changes have caused defects previously.

## Guardrails
- Do not delete or modify approved tests.
- Do not invent existing test IDs.
- Clearly distinguish selected, deferred, and newly recommended tests.
- High-risk financial process recommendations require human review.
- AI may recommend a new scenario, but must not claim it already exists in Tosca.
- Automated and manual tests must both be considered.

## Required output
Return STRICT JSON:

{
  "change_summary": "string",
  "impacted_processes": ["string"],
  "overall_risk": "Critical|High|Medium|Low",
  "selected_tests": [
    {
      "test_id": "existing test id",
      "reason": "short explanation",
      "risk_score": 0,
      "execution_route": "TOSCA|MANUAL|HYBRID"
    }
  ],
  "deferred_tests": [
    {
      "test_id": "existing test id",
      "reason": "short explanation"
    }
  ],
  "coverage_gaps": [
    {
      "gap": "missing coverage",
      "recommended_scenario": "new test scenario",
      "suggested_route": "TOSCA|MANUAL|HYBRID"
    }
  ],
  "human_review_required": true,
  "confidence": 0.0,
  "executive_summary": "2-4 sentence summary"
}

## Success criteria
- All identified Critical risks are covered by selected tests or explicitly identified as coverage gaps.
- Every selected test has a clear rationale.
- Existing test IDs are never fabricated.
- Output distinguishes automated Tosca execution from manual execution.
- Financial-impact changes require human review.
