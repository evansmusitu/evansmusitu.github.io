# Scenario analysis and financial stress tests that can be audited

**Editorial status:** Draft for factual, financial-content, rights and publication review — **not approved for public release**.  
**Primary search intent:** financial scenario analysis stress testing methodology  
**Language:** English (original); localized versions not approved.  
**Article type:** Technical explainer; no proprietary or customer data.  

## Research question

A forecast is usually organized around what is expected; a stress test asks how a system behaves under an adverse but intelligible set of assumptions. A useful scenario does not need to predict precisely when an event will occur. It needs explicit shocks, a defensible transmission mechanism and an honest account of what the model leaves out.

## Method and reproducibility

Start by declaring the entity and decision being evaluated. List the risk factors, starting portfolio or balance-sheet state and scenario horizon. Apply a coherent set of shocks, including correlations or dependencies that may change under stress. Record any dynamic management response separately from the mechanical calculation. Compare the scenario to a baseline and document second-order effects such as liquidity, transaction costs and feedback loops.

## Worked conceptual example

A simplified portfolio holds assets sensitive to interest rates and foreign exchange. A scenario could combine a higher discount rate with a sharp currency move. Applying both shocks independently may miss their interactions, while treating them as perfectly correlated may exaggerate them. Rather than proclaiming a single correct number, report the exact factor changes, pricing rules and sensitivity to different co-movement assumptions.

## Failure modes and how to challenge the result

Scenario narratives are not evidence that a specific event is likely. Models may omit liquidity freezes, settlement delays, nonlinearity or data revisions. Reverse stress testing starts with a failure condition and searches for plausible combinations that produce it; it must not be confused with estimating event probability. Include human challenge of shock sizes and mechanisms.

## Reviewer checklist

State scenario horizon; disclose shock vector; retain baseline; test interactions; record modelling simplifications; seek independent challenge.

## Scope and limitations

Stress testing is a decision-support exercise; its outputs depend on assumptions and may substantially understate extreme conditions. It is not a forecast or trading instruction.

## Background reference

[Federal Reserve, revised model-risk guidance SR 26-2 (2026)](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm). This reference is for contextual reading and does not independently validate the illustrative example above.

## Related MUSITU page

[Explore relevant MUSITU information](/products/fmi/). Describing a research method does not assert that a specific MUSITU product has implemented or independently validated it.
