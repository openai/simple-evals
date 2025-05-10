# Length-Variance (len_var) Scorer

| Key | Value |
|-----|-------|
| **Purpose** | Detects internal length fluctuation in a single answer |
| **Formula** | σ(window_lengths) / μ(window_lengths) |
| **Threshold (tentative)** | <0.20 : ✅ / 0.20-0.39 : ⚠️ / ≥0.40 : 🔥 |
| **Dependencies** | None (pure Python stdlib) |
