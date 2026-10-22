# Reviewable cleanup change

The tracked `review-fixture/isolation.json` deliberately starts with `resetAfterEach: false`. The review commands execute the owned Python test catalog using this policy; changing it to `true` enables the existing state/environment reset after every test. Test bodies and assertions remain unchanged. This is a concrete configuration repair for these fixtures, not general automatic code repair or a verified Duo-generated change.

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

No pipeline, MR or Duo session has run yet. Local artifacts and environment variables do not authenticate GitLab execution. After authorized credentials and sponsor coverage are confirmed, preserve actual job/session/MR URLs and commit IDs separately. Python 3.14.1 is locally tested; a different Duo execution image remains unverified until its actual commands run.
