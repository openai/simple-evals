# Multilingual MMLU Benchmark Results

To evaluate multilingual performance, we translated MMLU’s test set into 14 languages using professional human translators. Relying on human translators for this evaluation increases confidence in the accuracy of the translations, especially for low-resource languages like Yoruba.

## Results

|         Language         |     o1     | gpt-4o-2024-11-20 | o3-mini-high | o3-mini | o1-mini | gpt-4o-mini-2024-07-18 |
| :----------------------: | :--------: | :---------------: | :----------: | :-----: | :-----: | :--------------------: |
|          Arabic          | **0.8900** |      0.8311       |  **0.8193**  | 0.8070  | 0.7945  |         0.7089         |
|         Bengali          | **0.8734** |      0.8014       |  **0.8010**  | 0.7865  | 0.7725  |         0.6577         |
|   Chinese (Simplified)   | **0.8892** |      0.8418       |  **0.8363**  | 0.7945  | 0.8180  |         0.7305         |
| English (not translated) | **0.9230** |      0.8570       |  **0.8690**  | 0.8590  | 0.8520  |         0.8200         |
|          French          | **0.8932** |      0.8461       |  **0.8374**  | 0.8247  | 0.8212  |         0.7659         |
|          German          | **0.8904** |      0.8363       |  **0.8079**  | 0.8029  | 0.8122  |         0.7431         |
|          Hindi           | **0.8833** |      0.8191       |  **0.8114**  | 0.7996  | 0.7887  |         0.6916         |
|        Indonesian        | **0.8861** |      0.8397       |  **0.8284**  | 0.8220  | 0.8174  |         0.7452         |
|         Italian          | **0.8970** |      0.8448       |  **0.8383**  | 0.8292  | 0.8222  |         0.7640         |
|         Japanese         | **0.8887** |      0.8349       |  **0.8312**  | 0.8227  | 0.8129  |         0.7255         |
|          Korean          | **0.8824** |      0.8289       |  **0.8261**  | 0.8158  | 0.8020  |         0.7203         |
|   Portuguese (Brazil)    | **0.8952** |      0.8360       |  **0.8405**  | 0.8316  | 0.8243  |         0.7677         |
|         Spanish          | **0.8992** |      0.8430       |  **0.8404**  | 0.8289  | 0.8303  |         0.7737         |
|         Swahili          | **0.8540** |      0.7786       |  **0.7379**  | 0.7167  | 0.7015  |         0.6191         |
|          Yoruba          | **0.7538** |      0.6208       |  **0.6374**  | 0.6164  | 0.5807  |         0.4583         |

These results can be reproduced by running

```bash
python -m simple-evals.run_multilingual_mmlu
```
