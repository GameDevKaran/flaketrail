# Reviewable cleanup change

The tracked `review-fixture/isolation.json` deliberately starts with `resetAfterEach: false`. The review commands execute the owned Python test catalog using this policy; changing it to `true` enables the existing state/environment reset after every test. Test bodies and assertions remain unchanged. This is a concrete authored configuration repair for these fixtures. Actual Duo selected and verified it; it is not general model-generated code repair.

Use Python 3.14 from the repository root. No cloud credentials are needed:

```sh
python -m flaketrail.review capture
```

Expected exit **1** means the original failure was actually captured. Exit **2** means unresolved/error, not a valid failing reproduction. Inspect `artifacts/review/capture.json` and its JUnit XML. Capture always executes the original no-cleanup baseline even when the candidate configuration has changed, so the failure remains reproducible. The default scenario is `currency-cache`; `--scenario environment-leak` and `--scenario derived-cache` select the other owned cases.

On a review branch, inspect and apply only the proposed cleanup policy:

```sh
python -m flaketrail.review propose --capture artifacts/review/capture.json
python -m flaketrail.review propose --capture artifacts/review/capture.json --apply
git diff -- review-fixture/isolation.json
python -m flaketrail.review verify --capture artifacts/review/capture.json
```

`propose` without `--apply` writes a proposal artifact and changes no source. With `--apply`, only the fixed configuration file changes. Stale source fingerprints, a non-replaying target failure, unknown settings and an already-modified candidate refuse without overwriting the candidate. Keep the baseline capture immutable; do not rehash modified assertions to manufacture acceptance.

Verification replays the captured failure against the unchanged original fixture/harness source, establishes deletion-minimality, then runs the candidate on the minimal order plus ten independently seeded full orders. Every test and assertion must remain. Both skipping the victim and disabling cleanup are executed as negative controls and must be rejected. Exit **0** requires all gates; an unchanged `false` policy fails. JSON and JUnit results are saved separately. Add `--output artifacts/review-candidate` to preserve a separate rehearsal directory.

For an MR, commit only the reviewed `review-fixture/isolation.json` diff; attach the real capture/proposal/verification artifacts separately. Leave the default branch's original configuration unchanged until a human approves the MR. Never auto-merge or publish source.

The prepared GitLab pipeline accepts only manually started web pipelines. `capture_original_failure` records the real failure, allowing only its expected exit 1. `verify_reviewed_repair` is a blocking manual job using that capture; it must pass on the candidate commit. An allowed baseline failure alone is not repair success. JUnit describes results but does not control a job's exit status. [GitLab exit-code configuration](https://docs.gitlab.com/ci/yaml/#allow_failureexit_codes), [JUnit reporting](https://docs.gitlab.com/ci/testing/unit_test_reports/).

The actual [Duo session, draft MR and candidate pipeline](GITLAB_INTEGRATION.md) are now verified. Pipeline 2988163158 succeeded on candidate `883229409d95e75a4217647b43ff62cb1b8d92e8`: its baseline capture intentionally failed as expected and its blocking repair job passed. The default branch retains the original policy. Local artifacts and environment variables alone still do not authenticate provider execution. Python 3.14.1 was locally tested; the actual Duo commands passed on Python 3.12.14, while application release and candidate CI use Python 3.14.
