# MiniCzechBenchmark
Selected 4 x 200 multiple-choice questions to test large language models.

## Datasets (200 randomly selected questions each)
 * [MiniAGREE](https://huggingface.co/datasets/simecek/mini_agree) (Czech language)
 * [MiniCzechNews](https://huggingface.co/datasets/simecek/mini_czech_news) (news categorization)
 * [MiniKlokánek](https://huggingface.co/datasets/simecek/mini_klokanek) (math)
 * [MiniCTKFacts](https://huggingface.co/datasets/simecek/mini_ctkfacts) (reasoning)
 * Sumarizace (text summarization) - t.b.d.

To evaluate a model on MiniCzechBenchmark, use [minicz_bench.ipynb](minicz_bench.ipynb), either interactively or via [Papermill](https://github.com/nteract/papermill)

```
papermill minicz_bench.ipynb output.ipynb -p MODEL "CohereForAI/aya-expanse-8b" -p DATA_SIZE "mini"
```

The full datasets and few-shot prompts come from the [CzechBench](https://gitlab.com/jirkoada/czech-bench) benchmark. Special thanks to Adam Jirkovsky and the authors of the original datasets for this resource.

## Results (Mar 30, 2025)

| model                                            |   average_accuracy |   agree_accuracy |   czech_news_accuracy |   klokanek_accuracy |   ctkfacts_accuracy |   average_validity |
|:-------------------------------------------------|-------------------:|-----------------:|----------------------:|--------------------:|--------------------:|-------------------:|
| gemini-2.5-pro-exp-03-25                         |               0.84 |             0.89 |                  0.84 |                0.90 |                0.74 |               1    |
| o3-mini                                          |               0.79 |             0.78 |                  0.82 |                0.92 |                0.66 |               1    |
| o1-mini                                          |               0.79 |             0.74 |                  0.84 |                0.84 |                0.76 |               1    |
| deepseek-ai/DeepSeek-R1                          |               0.76 |             0.74 |                  0.82 |                0.78 |                0.72 |               0.97 |
| Qwen/QwQ-32B                                     |               0.75 |             0.76 |                  0.8  |                0.71 |                0.74 |               0.94 |
| gemini-2.0-pro-exp-02-05                         |               0.75 |             0.79 |                  0.84 |                0.64 |                0.72 |               1    |
| gemini-1.5-pro-latest                            |               0.72 |             0.78 |                  0.85 |                0.53 |                0.72 |               1    |
| gemini-2.0-flash-exp                             |               0.72 |             0.72 |                  0.85 |                0.56 |                0.76 |               1    |
| claude-3-5-sonnet-20241022                       |               0.72 |             0.86 |                  0.84 |                0.48 |                0.7  |               1    |
| gemini-2.0-flash                                 |               0.72 |             0.72 |                  0.85 |                0.55 |                0.76 |               1    |
| claude-3-5-sonnet-20240620                       |               0.71 |             0.88 |                  0.81 |                0.44 |                0.72 |               1    |
| claude-3-7-sonnet-20250219                       |               0.71 |             0.88 |                  0.8  |                0.46 |                0.7  |               1    |
| deepseek-chat                                    |               0.69 |             0.74 |                  0.8  |                0.54 |                0.7  |               1    |
| deepseek-ai/DeepSeek-V3                          |               0.68 |             0.71 |                  0.82 |                0.52 |                0.7  |               0.99 |
| gemini-2.0-flash-lite                            |               0.66 |             0.7  |                  0.84 |                0.44 |                0.68 |               1    |
| gpt-4o                                           |               0.65 |             0.76 |                  0.84 |                0.33 |                0.69 |               1    |
| gpt-4o-2024-05-13                                |               0.65 |             0.76 |                  0.82 |                0.34 |                0.68 |               1    |
| meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo    |               0.64 |             0.72 |                  0.81 |                0.36 |                0.68 |               0.99 |
| Qwen/Qwen2.5-72B-Instruct-GPTQ-Int4              |               0.64 |             0.6  |                  0.84 |                0.44 |                0.68 |               1    |
| unsloth/Qwen2.5-72B-Instruct-bnb-4bit            |               0.64 |             0.58 |                  0.86 |                0.45 |                0.67 |               1    |
| unsloth/Mistral-Large-Instruct-2407-bnb-4bit     |               0.64 |             0.62 |                  0.83 |                0.36 |                0.72 |               1    |
| gpt-4-turbo                                      |               0.64 |             0.68 |                  0.83 |                0.34 |                0.68 |               1    |
| mistralai/Mistral-Small-24B-Instruct-2501        |               0.63 |             0.66 |                  0.84 |                0.3  |                0.72 |               1    |
| claude-3-5-haiku-20241022                        |               0.63 |             0.64 |                  0.84 |                0.31 |                0.73 |               1    |
| mistral-small-latest                             |               0.63 |             0.63 |                  0.82 |                0.37 |                0.68 |               1    |
| gemini-1.5-flash-latest                          |               0.62 |             0.62 |                  0.82 |                0.34 |                0.69 |               0.99 |
| Qwen/Qwen2.5-32B-Instruct                        |               0.61 |             0.64 |                  0.78 |                0.4  |                0.64 |               1    |
| Qwen/Qwen2.5-72B-Instruct-Turbo                  |               0.61 |             0.55 |                  0.8  |                0.4  |                0.69 |               1    |
| mistral-large-latest                             |               0.61 |             0.61 |                  0.84 |                0.31 |                0.68 |               1    |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B         |               0.61 |             0.64 |                  0.72 |                0.33 |                0.74 |               0.81 |
| Qwen/Qwen2.5-14B-Instruct-1M                     |               0.6  |             0.56 |                  0.78 |                0.33 |                0.73 |               1    |
| unsloth/Llama-3.3-70B-Instruct-bnb-4bit          |               0.6  |             0.55 |                  0.78 |                0.36 |                0.72 |               1    |
| meta-llama/Llama-3.3-70B-Instruct-Turbo          |               0.6  |             0.58 |                  0.82 |                0.34 |                0.65 |               1    |
| fsaudm/Meta-Llama-3.1-70B-Instruct-NF4           |               0.6  |             0.55 |                  0.8  |                0.33 |                0.71 |               1    |
| unsloth/Meta-Llama-3.1-70B-Instruct-bnb-4bit     |               0.6  |             0.55 |                  0.8  |                0.34 |                0.71 |               0.99 |
| Qwen/Qwen2.5-14B-Instruct                        |               0.6  |             0.6  |                  0.79 |                0.32 |                0.68 |               1    |
| unsloth/gemma-3-12b-it                           |               0.6  |             0.52 |                  0.83 |                0.33 |                0.71 |               1    |
| google/gemma-2-27b-it                            |               0.59 |             0.57 |                  0.8  |                0.3  |                0.7  |               1    |
| gpt-4o-mini                                      |               0.59 |             0.64 |                  0.82 |                0.31 |                0.6  |               1    |
| unsloth/gemma-3-27b-it                           |               0.58 |             0.47 |                  0.84 |                0.4  |                0.62 |               1    |
| claude-3-haiku-20240307                          |               0.58 |             0.57 |                  0.8  |                0.28 |                0.65 |               1    |
| gemini-1.5-flash-8b-latest                       |               0.58 |             0.56 |                  0.77 |                0.24 |                0.74 |               1    |
| speakleash/Bielik-11B-v2.3-Instruct              |               0.57 |             0.55 |                  0.8  |                0.26 |                0.69 |               1    |
| AMead10/c4ai-command-r-08-2024-awq               |               0.57 |             0.48 |                  0.83 |                0.3  |                0.7  |               1    |
| unsloth/c4ai-command-r-08-2024-bnb-4bit          |               0.57 |             0.48 |                  0.82 |                0.28 |                0.72 |               1    |
| microsoft/phi-4                                  |               0.57 |             0.48 |                  0.81 |                0.3  |                0.7  |               1    |
| mistralai/Mistral-Small-Instruct-2409            |               0.57 |             0.4  |                  0.82 |                0.3  |                0.74 |               1    |
| CohereForAI/aya-expanse-32b                      |               0.56 |             0.5  |                  0.78 |                0.3  |                0.67 |               1    |
| google/gemma-2-9b-it                             |               0.54 |             0.5  |                  0.78 |                0.26 |                0.62 |               1    |
| gpt-3.5-turbo                                    |               0.53 |             0.48 |                  0.76 |                0.28 |                0.59 |               1    |
| Qwen/Qwen2.5-7B-Instruct                         |               0.52 |             0.37 |                  0.72 |                0.3  |                0.7  |               1    |
| CohereForAI/aya-23-35B                           |               0.52 |             0.5  |                  0.76 |                0.22 |                0.6  |               1    |
| NousResearch/Hermes-3-Llama-3.1-8B               |               0.52 |             0.43 |                  0.7  |                0.26 |                0.68 |               1    |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B         |               0.52 |             0.58 |                  0.26 |                0.54 |                0.7  |               0.73 |
| mistralai/Ministral-8B-Instruct-2410             |               0.52 |             0.4  |                  0.68 |                0.29 |                0.69 |               1    |
| CohereForAI/aya-expanse-8b                       |               0.51 |             0.48 |                  0.75 |                0.22 |                0.58 |               1    |
| mistralai/Mixtral-8x7B-Instruct-v0.1             |               0.5  |             0.3  |                  0.76 |                0.26 |                0.72 |               0.98 |
| Qwen/Qwen2.5-7B-Instruct-1M                      |               0.5  |             0.35 |                  0.75 |                0.28 |                0.64 |               1    |
| mistralai/Mistral-Nemo-Instruct-2407             |               0.49 |             0.3  |                  0.72 |                0.26 |                0.68 |               1    |
| meta-llama/Llama-3.1-8B-Instruct                 |               0.49 |             0.44 |                  0.75 |                0.18 |                0.59 |               1    |
| google/gemma-2-2b-it                             |               0.48 |             0.41 |                  0.64 |                0.3  |                0.57 |               1    |
| mistralai/Mistral-7B-Instruct-v0.3               |               0.48 |             0.28 |                  0.67 |                0.28 |                0.68 |               1    |
| unsloth/gemma-3-4b-it                            |               0.48 |             0.38 |                  0.7  |                0.26 |                0.56 |               1    |
| meta-llama/Meta-Llama-3-8B-Instruct              |               0.47 |             0.3  |                  0.72 |                0.28 |                0.58 |               1    |
| CohereForAI/aya-23-8B                            |               0.47 |             0.24 |                  0.72 |                0.28 |                0.63 |               1    |
| utter-project/EuroLLM-9B-Instruct                |               0.45 |             0.32 |                  0.55 |                0.28 |                0.64 |               1    |
| tiiuae/Falcon3-10B-Instruct                      |               0.43 |             0.26 |                  0.75 |                0.22 |                0.51 |               1    |
| Qwen/Qwen2.5-3B-Instruct                         |               0.41 |             0.38 |                  0.4  |                0.26 |                0.58 |               1    |
| meta-llama/Llama-3.2-3B-Instruct                 |               0.41 |             0.32 |                  0.5  |                0.29 |                0.52 |               1    |
| microsoft/Phi-3.5-mini-instruct                  |               0.39 |             0.19 |                  0.56 |                0.24 |                0.56 |               1    |
| ibm-granite/granite-3.0-8b-instruct              |               0.34 |             0.24 |                  0.52 |                0.25 |                0.32 |               0.99 |
| Qwen/Qwen2.5-1.5B-Instruct                       |               0.33 |             0.36 |                  0.26 |                0.28 |                0.42 |               1    |
| microsoft/Phi-3-mini-128k-instruct               |               0.31 |             0.12 |                  0.62 |                0    |                0.5  |               0.65 |
| microsoft/Phi-3-mini-4k-instruct                 |               0.31 |             0.08 |                  0.52 |                0.17 |                0.46 |               0.83 |
| unsloth/gemma-3-1b-it                            |               0.31 |             0.27 |                  0.28 |                0.22 |                0.46 |               1    |
| mistralai/Mistral-7B-Instruct-v0.1               |               0.3  |             0.2  |                  0.44 |                0.02 |                0.54 |               0.77 |
| ibm-granite/granite-3.0-2b-instruct              |               0.21 |             0.21 |                  0.2  |                0.08 |                0.36 |               0.84 |
| tiiuae/Falcon3-Mamba-7B-Instruct                 |               0.19 |             0.17 |                  0.14 |                0.27 |                0.2  |               0.89 |


You can also download results as [CSV table](minicz_bench.csv).

## Comparison to Full Datasets 

Comparison of average accuracies (over 4 datasets) of 24 open models (mix of Lammas, Mistrals, Gemmas, Qwens...) on MiniCzechBenchmark and on full datasets.

The Spearman rank-order correlation coefficient between average accuracies is $>0.996$. The maximum absolute difference between average accuracies is $0.0291$.

![](./assets/average_accuracy_comparison.png)

## Comparison to CzechBench and BenCzechMark (Oct 31, 2024)

Datasets included in *MiniCzechBenchmark* were selected to be representative of [CzechBench](https://huggingface.co/spaces/CIIRC-NLP/czechbench_leaderboard), so it is not surprising that the shared models achieve similar performance on both benchmarks, with a Spearman rank-order correlation coefficient of $0.99$.

If we compare *MiniCzechBenchmark* results to the [recently](https://huggingface.co/blog/benczechmark) introduced [BenCzechMark](https://huggingface.co/spaces/CZLC/BenCzechMark), the Spearman rank-order correlation coefficient is approx. $0.65$.

![](./assets/MiniCzechBenchmark_comparison.png)

## Benchmark Runs Outputs

At the end of [evaluation script](./minicz_bench.ipynb), we save the results in the following format:
- `model`: model name
- `datasets`: dataset names
- `raw outputs`: raw outputs of the model
- `dfs`: dataframes with the processed results
- `metrics`: accuracies of the model on each dataset, also percentages of valid answers
- `timing_results`: timing results of the model on each dataset (in seconds)

The results are saved in the [bench_runs](./bench_runs) directory.

