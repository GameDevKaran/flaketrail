# Private Duo failure-review flow

The private custom flow was registered and executed in project **87890207** (`.../43478475/flaketrail`). Actual session [10031632](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43478475/flaketrail/-/automate/agent-sessions/10031632) completed on 26 October 2026; its provider job succeeded. [Full provider chain](GITLAB_INTEGRATION.md). `.gitlab/duo/flow.yml` records the configuration; a committed YAML file alone is not execution evidence. Keep deliberate mention triggers and do not enable broad pipeline/issue triggers.

The single agent reads the actual project skill, diagnoses the original currency-cache fixture and inspects a source-bound captured failure. An explicit candidate request permits only the authored reset-policy change. The operator reviews the actual session output before creating a branch/MR and running the separate manual CI jobs. No automatic merge, publication, deployment, comment, pipeline or MR is configured.

## Runtime and fixed commands

The application release remains Python3.14. The default Duo image retains Sandbox Runtime and currently includes Python3.12; no replacement image or runtime installer is added. Prefer its explicit `python3.12` executable and record the version; otherwise inspect `python3 --version`. The actual flow used Python 3.12.14 and completed capture, reduction, proposal/application and verification. The expected original capture exited 1; the candidate gate exited 0. This establishes compatibility for those narrow commands, not qualification of the Python 3.14 application release. Missing features, exceptions or failed verification leave future results unresolved. Never change assertions or timeout limits to force a pass.

Use these literal arguments with the recorded interpreter (replace only the executable `python`):

```sh
python -m flaketrail.review capture
python -m flaketrail currency-cache --budget 40
python -m flaketrail.review propose --capture artifacts/review/capture.json
python -m flaketrail.review propose --capture artifacts/review/capture.json --apply
python -m flaketrail.review verify --capture artifacts/review/capture.json
git diff -- review-fixture/isolation.json
```

Capture must genuinely reproduce the original failure, write `artifacts/review/capture.json` and return **exit1** with `failure_captured`. That expected exit is not permission to ignore another error. Proposal without `--apply` is inspection only. Apply changes only the known `resetAfterEach` policy. Verification must return `verified_finite` and exit0 with retained failure, assertion coverage, minimized/seeded outcomes and rejected invalid controls. Never alter assertions, the baseline or the gate to pass. Locally captured evidence is not a GitLab failure artifact.

## Provider evidence to retain

Record actual Duo session URL/ID, source commit, interpreter/command exits, original failing pipeline/job/artifact, captured order/fingerprint, diagnosis, policy diff and repaired pipeline artifacts. Report local command outcomes separately from provider verification. The repair is an authored policy selected and reviewed by Duo, not general generated repair. The prompt requests at most 18 tool calls with no failed-command retries; this is a soft instruction, not an enforced runtime or spending cap. The supported prompt timeout is 180 seconds per prompt, not a whole-flow limit. Provider schema acceptance and this actual session/job are now verified; the soft request limits remain distinct from enforced spending or runtime caps.

The current [catalog validation schema](https://gitlab.com/gitlab-org/gitlab/-/raw/master/app/validators/json_schemas/ai_catalog/flow_v2.json) rejects `max_cycles`, although the engine's v1 specification documents it. This flow omits that unsupported key. The engine documentation gives a default of 280 cycles; the catalog exposes no supported cycle-limit field. Inspect the live session and stop it if it exceeds the intended scope. Local schema validation does not establish provider acceptance or execution.

Configuration follows the official [custom-flow schema](https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/) and [v1 specification](https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/raw/main/docs/flow_registry/v1.md). GitLab reads [agent configuration](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/agent-config-yaml/) from the default branch. The [default image inventory](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/images/) is background documentation; the actual interpreter observed in this project is recorded above.
