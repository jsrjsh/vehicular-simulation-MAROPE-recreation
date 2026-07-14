# POLICY_CHECKPOINT_AUDIT.md

This document audits the policy network training configurations and model checkpoint status for the MA-ROPE platform reproduction effort.

---

## 1. Baseline Statement

> **“algorithmic reconstruction test, not numerical checkpoint reproduction.”**

No pre-trained model weights or historical checkpoint binaries (`.pt` or `.pth` files) were provided in the initial repository workspace. The policy model is entirely trained from scratch during the execution. Therefore, this is an algorithmic reconstruction test rather than a numerical checkpoint validation.

---

## 2. Checkpoint Details (Smoke Run)

* **Trained checkpoint used:** No (trained from scratch)
* **Number of training episodes:** 30 episodes
* **Number of environment steps per episode:** 100 steps
* **Total training steps:** 3,000 steps
* **Training seed:** 42
* **Evaluation seeds:** 101, 102, 103, 104, 105 (seed + 100 + ep)
* **Final training epsilon ($\epsilon$):** Bounded at 0.05
* **FedAvg communication rounds:** 150 rounds (every 20 steps over 3,000 steps)
* **Replay mode:** Prioritized Experience Replay (PER)
* **Checkpoint Evaluation Repeatability:** Evaluates 100% deterministically when seeds are locked.
* **Checkpoint Hash (evaluation model):** No static paper hash exists. Newly saved weights differ depending on seed initialization.
