## Run evals

```sh
python simple_evals.py run drop --model deepseek-r1-llama-8b
```

```sh
python simple_evals.py run drop --model deepseek-r1-llama-8b -n 10 --out ./tmp/subset-10
```


## Logfire dashboard

```sql
SELECT trace_id, message, json_get(attributes, 'response_data', 'usage', 'completion_tokens') AS completion_tokens, json_get(attributes, 'response_data', 'usage', 'total_tokens') AS total_tokens
FROM records
LIMIT 10    
```