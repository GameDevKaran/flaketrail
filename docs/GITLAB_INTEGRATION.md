# Verified GitLab failure-review workflow

26 October 2026 IST. [Private GitLab project](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail) (ID 87890207) preserves the development history also held in the private GitHub repository. The public diagnosis workbench executes owned scenarios; the authenticated Duo/CI/MR chain below runs separately in GitLab. Public browser diagnosis does not itself invoke Duo or create an MR.

## Actual provider chain

| Stage | Verified record | Result |
|---|---|---|
| Original CI capture | [Pipeline 2986651575](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/pipelines/2986651575), [job 17449122880](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/jobs/17449122880) | Source `1766153e211153226e2b0b32bbd72e6be05bae12`; the owned order fails default_checkout's USD assertion with expected exit 1. |
| Duo diagnosis | [Session 10031632](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/automate/agent-sessions/10031632), [job 17457981783](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/jobs/17457981783) | Completed on source `b55e937a6ecfe811c560c59ed77c90e4b340a8db`; capture, reduction, authored proposal/application and finite verification succeeded. |
| Operator promotion | [Draft MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/merge_requests/1), branch `review/duo-cleanup-10031632` | Only `review-fixture/isolation.json` changes resetAfterEach from false to true. Candidate `883229409d95e75a4217647b43ff62cb1b8d92e8`. |
| Candidate CI | [Pipeline 2988163158](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/pipelines/2988163158) | Successful manual web pipeline on that exact candidate. |
| Baseline and repair jobs | [capture_original_failure](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/jobs/17458108540), [verify_reviewed_repair](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/jobs/17458108541) | Capture retains the expected failure; the blocking repair job succeeds with unchanged assertions. |

Duo created a fresh capture in its provider sandbox and diagnosed set_eur leaking EUR into default_checkout. Its own command output did not authenticate the earlier CI reference. The separate promotion step used the downloaded authentic original CI capture: fixture/harness fingerprints matched the candidate base, the original failure replayed, and the fixed propose/verify gate passed. The operator committed the policy, opened the draft MR and ran candidate CI. Duo did not create the MR, merge or deploy it.

## Evidence and limits

The actual Duo runtime was Python 3.12.14; the default python executable was 3.9.25 and was not used for the fixed review commands. Passing these commands on 3.12 does not qualify the Python 3.14 application release. The public runtime and candidate CI use Python 3.14 and retain their own evidence.

The minimal currency-cache order is [set_eur, default_checkout]; neither test fails alone. The candidate passes that order and ten full seeded orders (7101–7110), retaining test and assertion coverage. The skip_victim and missing_cleanup controls are rejected. The cleanup policy is authored and selected/reviewed through Duo, not general model-generated repair. This is an original planted fixture, not a held-out real-world flake dataset; deletion-minimality and finite seeds do not prove absence of flakes.

A green candidate pipeline does not conceal the failure: capture_original_failure deliberately executes the unchanged baseline and preserves the expected red job. Only expected exit 1 is allowed; unresolved capture errors block. The separate verify_reviewed_repair job is blocking and succeeded. Its authenticated JUnit report has 14 passing checks; the separate baseline capture has four passing tests and one expected failure. The combined pipeline report therefore still contains that intentional failure. An allowed capture failure by itself would not prove a repair.

GitLab retains actual JSON/JUnit artifacts and job states. Local JSON metadata alone is not provider authentication. The draft candidate remains unmerged and the public workbench is independently deployed; no candidate preview deployment is claimed. Both repositories stay private, so provider links need authorized access. Source publication remains the owner's decision.

See [fixed review commands](REVIEW_WORKFLOW.md), [Duo configuration](DUO_FLOW.md) and [public release evidence](LIVE_RELEASE.md).
