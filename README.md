# MiniCzechBenchmark

MiniCzechBenchmark is a small Czech benchmark built around 4 x 200 multiple-choice questions.

## Datasets (200 randomly selected questions each)

- [MiniAGREE](https://huggingface.co/datasets/simecek/mini_agree) (Czech language)
- [MiniCzechNews](https://huggingface.co/datasets/simecek/mini_czech_news) (news categorization)
- [MiniKlokánek](https://huggingface.co/datasets/simecek/mini_klokanek) (math)
- [MiniCTKFacts](https://huggingface.co/datasets/simecek/mini_ctkfacts) (reasoning)

## Update (Apr 2026)

This minibenchmark was originally presented at the Seznam LLM Meetup in October 2024. See the meetup recap [here](https://blog.seznam.cz/2024/10/ai-je-stale-horke-tema-ukazal-seznam-meetup-venovany-jazykovym-modelum/).

In practice, the dataset proved most useful as a quick and cheap screen for new models: a lightweight test to decide whether a model was interesting enough to justify proper evaluation on internal datasets. 

The benchmark was created before the rise of thinking models, and the math subset that used to be relatively difficult is now close to saturated. More recently, the project has also become a compact toy setup for me for learning and testing tooling such as Pydantic and Temporal.

Some findings may still be useful, especially as a cheap first-pass check for Czech-language capability and model behavior.

## Installation

With `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Environment variables are loaded automatically from `.env` via `pydantic-settings`. The main ones are `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, optional `OPENROUTER_API_KEY`, optional `NVIDIA_API_KEY`, and optionally `TEMPORAL_ADDRESS`.

To evaluate a model on MiniCzechBenchmark, first start a local Temporal server, then start the worker, and finally submit the benchmark run.

```bash
temporal server start-dev
python -m minicz_bench worker --max-parallel 20
python -m minicz_bench run --model "gpt-4.1-nano" --data-size mini --max-parallel 20 --max-attempts 5
```

Routing rules are simple: bare `gpt-*` / `o*` models use `OPENAI_API_KEY` when available, bare `claude-*` models use `ANTHROPIC_API_KEY` when available, and OpenRouter is used as a fallback when `OPENROUTER_API_KEY` is set. If you want to force OpenRouter, pass an explicit model such as `openrouter/openai/gpt-4.1-nano`.

NVIDIA is also supported as an explicit option. NVIDIA advertises free serverless APIs for development via NVIDIA NIM, so if you have a `NVIDIA_API_KEY`, you can run models using the `nvidia_nim/...` prefix, for example:

```bash
python -m minicz_bench run --model "nvidia_nim/meta/llama-3.1-8b-instruct" --data-size mini
```

Temporal is used here as a teaching-friendly orchestration layer: each benchmark item is executed as its own activity, so retries, concurrency limits, and run durability are visible in the workflow rather than hidden in ad-hoc async code.

The full datasets and few-shot prompts come from the [CzechBench](https://gitlab.com/jirkoada/czech-bench) benchmark. Special thanks to Adam Jirkovsky and the authors of the original datasets for this resource.

## Results

The historical leaderboard is now kept in [RESULTS.md](RESULTS.md), which preserves the old scores and adds room for richer metadata such as release date, parameter count, memory requirements, run cost, and duration.

For open models that can fit into 1 GPU (A100 or H100, 80GB) the historical calculation was performed at a local server with HF `transformers`; we used OpenAI, Anthropic, Google, TogetherAI or Fireworks API for the rest.

## Comparison to Full Datasets

Comparison of average accuracies (over 4 datasets) of 24 open models (mix of Lammas, Mistrals, Gemmas, Qwens...) on MiniCzechBenchmark and on full datasets.

The Spearman rank-order correlation coefficient between average accuracies is $>0.996$. The maximum absolute difference between average accuracies is $0.0291$.

Figure: [average_accuracy_comparison.png](assets/average_accuracy_comparison.png)

## Comparison to CzechBench and BenCzechMark (Oct 31, 2024)

Datasets included in *MiniCzechBenchmark* were selected to be representative of [CzechBench](https://huggingface.co/spaces/CIIRC-NLP/czechbench_leaderboard), so it is not surprising that the shared models achieve similar performance on both benchmarks, with a Spearman rank-order correlation coefficient of $0.99$.

If we compare *MiniCzechBenchmark* results to the [recently](https://huggingface.co/blog/benczechmark) introduced [BenCzechMark](https://huggingface.co/spaces/CZLC/BenCzechMark), the Spearman rank-order correlation coefficient is approx. $0.65$.

Figure: [MiniCzechBenchmark_comparison.png](assets/MiniCzechBenchmark_comparison.png)

## Benchmark Runs Outputs

At the end of each benchmark run, we save the results in the following format:

- `model`: model name
- `datasets`: dataset names
- `raw outputs`: raw outputs of the model
- `dfs`: dataframes with the processed results
- `metrics`: accuracies of the model on each dataset, also percentages of valid answers
- `timing_results`: timing results of the model on each dataset (in seconds)
- `cost_usd`: per-dataset and total API cost for new runs
- `token_usage`: prompt/completion/total tokens for new runs

The results are saved in the [bench_runs](./bench_runs) directory.

New runs also emit a JSON sidecar next to the legacy `pkl.gz` artifact so cost, token usage, and wall-clock timing can be reused when updating [RESULTS.md](RESULTS.md).