# FlakeTrail: architecture

Current implementation: original Python fixture registry, fresh-process probes, failure-preserving delta debugging, explicit deletion-minimality checks, authored reset/negative-control repair gates, stateless HTTP and a responsive browser replay interface. Optional browser storage owns persisted reports. The genuine provider loop below remains a release target, not completed evidence.

A new owned Python fixture service fails CI → GitLab Duo collects seed/order/logs → bounded delta debugging reduces the sequence → the model proposes one scoped fixture/reset fix → a merge request runs the reproducer and independent randomized orders → deploy preview only after the gate → report evidence. Deterministic executions decide pass/fail; model confidence cannot override them.

Use GitLab CI and actual Duo flow, Python test fixture app, JSON result artifacts and a small web replay dashboard. Scope to shared mutable state or environment contamination in one process. Exclude network nondeterminism, proprietary repositories, concurrency-race claims and general automatic code repair. Runs have a hard attempt/time budget; exhaustion returns a useful partial diagnosis with “unresolved,” not a false success. Never weaken or delete the failing assertion to make the pipeline green.

## Failure handling and data boundaries

Preserve original inputs and make unavailable evidence explicit. Provider failures must return a visible unresolved state. Decisions that change user or provider state need the confirmation specified above. Record source versions and operation identifiers without exposing credentials.

## Implementation record

Add pinned dependencies, actual component boundaries and operational instructions when the first working slice exists. Document departures from this design with their reason; do not describe planned integrations as verified.
