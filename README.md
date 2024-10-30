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

## Results

t.b.d.

## Comparison to Full Datasets 

Comparison of average accuracies (over 4 datasets) of 24 open models (mix of Lammas, Mistrals, Gemmas, Qwens...) on MiniCzechBenchmark and on full datasets.

The Spearman rank-order correlation coefficient between average accuracies is $>0.996$. The maximum absolute difference between average accuracies is $0.0291$.

![](./assets/average_accuracy_comparison.png)

## Comparison to CzechBench

t.b.d.

## Notebooks with Benchmarks Runs

t.b.d.


