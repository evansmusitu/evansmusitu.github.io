# Walk-forward validation without hidden leakage

**Editorial status:** Draft for factual, financial-content, rights and publication review — **not approved for public release**.  
**Primary search intent:** walk forward validation time series models  
**Language:** English (original); localized versions not approved.  
**Article type:** Technical explainer; no proprietary or customer data.  

## Research question

Time-series data cannot be shuffled indiscriminately like many independent observations. A model trained on later market conditions can inadvertently influence an earlier validation result. Walk-forward evaluation provides a closer approximation to the sequence in which knowledge becomes available, but the split itself does not prevent leakage elsewhere in a pipeline.

## Method and reproducibility

Set a chronological training window, a following tuning interval where appropriate, and a later evaluation window. At each step fit preprocessing, feature selection and model parameters only on data available before the prediction timestamp. Refit as the evaluation window advances, and aggregate outcomes across windows rather than cherry-picking the best regime. Document whether the method uses expanding or rolling history, why those durations were chosen and what happens at gaps or market closures.

## Worked conceptual example

Suppose each monthly forecast uses the preceding 24 months to estimate parameters. An expanding evaluation might train on months 1–24 and score month 25, then train on 1–25 and score month 26. A rolling alternative would use months 2–25 for month 26. If a normalization step uses the full 30-month sample, future distribution information has entered the past. The walk-forward table would look valid but the result would not.

## Failure modes and how to challenge the result

Inspect timestamp alignment, label horizon overlap, corporate action adjustments, selection of features using the full dataset, and data releases with delayed public availability. Test both performance dispersion across windows and aggregate results. A model that works in one easy regime and fails elsewhere should not be described as robust.

## Reviewer checklist

Use time-aware splits; fit transforms inside each fold; model release lags; preserve each prediction timestamp; publish window-level errors; lock the final evaluation plan.

## Scope and limitations

Walk-forward validation estimates historical out-of-sample behaviour under specific assumptions; it cannot eliminate changing regimes or ensure future generalization.

## Background reference

[Federal Reserve, revised model-risk guidance SR 26-2 (2026)](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm). This reference is for contextual reading and does not independently validate the illustrative example above.

## Related MUSITU page

[Explore relevant MUSITU information](/solutions/finance-research/). Describing a research method does not assert that a specific MUSITU product has implemented or independently validated it.
