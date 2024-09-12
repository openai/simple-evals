# Multilingual MMLU Benchmark Results

To evaluate multilingual performance, we translated MMLU’s test set into 14 languages using professional human translators. Relying on human translators for this evaluation increases confidence in the accuracy of the translations, especially for low-resource languages like Yoruba.

## Results

|         Language         | o1-preview | gpt-4o-2024-08-06 |  o1-mini   | gpt-4o-mini-2024-07-18 |
| :----------------------: | :--------: | :---------------: | :--------: | :--------------------: |
|          Arabic          | **0.8821** |      0.8155       | **0.7945** |         0.7089         |
|         Bengali          | **0.8622** |      0.8007       | **0.7725** |         0.6577         |
|   Chinese (Simplified)   | **0.8800** |      0.8335       | **0.8180** |         0.7305         |
| English (not translated) | **0.9080** |      0.8870       | **0.8520** |         0.8200         |
|          French          | **0.8861** |      0.8437       | **0.8212** |         0.7659         |
|          German          | **0.8573** |      0.8292       | **0.8122** |         0.7431         |
|          Hindi           | **0.8782** |      0.8061       | **0.7887** |         0.6916         |
|        Indonesian        | **0.8821** |      0.8344       | **0.8174** |         0.7452         |
|         Italian          | **0.8872** |      0.8435       | **0.8222** |         0.7640         |
|         Japanese         | **0.8788** |      0.8287       | **0.8129** |         0.7255         |
|          Korean          | **0.8815** |      0.8262       | **0.8020** |         0.7203         |
|   Portuguese (Brazil)    | **0.8859** |      0.8427       | **0.8243** |         0.7677         |
|         Spanish          | **0.8893** |      0.8493       | **0.8303** |         0.7737         |
|         Swahili          | **0.8479** |      0.7708       | **0.7015** |         0.6191         |
|          Yoruba          | **0.7373** |      0.6195       | **0.5807** |         0.4583         |

These results can be reproduced by running

```bash
python -m simple-evals.run_multilingual_mmlu
```
