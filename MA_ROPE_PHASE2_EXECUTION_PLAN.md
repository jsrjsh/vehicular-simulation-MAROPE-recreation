# MA-ROPE Phase 2 Execution Plan

## Objective
Reconstruct the MA-ROPE simulator from the recreation guide while preserving paper fidelity.

## Goals
1. Reproduce published MA-ROPE results.
2. Validate figures/tables.
3. Freeze baseline as MA-ROPE v1.0.
4. Build MA-ROPE+ only after baseline is frozen.

## Inputs
- MA_ROPE_RECREATION_GUIDE.md
- IEEE manuscript
- Existing SUMO/ns-3 pipeline

## Rules
- Reproduce before improving.
- Never guess missing equations.
- Preserve baseline behaviour.

## Deliverables
- IMPLEMENTATION_TRACE.md
- BUILD_STATUS.md
- TEST_REPORT.md
- REPRODUCIBILITY_REPORT.md

## Baseline Freeze
Create git tag: MA-ROPE-v1.0

## Afterwards
Implement:
- Differential Privacy
- ε sweep
- Communication overhead
- Improved SUMO realism
- RSU handover
