# TASK SUMMARY

<!-- User intent, verified scope, desired outcome and explicit non-goals. -->

# EVIDENCE AND CURRENT STATE

<!-- Current repository state with source/test/config/decision evidence.
Use VERIFIED / INFERRED / UNVERIFIED / BLOCKED. Distinguish historical context from current source. -->

# DESIRED STATE

<!-- User-observable target. Do not assume a product or architecture decision that lacks approval. -->

# ACCEPTANCE CRITERIA

<!-- Observable, testable criteria. Link every criterion to a planned validation method. -->

# PRESERVED INVARIANTS

<!-- Public/default/error/state semantics, identity, persistence, lineage, safety and compatibility constraints that must remain true. -->

# DECISION GATE

<!-- Existing approved decisions with evidence, OR:
USER DECISION REQUIRED
Decision:
Why current evidence does not decide it:
Options / trade-offs:
Required approval:
Do not write implementation details dependent on an unapproved decision. -->

# AFFECTED MODULES AND BOUNDARIES

<!-- UI/Page/Controller/Service/Queue/Engine/Runtime, persistence, APIs, runtime/resource and security boundaries affected or verified unaffected. -->

# CALLERS AND DEPENDENCIES

<!-- Actual entry points, caller chain, extension points, models/configuration/serialization/runtime dependencies, and immutable ID/snapshot context. -->

# FILES TO MODIFY

<!-- Expected files, purpose and reason each file is necessary. -->

# FILES NOT TO MODIFY

<!-- Excluded files/modules/data paths and the safety/compatibility reason to preserve them. -->

# RISK ANALYSIS

<!-- Regression, compatibility, identity/persistence/lineage, data/artifact, resource/job, runtime/readiness, security and UI-responsiveness risks as applicable. -->

# VALIDATION PLAN

<!-- Per criterion/slice:
- check or command;
- claim it can prove;
- prerequisite/environment;
- limitation or fallback evidence.
Include targeted tests, compile/import, relevant smoke, git diff --check and git status --short. -->

# IMPLEMENTATION PLAN

<!-- Dependency-safe minimal slices. For each:
1. File/module and existing extension point.
2. Proposed change.
3. Caller/dependency impact.
4. Invariants/failure/cancel/retry/recovery behavior.
5. Data/resource/security/readiness constraints.
6. Validation evidence.
Do not include speculative refactor or unapproved product decisions. -->

# UNVERIFIED ITEMS / BLOCKERS

<!-- Missing evidence, environment limits, expected decisions or validations that cannot currently be performed. -->

# FINAL STATUS

<!-- Use exactly one:
READY FOR IMPLEMENTATION
BLOCKED
USER DECISION REQUIRED

READY FOR IMPLEMENTATION means the plan is evidence-backed and safe to implement; it does not claim production capability is READY. -->