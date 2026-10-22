# Private Duo failure-review flow

`.gitlab/duo/flow.yml` is prepared configuration, not an installed or verified integration. Register it only in private project **87890207** (`.../43478475/flaketrail`) after the existing credential, permission and sponsored-usage gates clear. Select **Private**, paste the YAML into a custom Flow, enable only a deliberate mention trigger, and start a fresh session. Do not enable broad pipeline/issue triggers. A committed YAML file does not register a catalog flow.

The single agent reads the actual project skill, diagnoses the original currency-cache fixture and inspects a source-bound captured failure. An explicit candidate request permits only the authored reset-policy change. The operator reviews the actual session output before creating a branch/MR and running the separate manual CI jobs. No automatic merge, publication, deployment, comment, pipeline or MR is configured.

## Runtime and fixed commands

The application release remains Python3.14. The default Duo image retains Sandbox Runtime and currently includes Python3.12; no replacement image or runtime installer is added. Prefer its explicit `python3.12` executable and record the version; otherwise inspect `python3 --version`. The first authorized flow may attempt the fixed diagnosis/review commands on that interpreter as a targeted compatibility check. Missing features, exceptions or failed verification leave the result unresolved. Compatibility is currently unverified; passing these narrow CLI commands would not qualify a different application release runtime. Never change assertions or timeout limits to force a pass.

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

Record actual Duo session URL/ID, source commit, interpreter/command exits, original failing pipeline/job/artifact, captured order/fingerprint, diagnosis, policy diff and repaired pipeline artifacts. Report local command outcomes separately from provider verification. The repair is an authored policy selected and reviewed by Duo, not general generated repair. `max_cycles: 18` is a soft reasoning limit, not a spending cap. Provider schema acceptance, runner availability and execution remain unverified.

Configuration follows the official [custom-flow schema](https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/) and [v1 specification](https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/raw/main/docs/flow_registry/v1.md). GitLab reads [agent configuration](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/agent-config-yaml/) from the default branch. The [default image inventory](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/images/) is documented, not verified for this project.
