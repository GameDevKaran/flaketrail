# FlakeTrail

Minimize order-dependent test failures and verify repairs.

## Status

This repository contains the initial product documentation. Application development has not started. There is no runnable application, measured benchmark or deployed service yet.

## Intended use

A maintainer sees a test that passes alone but fails after another test. FlakeTrail converts a captured failing order into a smaller reproducible interaction, proposes an isolation fix and verifies that it fixes the cause instead of hiding the failure with retries.

## Planned workflow

A new owned Python fixture service fails CI → GitLab Duo collects seed/order/logs → bounded delta debugging reduces the sequence → the model proposes one scoped fixture/reset fix → a merge request runs the reproducer and independent randomized orders → deploy preview only after the gate → report evidence. Deterministic executions decide pass/fail; model confidence cannot override them.

## Development

Start with the behavior and boundaries in [Architecture](docs/architecture.md), then establish the fixtures and acceptance checks in [Verification plan](docs/verification-plan.md). Runtime versions, dependency installation, commands and deployment instructions will be added alongside working code. No installation command is available at this stage.

Keep credentials in local ignored files or the deployment secret store. Do not commit user data, provider tokens or private evaluation records.

## License

Original application code and these documents use the [MIT license](LICENSE). Future dependencies, models, datasets and media retain their own licenses and must be reviewed before inclusion.
