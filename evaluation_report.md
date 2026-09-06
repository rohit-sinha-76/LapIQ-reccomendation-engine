# LapIQ — Evaluation Benchmark Report

**Date**: 2026-08-03  
**Evaluation Suite**: 5 Target Persona Profiles  
**Dataset Size**: 479 Cleaned Indian Laptop Variants  

---

## Overall Accuracy Metrics

- **Total Personas Evaluated**: 5
- **Top-1 Recommendation Accuracy**: **100.0%** (5/5)
- **Top-3 Recommendation Accuracy**: **100.0%** (5/5)

---

## Detailed Persona Breakdown

| Persona ID | Persona Name | Target Segment | Budget (INR) | Top-1 Match | Top-3 Match | Top Pick Model | Score |
|---|---|---|---|---|---|---|---|
| `p-student-01` | Rohan - CS Student | Students | INR 60,000 | PASS | PASS | `ACER Aspire 14 Intel Core i7 13th G` | 0.81 |
| `p-gamer-01` | Ananya - Esports Gamer | Gamers | INR 135,000 | PASS | PASS | `ACER Predator Helios Neo 16 2025` | 0.88 |
| `p-creator-01` | Vikram - Video Editor | Creators | INR 165,000 | PASS | PASS | `ASUS ROG Strix G16 2025 G614JVR` | 0.90 |
| `p-pro-01` | Priya - Tech Executive | Professionals | INR 75,000 | PASS | PASS | `LENOVO IdeaPad Slim 5 2.5K IPS Intel ` | 0.82 |
| `p-budget-01` | Amit - School Student | Students | INR 35,000 | PASS | PASS | `ACER Aspire 3 Intel Core i3 13th Ge` | 0.73 |

---

## Verdict & Quality Notes

1. **Deterministic Reproducibility**: 100% reproducible ranking across all 5 evaluation profiles without LLM intervention.
2. **Zero Hallucination**: Every recommended laptop variant exists in the verified 479-laptop dataset and satisfies strict business rules filtering.
3. **Segment Weight Alignment**: Scoring Engine weights correctly prioritize battery for Students, performance for Gamers, and portability for Professionals.