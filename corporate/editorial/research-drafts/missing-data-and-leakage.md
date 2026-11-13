# Missing values and data leakage in quantitative machine learning

**Editorial status:** Draft for factual, financial-content, rights and publication review — **not approved for public release**.  
**Primary search intent:** data leakage missing data quantitative machine learning  
**Language:** English (original); localized versions not approved.  
**Article type:** Technical explainer; no proprietary or customer data.  

## Research question

Missing values are seldom random in real research. A stale observation, unavailable field or suspended market can be related to the outcome a model is attempting to predict. A cleaning method that treats all missing values identically may remove precisely the difficult cases that matter most. Leakage occurs when information unavailable at decision time helps form the apparent prediction.

## Method and reproducibility

Define each feature's economic publication timestamp separately from its row date. Split evaluation periods chronologically, then fit imputation, scaling and feature selection inside training data only. Preserve missingness indicators when analytically justified. Compare complete-case, forward-fill and explicitly modelled-missingness results, checking which observations are omitted by each approach. Create assertion tests that reject features published after their target prediction time.

## Worked conceptual example

A company's annual earnings number might be stored under its fiscal year-end but released months later. A forecast made shortly after year-end cannot legally or logically use the subsequently disclosed value. A daily backtest that merges on fiscal-year date could quietly insert future information. Correct alignment uses an as-of join that respects the public release time and a stated publication lag.

## Failure modes and how to challenge the result

Forward filling may manufacture a tradeable price during a halt. Dropping all rows with missing signals can selectively erase failure periods. Global normalization based on the entire dataset can leak future distribution changes even when labels are correctly separated. The audit should include the complete pipeline, not only model.fit().

## Reviewer checklist

Store availability timestamps; make as-of joins explicit; fit preprocessing within folds; audit deleted rows; test delayed publications; examine missingness by regime.

## Scope and limitations

No cleaning method is universally correct. Results are conditional on the observation mechanism, access to historic releases and the model's purpose.

## Background reference

[Federal Reserve SR 26-2: Revised Guidance on Model Risk Management, 17 April 2026](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm). This reference is for contextual reading and does not independently validate the illustrative example above.

## Related MUSITU page

[Explore relevant MUSITU information](/research/). Describing a research method does not assert that a specific MUSITU product has implemented or independently validated it.
