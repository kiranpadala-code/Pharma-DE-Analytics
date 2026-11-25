# 10 – Analytics Requirements

## 1. Purpose

Define the business questions and candidate output datasets that the curated warehouse should support.

These are analytical requirements, not a commitment that every metric can be calculated from the supplied data. Confirm availability, grain, and definitions during modeling.

## 2. Candidate outputs

### 2.1 Territory performance – `mart_territory_performance`

**Candidate grain:** Reporting month + territory; product may need to be included depending on the reporting question.

Potential measures:
- Call count.
- Unique HCPs visited.
- Sample quantity distributed.
- TRx and NRx.
- Market share using an appropriate numerator/denominator aggregation.
- Active representative count.

Questions:
- Which territories have the highest field activity?
- How do prescription measures vary by territory?
- Which territories have lower activity or prescription trends?

### 2.2 Representative activity – `mart_rep_performance`

**Candidate grain:** Reporting month + representative.

Potential measures:
- Calls.
- Unique HCPs visited.
- Average call duration.
- Sample quantity distributed.
- Target HCP coverage, if target definitions support it.

Prescription measures should not be attributed to a representative unless an explicit attribution rule exists. Territory prescription results are not automatically individual representative results.

### 2.3 HCP engagement – `mart_hcp_engagement`

**Candidate grain:** Reporting month + HCP; product may be required for prescription-level analysis.

Potential attributes/measures:
- HCP name and specialty.
- Account and territory.
- Calls and last call date.
- Sample quantity.
- TRx, NRx, and prescription change.

Questions:
- Which HCPs have high or low engagement?
- How do HCP prescription trends vary by specialty?
- Which target HCPs have not been contacted in the reporting period?

### 2.4 Product performance – `mart_product_performance`

**Candidate grain:** Reporting month + product.

Potential measures:
- Calls discussing product.
- Sample quantity.
- TRx and NRx.
- Market share.
- Prescription change.
- Number of territories with activity.

Do not sum repeated market totals or calculate unweighted averages of percentages.

### 2.5 Sample and prescription trend – `mart_sample_effectiveness`

**Candidate grain:** HCP + product + analysis period, subject to a defined observation window.

Potential measures:
- Sample date and quantity.
- Pre-sample prescription measure.
- Post-sample prescription measure.
- Change between observation windows.

This is an observational comparison. It does not establish that samples caused prescription changes. Confounding factors and comparison design would be needed for causal claims.

### 2.6 Monthly commercial summary – `mart_monthly_commercial_summary`

**Candidate grain:** Reporting month, with additional dimensions only if explicitly required.

Potential measures:
- Total calls.
- Unique HCPs visited.
- Sample quantity.
- TRx and NRx.
- Market share with a defined aggregation method.
- Active representative count.
- Territory count.

## 3. Metric definitions to confirm

| Metric | Definition needed |
|---|---|
| Call count | Count of unique call IDs |
| Unique HCPs visited | Distinct NPI values with a qualifying call |
| Sample quantity | Sum of `qty_dropped`; confirm units are comparable |
| TRx | Sum of `trx_count` at a non-duplicating grain |
| NRx | Sum of `nrx_count` at a non-duplicating grain |
| Market share | Numerator and denominator at a common comparison grain |
| HCP coverage | Define eligible target HCP denominator and period |
| Call compliance rate | Compliant calls / eligible calls; define eligibility |
| Sample effectiveness | Define pre/post windows and comparison method |

## 4. Analytics acceptance criteria

- Every output has a documented grain.
- Every metric has a definition and aggregation rule.
- Joins do not inflate measures.
- Null and excluded records are handled transparently.
- Totals reconcile to the underlying fact models.
- Outputs can be queried directly in Snowflake.
