# How to verify an AI-assisted financial research answer

**Editorial status:** Draft for factual, financial-content, rights and publication review — **not approved for public release**.  
**Primary search intent:** verify AI generated financial research evidence sources  
**Language:** English (original); localized versions not approved.  
**Article type:** Technical explainer; no proprietary or customer data.  

## Research question

An AI response can be fluent while making an unsupported inference, mixing incompatible periods or citing a source that does not establish the claim. A reliable research workflow separates the request, source material, calculations, interpretation and final communication. The task is to verify the evidence path, not to judge the model by confidence or prose quality.

## Method and reproducibility

First list every externally checkable claim and every computed value. Confirm that each cited source exists, is accessible, is dated appropriately and supports the specific statement. Recalculate material arithmetic with an independent tool or reproducible code. Mark estimates and projections as assumptions. Require a human reviewer to challenge financial interpretations and to identify where the evidence stops. Preserve links, calculation inputs, units and caveats in a compact output manifest.

## Worked conceptual example

An assistant states that a portfolio outperformed its benchmark by eight percentage points. To evaluate the claim, the reviewer needs both return definitions, matching dates, currency, fee treatment, dividend convention and benchmark membership. If the values are 12% and 4%, the arithmetic difference is eight percentage points; it is not an 8% relative increase. A citation to a general market article does not validate the specific calculation.

## Failure modes and how to challenge the result

Look for invented sources, outdated revisions, omitted negative findings, figures transferred between jurisdictions and summaries that erase uncertainty. Automated citation extraction can help locate references but does not establish truth. Even a fully reproducible computation can answer the wrong business question if the metric or population was misidentified.

## Reviewer checklist

Extract claims; validate each source; recalculate numbers; test date/unit alignment; record uncertainty; require human sign-off for consequential decisions.

## Scope and limitations

This procedure reduces preventable errors but cannot guarantee accuracy. It does not establish that MUSITU Axiom or any other product automatically performs all these checks.

## Background reference

[NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework). This reference is for contextual reading and does not independently validate the illustrative example above.

## Related MUSITU page

[Explore relevant MUSITU information](/products/axiom/). Describing a research method does not assert that a specific MUSITU product has implemented or independently validated it.
