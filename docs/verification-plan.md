# FlakeTrail: verification plan

No tests or evaluations have run. The following are prospective acceptance targets, not results.

## Fixtures and acceptance

six development and six held-out planted order-dependent faults. Reproduce all six held-out failures; isolate at least five within a capped 40-run budget each; zero accepted fixes may remove coverage or retain a reproducible original fault. Run each proposed repair under ten unseen seeds and report that this is finite evidence, not proof of absence of flakes. Compare repeated reruns, seed replay alone and the complete loop on runs/time/minimal sequence length.

## Demonstration to verify

failing pipeline, one-click causal trace, reduced two-test interaction, proposed reset fix, independent seed checks and preview. Include the rejected test-disabling patch.

## Result record

For each run, record the source commit, fixture version, runtime/provider versions, actual pass and failure counts, latency, cost where relevant, and limitations. Keep development and held-out inputs separate. Report negative findings; freeze the protocol before inspecting held-out results.

A release requires a functioning end-to-end workflow and a clean-session replay. Documentation, repository creation and HTTP availability alone do not establish application correctness.
