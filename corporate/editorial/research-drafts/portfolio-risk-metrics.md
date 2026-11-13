# Interpreting portfolio volatility, drawdown and tail risk

**Editorial status:** Draft for factual, financial-content, rights and publication review — **not approved for public release**.  
**Primary search intent:** portfolio volatility drawdown risk metrics explained  
**Language:** English (original); localized versions not approved.  
**Article type:** Technical explainer; no proprietary or customer data.  

## Research question

No single risk number describes all ways a portfolio can lose value. Volatility measures dispersion under a return convention, drawdown describes a particular path from peak to trough, and tail-oriented measures focus on adverse outcomes. These metrics answer different questions and can disagree without any one of them being wrong.

## Method and reproducibility

Specify the holdings, valuation time, currency, return interval, rebalancing convention and fee treatment before computing anything. Define sample versus population volatility and annualization assumptions. Calculate maximum drawdown from a complete wealth index, not from isolated return observations. For quantiles and expected shortfall, specify empirical or parametric estimation, confidence level and lookback window. Test how the estimates change under alternative regimes, stale marks or missing prices.

## Worked conceptual example

Consider returns of +10% followed by −10%. The arithmetic sum is zero, but the compounded wealth factor is 1.10 × 0.90 = 0.99, a 1% loss. The drawdown after the second period is measured relative to the peak, not the original starting value. Volatility alone cannot convey this path dependence. A concise risk table should therefore show more than a single annualized standard deviation.

## Failure modes and how to challenge the result

Avoid comparing annualized figures from different frequencies without disclosure. Thin trading can understate observed variability; extreme losses may be poorly represented in a short sample. Value-at-risk style estimates are thresholds rather than worst-case loss ceilings. Historical drawdown depends on the observed sample and its initial boundary.

## Reviewer checklist

Declare return definitions; include currency and fees; compute complementary metrics; show stress periods; present sensitivity bands; avoid promises of safety.

## Scope and limitations

Risk estimates are descriptive model outputs, not guarantees or investment advice. Some distributions may make familiar parametric assumptions unsuitable.

## Background reference

[Federal Reserve, revised model-risk guidance SR 26-2 (2026)](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm). This reference is for contextual reading and does not independently validate the illustrative example above.

## Related MUSITU page

[Explore relevant MUSITU information](/solutions/finance-research/). Describing a research method does not assert that a specific MUSITU product has implemented or independently validated it.
