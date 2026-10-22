# FlakeTrail

Minimize order-dependent test failures and verify repairs.

## Status

The local Python diagnosis engine, HTTP API and browser replay dashboard work. Twenty-one automated tests and the prior eight actual browser checks passed. Three original planted faults reduce to two- or three-test interactions; reset repairs preserve assertions, while skipping the victim is rejected. A separate [review workflow](docs/REVIEW_WORKFLOW.md) now captures a real failing order, proposes an actual cleanup-configuration diff, and verifies that candidate with JSON/JUnit evidence. Actual GitLab Duo/MR/CI and public deployment remain pending. These examples are local development fixtures, not captured provider failures or held-out results.

## Intended use

A maintainer sees a test that passes alone but fails after another test. FlakeTrail converts a captured failing order into a smaller reproducible interaction, proposes an isolation fix and verifies that it fixes the cause instead of hiding the failure with retries.

## Planned workflow

A new owned Python fixture service fails CI → GitLab Duo collects seed/order/logs → bounded delta debugging reduces the sequence → the model proposes one scoped fixture/reset fix → a merge request runs the reproducer and independent randomized orders → deploy preview only after the gate → report evidence. Deterministic executions decide pass/fail; model confidence cannot override them.

## Development

Use Python 3.14 (tested locally with 3.14.1); runtime dependencies are standard-library only:

```sh
python -m flaketrail.web
```

Open http://127.0.0.1:8786. Choose an example, trace the failure, inspect the minimized order and review both the reset repair and rejected skip-test control. Set the run limit to 1 to see an honest partial/unresolved result. Reports export as JSON and can be optionally saved, restored or deleted in the browser. The server stores no result database.

```sh
python -m flaketrail --list
python -m flaketrail currency-cache --budget 40
python -m unittest discover -s tests -v
python -m flaketrail.evidence
npm ci
npx playwright install chromium
npm run test:browser
```

Every probe launches a fresh Python subprocess and executes only known test IDs. The minimizer preserves the nominated failure fingerprint, verifies the victim passes alone and checks each single deletion. This establishes deletion-minimality, not a globally shortest sequence. The minimization limit is 1–40 attempts/35 seconds; repair verification has a separate maximum of 12 runs/35 seconds. Worker execution has a three-second timeout, one active diagnosis is admitted per web process, and HTTP input is capped at 8KiB. No uploaded code, shell commands or arbitrary URL fetch is supported.

The authored reset fix reinitializes shared state and restores the one fixture environment variable after each test; it is not model-generated repair. Ten independently seeded orders plus the minimized case must retain the same assertions. A skip-victim control is rejected for lost coverage even when the remaining assertions pass. [Evidence limits](docs/LOCAL_MILESTONE.md), [provider continuation](docs/GITLAB_INTEGRATION.md).

`docker build -t flaketrail:local-check .` builds a non-root Python image. `node scripts/verify-container.mjs` checks it locally. Set HOST=0.0.0.0 in a container and FLAKETRAIL_PUBLIC_ORIGIN to the exact deployed HTTPS origin. Cloud deployment has not occurred and needs its own spending approval.

Keep credentials in local ignored files or the deployment secret store. Do not commit user data, provider tokens or private evaluation records.

## License

Original code, fixture tests and documents use the [MIT license](LICENSE). Python and its standard library retain PSF/component licenses; Playwright Test1.64.1 is Apache-2.0 and used only for development checks. The UI uses system fonts and no external assets. Source stays private until explicit owner publication authorization; MIT licensing alone is not permission to publish.
