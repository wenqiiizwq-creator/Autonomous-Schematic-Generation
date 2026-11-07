# ASG evaluations

Circuit cases live in the evaluation set shared with schematic-review (`原理图设计规范/评测集/`, located by `evals/eval_set.py`, override with `CIRCUIT_EVAL_SET`). `python3 evals/circuit_cases/run.py prepare --case <id> --out <new dir> --guideline-release <selected release>` gives ASG one circuit's requirements only; results go to `评测记录/ASG/` next to that set (located by `eval_set.records()`, override with `CIRCUIT_EVAL_RECORDS`). The benchmarks below are separate and stay here.

Synthetic regression fixtures stay in `tests/`; `value_patch/` holds the validation record used by `scripts/patch_schematic_values.py`.
