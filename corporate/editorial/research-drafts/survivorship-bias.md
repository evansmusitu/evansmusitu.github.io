# Survivorship bias in financial research datasets

**Editorial status:** Draft for factual, financial-content, rights and publication review — **not approved for public release**.  
**Primary search intent:** survivorship bias historical stock datasets  
**Language:** English (original); localized versions not approved.  
**Article type:** Technical explainer; no proprietary or customer data.  

## Research question

A study of firms trading today may silently omit firms that failed, delisted or merged before the present. Using only surviving securities to reconstruct past performance can produce an unrealistically strong picture of historical opportunities. The data universe must match what a researcher could reasonably have selected at each earlier date.

## Method and reproducibility

Define membership using point-in-time records rather than the latest constituent list. Preserve delisted observations, corporate actions and the security's status at each date. Record the differences between issuer identity, security identity and symbol changes. Verify treatment of dividends, splits, suspended trading and missing terminal prices. When historical identifiers cannot be reconstructed, qualify the study and compare sensitivity to plausible exclusions.

## Worked conceptual example

A report evaluates ten years of an index using companies included today. A company that disappeared after a severe loss may be absent from the chosen dataset. Even if every surviving company's return is computed correctly, the study does not recreate the earlier investment opportunity set. The right comparison uses index membership as it changed at the time and an appropriate total-return convention.

## Failure modes and how to challenge the result

Survivorship can affect strategies, mutual-fund databases, analyst forecasts and even academic corpora. Watch for filters such as 'has ten years of price history' because those can exclude new listings and failures. Treat unexplained missing data as a research issue, not a harmless cleaning inconvenience. Document security master sources and update policies.

## Reviewer checklist

Use point-in-time constituents; retain delistings; track identifier changes; document exclusions; audit missing endpoints; disclose unresolved data gaps.

## Scope and limitations

The absence of historical coverage may make a finding exploratory only. Do not infer actual investor outcomes from a reconstructed dataset without execution and fee assumptions.

## Background reference

[Federal Reserve, revised model-risk guidance SR 26-2 (2026)](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm). This reference is for contextual reading and does not independently validate the illustrative example above.

## Related MUSITU page

[Explore relevant MUSITU information](/research/). Describing a research method does not assert that a specific MUSITU product has implemented or independently validated it.
