# Job State Machine

Trang thai hop le: created, queued, waiting_dependency, running, pause_requested, paused, resume_requested, cancel_requested, cancelling, retry_wait, completed, failed, cancelled, interrupted va blocked.

Transition bat hop le bi chan boi JobStateMachine.

Running job sau crash/startup recovery thanh interrupted.
