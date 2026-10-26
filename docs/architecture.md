# FlakeTrail architecture

The public Cloud Run workbench runs Python 3.14: an owned fixture registry, fresh-process probes, failure-preserving reduction, deletion-minimality checks, authored cleanup/negative-control gates, stateless HTTP and a browser replay interface. Optional browser storage owns saved reports. Only known test IDs execute; no uploaded code, external URL fetch or arbitrary shell execution is accepted. Provider credentials are not forwarded to workers.

The separate private GitLab workflow captures the original owned currency-cache failure in CI. The actual Duo flow runs fixed diagnosis/review commands on Python 3.12.14 and selects the authored cleanup policy. A separate operator step validates the unchanged original CI artifact against fixture/harness fingerprints, promotes only `review-fixture/isolation.json` to a draft MR and runs manual candidate CI on Python 3.14. The candidate pipeline preserves the original failure and passes its blocking repair gate. [Provider records](GITLAB_INTEGRATION.md) identify each source, job and session; main retains the original policy pending review.

## Boundaries and failure handling

Attempt and time limits return partial or unresolved results when exhausted. The reducer preserves the target failure, proves the victim passes alone and checks each deletion. This supports deletion-minimality, not a globally shortest sequence. Candidate acceptance retains tests/assertions across the minimal order and ten seeded full orders; skip-test and missing-cleanup controls must be rejected.

The scenarios are original planted shared-state/environment faults, not a held-out dataset or general model-generated repair. Network nondeterminism and concurrency races are outside scope. Browser diagnosis does not invoke Duo, open MRs, merge or deploy previews. The actual draft candidate remains unmerged; the public workbench has independent release evidence. Keep failed captures and authenticate provider results separately from locally generated JSON. See [public release](LIVE_RELEASE.md) and [review commands](REVIEW_WORKFLOW.md).
