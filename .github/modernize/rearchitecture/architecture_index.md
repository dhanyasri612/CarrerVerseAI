# Architecture index

## Implementation Guide

This index is not the full contract. Do not implement from this file alone; follow the artifact paths below.

### Global artifacts

- `unit_graph.yaml`: filter by assigned unit for entrypoints, dependencies, and shared refs.
- `migration_boundary.yaml`: use `must_rewrite` for the redesign scope; source anchors are not rewrite targets.
- `wire_contracts.yaml`: filter by `unit` and preserve frozen request, response, auth, and error behavior.
- `shared_modules.yaml`: filter by `used_by_units`; keep `used_fields` within the declared field set.
- `cross_unit_state.yaml`: filter flows where the assigned unit is writer or reader.
- `seams.yaml`: filter cuts touching the assigned unit; frozen-side rules are authoritative.

### Units

Each unit must read its `behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml` before implementation. Completion evidence must report those paths, every `must_preserve` item implemented, unresolved contracts, and build/test/runtime verification.

- `opening`: `units/opening/{behavior,bindings,unit_decomposition}.yaml`; trigger `GET /`.
- `profile`: `units/profile/{behavior,bindings,unit_decomposition}.yaml`; trigger `GET /profile`.
- `career-discovery`: `units/career-discovery/{behavior,bindings,unit_decomposition}.yaml`; trigger `GET /career-discovery`.
- `skill-gap`: `units/skill-gap/{behavior,bindings,unit_decomposition}.yaml`; trigger `GET /skill-gap`.
- `learning-roadmap`: `units/learning-roadmap/{behavior,bindings,unit_decomposition}.yaml`; trigger `GET /career-roadmap`.
- `interview`: `units/interview/{behavior,bindings,unit_decomposition}.yaml`; trigger `GET /ai/interview`.
- `career-intelligence`: `units/career-intelligence/{behavior,bindings,unit_decomposition}.yaml`; trigger `GET /ai/intelligence`.
