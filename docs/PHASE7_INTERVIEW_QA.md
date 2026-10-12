# Technical interview practice — 65 substantial answers

Practice material, not a claim that the user personally performed every implementation step. Codex generated and executed substantial work. Explain only reviewed evidence and actual personal contributions. Answers target roughly 45–90 seconds at a conversational pace; rehearse and adapt rather than memorize.

## 01. Why call this pharmaceutical intelligence when it uses NHS prescribing data?
Category: Business framing

**Spoken answer**

I would define the intelligence narrowly: it organizes observed dispensing activity, ingredient cost, forecast reliability and analytical review questions for a pharmaceutical context. The public source makes the work inspectable, but it cannot replace manufacturer sales, distribution, contracting or patient-level evidence required for many commercial decisions. The design connects executive summaries to their evidence, so an analyst can distinguish a descriptive finding from model performance and an illustrative planning assumption. For an interview, the value is demonstrating disciplined analysis and communication across those layers rather than presenting public records as a complete pharmaceutical market. The unit of analysis is recorded prescription activity, not receipts earned by a manufacturer. The dashboard explicitly states that NIC is NHS ingredient cost and labels monitoring scores as analytical priorities.

**Four points to retain**

- I would define the intelligence narrowly: it organizes observed dispensing activity, ingredient cost, forecast reliability and analytical review questions for a pharmaceutical context.
- The public source makes the work inspectable, but it cannot replace manufacturer sales, distribution, contracting or patient-level evidence required for many commercial decisions.
- The design connects executive summaries to their evidence, so an analyst can distinguish a descriptive finding from model performance and an illustrative planning assumption.
- For an interview, the value is demonstrating disciplined analysis and communication across those layers rather than presenting public records as a complete pharmaceutical market.

**Technical explanation:** The unit of analysis is recorded prescription activity, not receipts earned by a manufacturer.

**Project-specific example:** The dashboard explicitly states that NIC is NHS ingredient cost and labels monitoring scores as analytical priorities.

**Likely follow-up:** What would change with authorized commercial sales data?

**Common mistake to avoid:** Equating prescribing intelligence with measured sales opportunity.

## 02. Is prescription-item count the same as pharmaceutical demand?
Category: Business framing

**Spoken answer**

An item is a recorded occurrence of a dispensed prescription product, so it is a useful activity measure with a precise administrative definition. It is not a unique patient, treatment course, tablet count or all demand, because repeat prescriptions and different presentations can contribute multiple items. The source excludes activity outside its stated community-reimbursement scope, and some observed absence can reflect reporting or applicability rather than no patient need. I would call the forecast a forecast of recorded activity and request utilization, stock, population and commercial data before interpreting it as total market demand. Separate the measured target from the broader latent business concept it only partially represents. The forecast target is prescription_items; physical total_quantity is retained with unit and not pooled across tablet and liquid records.

**Four points to retain**

- An item is a recorded occurrence of a dispensed prescription product, so it is a useful activity measure with a precise administrative definition.
- It is not a unique patient, treatment course, tablet count or all demand, because repeat prescriptions and different presentations can contribute multiple items.
- The source excludes activity outside its stated community-reimbursement scope, and some observed absence can reflect reporting or applicability rather than no patient need.
- I would call the forecast a forecast of recorded activity and request utilization, stock, population and commercial data before interpreting it as total market demand.

**Technical explanation:** Separate the measured target from the broader latent business concept it only partially represents.

**Project-specific example:** The forecast target is prescription_items; physical total_quantity is retained with unit and not pooled across tablet and liquid records.

**Likely follow-up:** How would you connect this proxy to an actual demand planning decision?

**Common mistake to avoid:** Renaming item totals as patient counts or total market volume.

## 03. Why did the project use public data instead of manufacturer sales data?
Category: Business framing

**Spoken answer**

Public NHSBSA records allow source attribution, fixed snapshots and independent reconciliation without claiming access to proprietary data that was not supplied. They still support analyst-relevant questions about data quality, SQL grains, cost ratios, time-series evaluation and transparent dashboard communication across an end-to-end pipeline. The tradeoff is that commercial variables such as net sales, discounts, channel inventory and promotion are missing, so commercial impact cannot be estimated honestly. If authorized company data became available, I would redefine measures and joins first, then validate a separate analysis rather than transferring these public-source conclusions directly. Data suitability depends on the decision, grain, provenance and missing business variables, not on whether a dataset is large. The repository records an NHSBSA chemical filter and immutable receipts rather than an Axtria or manufacturer connection.

**Four points to retain**

- Public NHSBSA records allow source attribution, fixed snapshots and independent reconciliation without claiming access to proprietary data that was not supplied.
- They still support analyst-relevant questions about data quality, SQL grains, cost ratios, time-series evaluation and transparent dashboard communication across an end-to-end pipeline.
- The tradeoff is that commercial variables such as net sales, discounts, channel inventory and promotion are missing, so commercial impact cannot be estimated honestly.
- If authorized company data became available, I would redefine measures and joins first, then validate a separate analysis rather than transferring these public-source conclusions directly.

**Technical explanation:** Data suitability depends on the decision, grain, provenance and missing business variables, not on whether a dataset is large.

**Project-specific example:** The repository records an NHSBSA chemical filter and immutable receipts rather than an Axtria or manufacturer connection.

**Likely follow-up:** Which commercial fields would you request first?

**Common mistake to avoid:** Implying proprietary access or client delivery.

## 04. What exactly does NIC represent?
Category: Business framing

**Spoken answer**

NIC means net ingredient cost in this source, an administrative ingredient-cost measure associated with recorded dispensing rather than a manufacturer revenue measure. An analyst needs to preserve that definition when displaying pounds, because the word cost alone can invite an unsupported interpretation as final expenditure or profit. The weighted NIC-per-item ratio describes the average accounting amount per recorded item within a scope, but presentation mix and unit-cost changes can both affect it. I would explain the source definition beside the KPI and keep financial planning claims conditional on additional reimbursement, discount and business-accounting information. The dashboard calculates aggregate NIC divided by aggregate items; that is not a mean of row-level unit ratios. The executive page displays the statement “NIC is NHS net ingredient cost, not manufacturer sales revenue.”

**Four points to retain**

- NIC means net ingredient cost in this source, an administrative ingredient-cost measure associated with recorded dispensing rather than a manufacturer revenue measure.
- An analyst needs to preserve that definition when displaying pounds, because the word cost alone can invite an unsupported interpretation as final expenditure or profit.
- The weighted NIC-per-item ratio describes the average accounting amount per recorded item within a scope, but presentation mix and unit-cost changes can both affect it.
- I would explain the source definition beside the KPI and keep financial planning claims conditional on additional reimbursement, discount and business-accounting information.

**Technical explanation:** The dashboard calculates aggregate NIC divided by aggregate items; that is not a mean of row-level unit ratios.

**Project-specific example:** The executive page displays the statement “NIC is NHS net ingredient cost, not manufacturer sales revenue.”

**Likely follow-up:** Does lower NIC/item establish an efficiency improvement?

**Common mistake to avoid:** Calling NIC manufacturer sales, realized margin or final total NHS spend.

## 05. Why did NIC fall while item volume increased?
Category: Business framing

**Spoken answer**

The observed totals can move in opposite directions because ingredient cost is item volume multiplied by a weighted per-item amount influenced by presentation mix. The project separates volume, presentation mix and within-presentation NIC-per-item contributions using an exact symmetric accounting decomposition whose components reconcile to the observed change. The within-presentation contribution is sufficiently negative to offset positive volume and mix contributions in the latest annual comparison, which explains the identity mathematically. That does not identify the real-world cause of lower ratios; evidence about pricing, reimbursement, supply and other mechanisms would be needed for a causal explanation. Use C = V × Σ(s_j × p_j), where the three factors are aggregate volume, item shares and presentation-specific NIC/item. The verified 2025 comparison shows positive volume and mix effects but a negative within-presentation ratio effect.

**Four points to retain**

- The observed totals can move in opposite directions because ingredient cost is item volume multiplied by a weighted per-item amount influenced by presentation mix.
- The project separates volume, presentation mix and within-presentation NIC-per-item contributions using an exact symmetric accounting decomposition whose components reconcile to the observed change.
- The within-presentation contribution is sufficiently negative to offset positive volume and mix contributions in the latest annual comparison, which explains the identity mathematically.
- That does not identify the real-world cause of lower ratios; evidence about pricing, reimbursement, supply and other mechanisms would be needed for a causal explanation.

**Technical explanation:** Use C = V × Σ(s_j × p_j), where the three factors are aggregate volume, item shares and presentation-specific NIC/item.

**Project-specific example:** The verified 2025 comparison shows positive volume and mix effects but a negative within-presentation ratio effect.

**Likely follow-up:** Could patent expiry or negotiation explain the result?

**Common mistake to avoid:** Asserting a price mechanism or realized savings from an accounting identity.

## 06. What business value does this portfolio demonstrate?
Category: Business framing

**Spoken answer**

It demonstrates how an analyst can convert administrative data into a coherent evidence chain, from acquisition and definitions through SQL and a usable executive interface. A reviewer can inspect denominators, forecast origins, missing evidence and scenario assumptions rather than relying on an attractive chart with unclear business meaning. The monitoring register makes analytical investigations explicit, while sensitivity tests reveal which apparent priorities depend on policy choices that need domain-user agreement. I would describe these capabilities as decision support and interview evidence, not quantified company impact, because no intervention or actual client adoption occurred in the project. Business usefulness is demonstrated through traceability and decision boundaries; realized business outcomes require a separate adoption and outcome evaluation. Each proposed investigation links to a supporting source output and rule, while hypothetical scenarios have separate evidence labels.

**Four points to retain**

- It demonstrates how an analyst can convert administrative data into a coherent evidence chain, from acquisition and definitions through SQL and a usable executive interface.
- A reviewer can inspect denominators, forecast origins, missing evidence and scenario assumptions rather than relying on an attractive chart with unclear business meaning.
- The monitoring register makes analytical investigations explicit, while sensitivity tests reveal which apparent priorities depend on policy choices that need domain-user agreement.
- I would describe these capabilities as decision support and interview evidence, not quantified company impact, because no intervention or actual client adoption occurred in the project.

**Technical explanation:** Business usefulness is demonstrated through traceability and decision boundaries; realized business outcomes require a separate adoption and outcome evaluation.

**Project-specific example:** Each proposed investigation links to a supporting source output and rule, while hypothetical scenarios have separate evidence labels.

**Likely follow-up:** How would you measure usefulness with actual business users?

**Common mistake to avoid:** Inventing sales uplift, cost reduction or production adoption.

## 07. What is the difference between source rows and analytical rows?
Category: Data engineering

**Spoken answer**

Source rows preserve the administrative granularity returned by the API, including available dimensions needed to understand repeated product, region and month records. The cleaned monthly dataset aggregates compatible records to an explicit business grain, so fewer rows do not imply that useful item or cost totals were discarded. Before aggregation, source keys and optional fields are validated; afterwards the monthly key and reconciliation checks verify uniqueness and conservation of the additive measures. I would explain both grains before presenting row counts, because a simple count of duplicates at the wrong grain can confuse legitimate dimensional variation with duplicate data. Aggregation should conserve additive measures while retaining identifiers and units required for subsequent joins. The verified project transforms 50,456 source rows into 3,920 monthly analytical rows with matching item and NIC totals.

**Four points to retain**

- Source rows preserve the administrative granularity returned by the API, including available dimensions needed to understand repeated product, region and month records.
- The cleaned monthly dataset aggregates compatible records to an explicit business grain, so fewer rows do not imply that useful item or cost totals were discarded.
- Before aggregation, source keys and optional fields are validated; afterwards the monthly key and reconciliation checks verify uniqueness and conservation of the additive measures.
- I would explain both grains before presenting row counts, because a simple count of duplicates at the wrong grain can confuse legitimate dimensional variation with duplicate data.

**Technical explanation:** Aggregation should conserve additive measures while retaining identifiers and units required for subsequent joins.

**Project-specific example:** The verified project transforms 50,456 source rows into 3,920 monthly analytical rows with matching item and NIC totals.

**Likely follow-up:** Which source dimensions disappear during monthly aggregation?

**Common mistake to avoid:** Calling every repeated product-month source row a duplicate.

## 08. How does the project retain acquisition provenance?
Category: Data engineering

**Spoken answer**

Acquisition stores filtered API responses and receipts rather than treating the online endpoint as a permanently unchanged input that can be refreshed invisibly. Each receipt records the request reference, download information and a content hash, so the analytical release can be tied to the records actually used. The pipeline refuses to overwrite existing raw evidence during refresh, and later phases compare protected hashes before consuming cleaned or analytical artifacts. That makes a revised download a new vintage requiring versioned validation, which is important because source corrections can alter a historical series without any code change. SHA-256 checks detect byte differences; they support integrity but do not by themselves establish the truth of a source record. The raw directory includes monthly filtered response files and corresponding receipt JSON files for the fixed extract.

**Four points to retain**

- Acquisition stores filtered API responses and receipts rather than treating the online endpoint as a permanently unchanged input that can be refreshed invisibly.
- Each receipt records the request reference, download information and a content hash, so the analytical release can be tied to the records actually used.
- The pipeline refuses to overwrite existing raw evidence during refresh, and later phases compare protected hashes before consuming cleaned or analytical artifacts.
- That makes a revised download a new vintage requiring versioned validation, which is important because source corrections can alter a historical series without any code change.

**Technical explanation:** SHA-256 checks detect byte differences; they support integrity but do not by themselves establish the truth of a source record.

**Project-specific example:** The raw directory includes monthly filtered response files and corresponding receipt JSON files for the fixed extract.

**Likely follow-up:** What happens if the provider revises a past month?

**Common mistake to avoid:** Assuming a reproducible request URL guarantees identical future responses.

## 09. How are identifier types preserved during ingestion?
Category: Data engineering

**Spoken answer**

Presentation and chemical codes are identifiers, so they should be loaded as strings rather than numeric measures even when some characters look like digits. Otherwise leading zeros can disappear, and that seemingly minor type conversion can break filters, joins, source comparisons or a supposedly unique business key. The ingestion checks required columns and configured chemical identity before normalizing dates and measures, keeping physical units and optional missing fields explicit. I would test type handling at boundaries and reject malformed required identifiers instead of silently coercing them into an alternative code that appears to work. Identifiers carry categorical meaning; numerical operations on them have no business interpretation. The ingestion reader specifies string dtypes and retains the leading-zero atorvastatin chemical code used in the API filter.

**Four points to retain**

- Presentation and chemical codes are identifiers, so they should be loaded as strings rather than numeric measures even when some characters look like digits.
- Otherwise leading zeros can disappear, and that seemingly minor type conversion can break filters, joins, source comparisons or a supposedly unique business key.
- The ingestion checks required columns and configured chemical identity before normalizing dates and measures, keeping physical units and optional missing fields explicit.
- I would test type handling at boundaries and reject malformed required identifiers instead of silently coercing them into an alternative code that appears to work.

**Technical explanation:** Identifiers carry categorical meaning; numerical operations on them have no business interpretation.

**Project-specific example:** The ingestion reader specifies string dtypes and retains the leading-zero atorvastatin chemical code used in the API filter.

**Likely follow-up:** How would you validate an unexpected identifier format?

**Common mistake to avoid:** Converting BNF identifiers to integers because they resemble numbers.

## 10. How did the project handle missing months?
Category: Data engineering

**Spoken answer**

It constructs a calendar-aware coverage view so that an unobserved month can be distinguished from a recorded zero rather than disappearing in a sorted table. Coverage diagnostics identify internal gaps and never-observed combinations, and reporting formulas disclose when a comparison lacks sufficient observed periods or a valid denominator. For forecasting, eligible histories must satisfy documented contiguous-history requirements; incomplete series are not silently repaired simply to increase the number of fitted models. The interpretation remains cautious because absence can reflect applicability, reporting, launch or discontinuation mechanisms, none of which can be established from a missing cell alone. A complete diagnostic spine and observed fact have different purposes; the spine preserves unknown cells without creating observed activity. The dashboard coverage grid combines observed rows with the absence-only table rather than assuming the absence file already contains every calendar cell.

**Four points to retain**

- It constructs a calendar-aware coverage view so that an unobserved month can be distinguished from a recorded zero rather than disappearing in a sorted table.
- Coverage diagnostics identify internal gaps and never-observed combinations, and reporting formulas disclose when a comparison lacks sufficient observed periods or a valid denominator.
- For forecasting, eligible histories must satisfy documented contiguous-history requirements; incomplete series are not silently repaired simply to increase the number of fitted models.
- The interpretation remains cautious because absence can reflect applicability, reporting, launch or discontinuation mechanisms, none of which can be established from a missing cell alone.

**Technical explanation:** A complete diagnostic spine and observed fact have different purposes; the spine preserves unknown cells without creating observed activity.

**Project-specific example:** The dashboard coverage grid combines observed rows with the absence-only table rather than assuming the absence file already contains every calendar cell.

**Likely follow-up:** Would you impute gaps for a different operational application?

**Common mistake to avoid:** Treating an unobserved row as a known zero.

## 11. Why did you avoid zero-filling missing values?
Category: Data engineering

**Spoken answer**

Zero is an observed numerical statement, while missing means the activity is not known in the extract, so replacing one with the other changes the meaning of evidence. That change can bias item totals, growth rates, variability, forecast scales and model comparisons, particularly for sparse presentation-region combinations or newly appearing products. The project retains nulls in the coverage spine and uses explicit eligibility or unavailable statuses where a required calculation cannot be supported by observed data. If a business rule later established that a particular absence truly means no activity, I would encode that rule with provenance and test it in a separate version. Imputation is a modeling assumption or a source-defined semantic rule, not a neutral formatting choice. Empty dashboard selections show a no-observations message, and unscored presentations are not assigned zero performance.

**Four points to retain**

- Zero is an observed numerical statement, while missing means the activity is not known in the extract, so replacing one with the other changes the meaning of evidence.
- That change can bias item totals, growth rates, variability, forecast scales and model comparisons, particularly for sparse presentation-region combinations or newly appearing products.
- The project retains nulls in the coverage spine and uses explicit eligibility or unavailable statuses where a required calculation cannot be supported by observed data.
- If a business rule later established that a particular absence truly means no activity, I would encode that rule with provenance and test it in a separate version.

**Technical explanation:** Imputation is a modeling assumption or a source-defined semantic rule, not a neutral formatting choice.

**Project-specific example:** Empty dashboard selections show a no-observations message, and unscored presentations are not assigned zero performance.

**Likely follow-up:** How would you distinguish a legitimate observed zero?

**Common mistake to avoid:** Using fillna(0) to make every chart and metric convenient.

## 12. How are anomalous records handled?
Category: Data engineering

**Spoken answer**

An anomaly flag indicates a need for review, not a confirmed data error, especially when a small presentation can show large relative changes from a low baseline. The project preserves the original observations and IQR flags, then adds retrospective MAD, calendar-change and prior rolling-median diagnostics with explicit interpretations. Robustness analysis examines whether broad findings depend on flagged observations or dominant presentations, while original analytical results remain traceable and unchanged. I would seek external source confirmation before correcting or deleting a suspicious value, and keep diagnostic exclusions separate from the primary reported dataset and forecast treatment. Retrospective classifications may inspect later observations; they cannot be imported as future-known training interventions. The anomaly code retains legacy flags and describes potential structural shifts without asserting that they are confirmed errors.

**Four points to retain**

- An anomaly flag indicates a need for review, not a confirmed data error, especially when a small presentation can show large relative changes from a low baseline.
- The project preserves the original observations and IQR flags, then adds retrospective MAD, calendar-change and prior rolling-median diagnostics with explicit interpretations.
- Robustness analysis examines whether broad findings depend on flagged observations or dominant presentations, while original analytical results remain traceable and unchanged.
- I would seek external source confirmation before correcting or deleting a suspicious value, and keep diagnostic exclusions separate from the primary reported dataset and forecast treatment.

**Technical explanation:** Retrospective classifications may inspect later observations; they cannot be imported as future-known training interventions.

**Project-specific example:** The anomaly code retains legacy flags and describes potential structural shifts without asserting that they are confirmed errors.

**Likely follow-up:** When would an extreme point justify correction?

**Common mistake to avoid:** Deleting outliers automatically or using future anomaly labels during backtesting.

## 13. How does hash protection improve reproducibility?
Category: Data engineering

**Spoken answer**

It provides a concrete comparison between the artifacts used at baseline and the files present after a later phase, rather than relying on a statement that nothing changed. The protected inventory covers raw data, cleaned tables, frozen selections, prior reports and executed notebooks, with explicit handling of missing as well as changed files. New portfolio materials and authorized presentation edits are recorded separately, so the audit can show additions without silently expanding what counts as historical evidence. I would pair hashes with numerical checks because identical bytes confirm preservation, while independent reductions test whether the preserved calculations and interpretations are internally consistent. Integrity, reproducibility and validity are related but different: a hash only addresses the first directly. Phase 7 captures its protected manifest before portfolio edits and compares every named file at final audit.

**Four points to retain**

- It provides a concrete comparison between the artifacts used at baseline and the files present after a later phase, rather than relying on a statement that nothing changed.
- The protected inventory covers raw data, cleaned tables, frozen selections, prior reports and executed notebooks, with explicit handling of missing as well as changed files.
- New portfolio materials and authorized presentation edits are recorded separately, so the audit can show additions without silently expanding what counts as historical evidence.
- I would pair hashes with numerical checks because identical bytes confirm preservation, while independent reductions test whether the preserved calculations and interpretations are internally consistent.

**Technical explanation:** Integrity, reproducibility and validity are related but different: a hash only addresses the first directly.

**Project-specific example:** Phase 7 captures its protected manifest before portfolio edits and compares every named file at final audit.

**Likely follow-up:** What if a protected file needs a genuine correction?

**Common mistake to avoid:** Updating the baseline hash to hide a discrepancy.

## 14. How would you extend the pipeline to more medicines?
Category: Data engineering

**Spoken answer**

I would first generalize the configured chemical scope and identifiers while keeping a clear source-to-fact grain, because medicine categories can have different presentations and units. Partitioning acquisition and validated storage by medicine and month would improve maintainability, but the same dimensional uniqueness and conservation checks would still be required. Forecast eligibility, feature behavior and monitoring normalization would need review for each scope; scores across unrelated medicine cohorts should not be compared without a meaningful shared policy. I would add representative fixture tests, capacity measurements and release-aware provenance before scaling the dashboard, rather than assuming that a larger extraction preserves every current analytical assumption. Scaling means validating grains, denominators, storage and modeling assumptions, not just enlarging the API filter. The current repository explicitly scopes one atorvastatin chemical; generalizing it is proposed future work, not an executed multi-medicine result.

**Four points to retain**

- I would first generalize the configured chemical scope and identifiers while keeping a clear source-to-fact grain, because medicine categories can have different presentations and units.
- Partitioning acquisition and validated storage by medicine and month would improve maintainability, but the same dimensional uniqueness and conservation checks would still be required.
- Forecast eligibility, feature behavior and monitoring normalization would need review for each scope; scores across unrelated medicine cohorts should not be compared without a meaningful shared policy.
- I would add representative fixture tests, capacity measurements and release-aware provenance before scaling the dashboard, rather than assuming that a larger extraction preserves every current analytical assumption.

**Technical explanation:** Scaling means validating grains, denominators, storage and modeling assumptions, not just enlarging the API filter.

**Project-specific example:** The current repository explicitly scopes one atorvastatin chemical; generalizing it is proposed future work, not an executed multi-medicine result.

**Likely follow-up:** How would you organize partitions and incremental updates?

**Common mistake to avoid:** Claiming performance or validity at a scale that was never tested.

## 15. Why was DuckDB a suitable choice?
Category: SQL and database design

**Spoken answer**

DuckDB supports analytical SQL over local data and integrates with pandas and Parquet, which suits a reproducible portfolio that does not require a managed database service. It makes reporting definitions inspectable in SQL, including calendar logic, grouped totals, window comparisons and controlled dimensional joins that can be checked against independent Python calculations. The local deployment reduces infrastructure and credential requirements, but it is not evidence that the same architecture would satisfy a large multi-user transactional or distributed workload. I would reassess storage, concurrency and operational requirements for production while retaining the benefit of explicit metric definitions and portable reporting artifacts for the dashboard. The dashboard consumes exported Parquet marts read-only; it does not execute database writes on every interaction. The project validates DuckDB reporting views against saved outputs, then registers the dashboard datasets with schema and hash contracts.

**Four points to retain**

- DuckDB supports analytical SQL over local data and integrates with pandas and Parquet, which suits a reproducible portfolio that does not require a managed database service.
- It makes reporting definitions inspectable in SQL, including calendar logic, grouped totals, window comparisons and controlled dimensional joins that can be checked against independent Python calculations.
- The local deployment reduces infrastructure and credential requirements, but it is not evidence that the same architecture would satisfy a large multi-user transactional or distributed workload.
- I would reassess storage, concurrency and operational requirements for production while retaining the benefit of explicit metric definitions and portable reporting artifacts for the dashboard.

**Technical explanation:** The dashboard consumes exported Parquet marts read-only; it does not execute database writes on every interaction.

**Project-specific example:** The project validates DuckDB reporting views against saved outputs, then registers the dashboard datasets with schema and hash contracts.

**Likely follow-up:** When would you choose a server database instead?

**Common mistake to avoid:** Calling a local analytical engine a proven enterprise-scale service.

## 16. Why create a fact table instead of analyzing a single flat file?
Category: SQL and database design

**Spoken answer**

A fact table declares the grain of additive measures, which makes it easier to understand exactly what one row represents before building summaries or joins. Separate dimensions hold descriptive labels and identifiers, preventing repeated descriptive fields from obscuring which relationships must be unique when a report joins them. A calendar and coverage model can then preserve time semantics independently of observed rows, allowing meaningful missingness diagnostics and adjacent-month comparisons. The benefit is not architectural decoration; it is reducing double counting, ambiguous denominators and inconsistent report definitions while making the model understandable to another analyst. Fact grain and join cardinality are contracts that should be validated before interpreting a grouped result. The SQL model supports month-region-presentation reporting while keeping item counts and NIC distinct from physical quantities.

**Four points to retain**

- A fact table declares the grain of additive measures, which makes it easier to understand exactly what one row represents before building summaries or joins.
- Separate dimensions hold descriptive labels and identifiers, preventing repeated descriptive fields from obscuring which relationships must be unique when a report joins them.
- A calendar and coverage model can then preserve time semantics independently of observed rows, allowing meaningful missingness diagnostics and adjacent-month comparisons.
- The benefit is not architectural decoration; it is reducing double counting, ambiguous denominators and inconsistent report definitions while making the model understandable to another analyst.

**Technical explanation:** Fact grain and join cardinality are contracts that should be validated before interpreting a grouped result.

**Project-specific example:** The SQL model supports month-region-presentation reporting while keeping item counts and NIC distinct from physical quantities.

**Likely follow-up:** What makes a dimension join safe?

**Common mistake to avoid:** Adding star-schema labels without validating the actual grain.

## 17. What is the grain of the monthly analytical fact?
Category: SQL and database design

**Spoken answer**

The fact represents a month, reported region and BNF presentation combination, with the physical unit retained in the source-normalized analytical definition. That is more specific than medicine by month, so regional and presentation summaries are derived aggregations rather than independent source facts that can be added together. Business keys must remain populated and unique, and identifiers must have stable types so that label joins do not create additional rows or erase valid combinations. I would state the grain before discussing totals, because both duplicate prevention and missing-cell interpretation depend on knowing which combinations are expected versus actually observed. One month-region-presentation row contains additive observed item and NIC measures; it is not a patient or manufacturer sales transaction. The dashboard contract checks uniqueness of month, region_code and presentation_key in cost_analytics.

**Four points to retain**

- The fact represents a month, reported region and BNF presentation combination, with the physical unit retained in the source-normalized analytical definition.
- That is more specific than medicine by month, so regional and presentation summaries are derived aggregations rather than independent source facts that can be added together.
- Business keys must remain populated and unique, and identifiers must have stable types so that label joins do not create additional rows or erase valid combinations.
- I would state the grain before discussing totals, because both duplicate prevention and missing-cell interpretation depend on knowing which combinations are expected versus actually observed.

**Technical explanation:** One month-region-presentation row contains additive observed item and NIC measures; it is not a patient or manufacturer sales transaction.

**Project-specific example:** The dashboard contract checks uniqueness of month, region_code and presentation_key in cost_analytics.

**Likely follow-up:** Why does the physical unit still matter?

**Common mistake to avoid:** Treating a presentation row as a unique patient or ignoring unit distinctions.

## 18. How do you prevent duplicate aggregation?
Category: SQL and database design

**Spoken answer**

I would validate the source business key at its true dimensional grain first, because repeated simpler product-month keys may be legitimate rather than accidental duplicates. After monthly aggregation, the fact key must be unique, and any dimension or reference join must enforce the intended many-to-one or one-to-one relationship. Reconciliation then checks additive totals before and after transformation, so a join that duplicates rows is detected even if a final chart looks plausible. The dashboard follows the same discipline by loading contract-validated products and calculating scoped summaries from a single observed fact rather than summing overlapping report tables. Uniqueness and measure conservation together are stronger than a blanket drop_duplicates operation. The project tests source and monthly keys, SQL joins and the conservation of historical items and NIC.

**Four points to retain**

- I would validate the source business key at its true dimensional grain first, because repeated simpler product-month keys may be legitimate rather than accidental duplicates.
- After monthly aggregation, the fact key must be unique, and any dimension or reference join must enforce the intended many-to-one or one-to-one relationship.
- Reconciliation then checks additive totals before and after transformation, so a join that duplicates rows is detected even if a final chart looks plausible.
- The dashboard follows the same discipline by loading contract-validated products and calculating scoped summaries from a single observed fact rather than summing overlapping report tables.

**Technical explanation:** Uniqueness and measure conservation together are stronger than a blanket drop_duplicates operation.

**Project-specific example:** The project tests source and monthly keys, SQL joins and the conservation of historical items and NIC.

**Likely follow-up:** How would you diagnose a many-to-many join?

**Common mistake to avoid:** Using DISTINCT after a faulty join to conceal duplicated measures.

## 19. How are calendar month changes calculated correctly?
Category: SQL and database design

**Spoken answer**

A row-based lag on an incomplete series can compare March with January and wrongly label the difference as a monthly change when February is absent. The reporting model uses explicit calendar relationships so that a previous-month comparison refers to the adjacent month rather than merely the previous observed row. If a required month or denominator is missing, the growth result should remain unavailable or carry an explanatory status instead of receiving a convenient zero. The same reasoning applies to annual comparisons: the project distinguishes complete aggregate years from partial selected windows, so a filter cannot silently change the meaning of annual growth. Time adjacency is a calendar condition, not just a row-order condition. The executive page withholds annual growth when the selected window does not contain both complete comparison years.

**Four points to retain**

- A row-based lag on an incomplete series can compare March with January and wrongly label the difference as a monthly change when February is absent.
- The reporting model uses explicit calendar relationships so that a previous-month comparison refers to the adjacent month rather than merely the previous observed row.
- If a required month or denominator is missing, the growth result should remain unavailable or carry an explanatory status instead of receiving a convenient zero.
- The same reasoning applies to annual comparisons: the project distinguishes complete aggregate years from partial selected windows, so a filter cannot silently change the meaning of annual growth.

**Technical explanation:** Time adjacency is a calendar condition, not just a row-order condition.

**Project-specific example:** The executive page withholds annual growth when the selected window does not contain both complete comparison years.

**Likely follow-up:** What would a missing-February fixture test assert?

**Common mistake to avoid:** Applying LAG to observed rows and calling every difference month-on-month.

## 20. Why use a ratio of sums for NIC per item?
Category: SQL and database design

**Spoken answer**

A row with a small number of items should not have the same influence on an overall per-item amount as a row contributing a large volume. Summing NIC and dividing by summed items produces the quantity-weighted accounting ratio for the displayed scope, which reconciles back to its additive inputs. An unweighted average of row ratios answers a different question and can change substantially when the data is split into more rows or grouped differently. I would make the denominator explicit and leave the result unavailable when aggregate items are not positive, rather than returning zero or an arbitrary replacement. Weighted NIC/item = Σ NIC / Σ items; equivalent row-ratio weights are items_i / Σ items. The executive, regional and presentation KPI calculations all use the aggregate ratio for their active filters.

**Four points to retain**

- A row with a small number of items should not have the same influence on an overall per-item amount as a row contributing a large volume.
- Summing NIC and dividing by summed items produces the quantity-weighted accounting ratio for the displayed scope, which reconciles back to its additive inputs.
- An unweighted average of row ratios answers a different question and can change substantially when the data is split into more rows or grouped differently.
- I would make the denominator explicit and leave the result unavailable when aggregate items are not positive, rather than returning zero or an arbitrary replacement.

**Technical explanation:** Weighted NIC/item = Σ NIC / Σ items; equivalent row-ratio weights are items_i / Σ items.

**Project-specific example:** The executive, regional and presentation KPI calculations all use the aggregate ratio for their active filters.

**Likely follow-up:** When would an unweighted average be meaningful?

**Common mistake to avoid:** Averaging regional or presentation unit ratios to calculate the national ratio.

## 21. How are contribution shares scoped?
Category: SQL and database design

**Spoken answer**

A share is meaningful only relative to a specified denominator, so both its period and entity population need to be visible when users filter a report. Regional contribution uses all reported regions in the selected year, even if the display shows a smaller region subset; otherwise selecting one region would misleadingly create a 100% share. Presentation shares use all presentations within the selected regions and year, while the displayed numerator follows the selected presentation choices. I would test those distinct scopes and label them beside the view, because a technically correct percentage can still communicate the wrong business meaning if its denominator is hidden. Numerator filters and denominator filters need not be identical, but their difference must be intentional and disclosed. The regional page explicitly captions the all-region denominator and downloads the same filtered summary it displays.

**Four points to retain**

- A share is meaningful only relative to a specified denominator, so both its period and entity population need to be visible when users filter a report.
- Regional contribution uses all reported regions in the selected year, even if the display shows a smaller region subset; otherwise selecting one region would misleadingly create a 100% share.
- Presentation shares use all presentations within the selected regions and year, while the displayed numerator follows the selected presentation choices.
- I would test those distinct scopes and label them beside the view, because a technically correct percentage can still communicate the wrong business meaning if its denominator is hidden.

**Technical explanation:** Numerator filters and denominator filters need not be identical, but their difference must be intentional and disclosed.

**Project-specific example:** The regional page explicitly captions the all-region denominator and downloads the same filtered summary it displays.

**Likely follow-up:** Should shares sum to 100% after selecting a subset?

**Common mistake to avoid:** Recomputing every filtered subset share as if it were the full observed market.

## 22. Why export reporting marts to Parquet?
Category: SQL and database design

**Spoken answer**

Parquet preserves column types and supports efficient local reads, making it suitable for a dashboard that needs stable reporting products rather than repeatedly rebuilding analytical queries. The export creates a clear boundary between validated analysis and presentation, so dashboard interaction cannot accidentally retrain models or alter the historical SQL database. A manifest records schema, business keys, row counts and content hashes; the loader rejects critical mismatches and returns copies of cached frames to prevent shared mutation. CSV remains useful for human downloads, but runtime calculations use typed validated data so that dates, identifiers and missing values do not rely on implicit text parsing. The dashboard manifest is a versioned runtime data contract, not a license to accept arbitrary files with matching names. All registered Phase 6 datasets are checked against their Parquet hashes before being used by page calculations.

**Four points to retain**

- Parquet preserves column types and supports efficient local reads, making it suitable for a dashboard that needs stable reporting products rather than repeatedly rebuilding analytical queries.
- The export creates a clear boundary between validated analysis and presentation, so dashboard interaction cannot accidentally retrain models or alter the historical SQL database.
- A manifest records schema, business keys, row counts and content hashes; the loader rejects critical mismatches and returns copies of cached frames to prevent shared mutation.
- CSV remains useful for human downloads, but runtime calculations use typed validated data so that dates, identifiers and missing values do not rely on implicit text parsing.

**Technical explanation:** The dashboard manifest is a versioned runtime data contract, not a license to accept arbitrary files with matching names.

**Project-specific example:** All registered Phase 6 datasets are checked against their Parquet hashes before being used by page calculations.

**Likely follow-up:** How do you handle a new validated data release?

**Common mistake to avoid:** Regenerating the manifest solely to make a corrupted file pass.

## 23. Why use HAC standard errors for a trend?
Category: Statistics

**Spoken answer**

Monthly residuals may be correlated, making independent-error standard errors too optimistic. HAC changes uncertainty around the fitted trend, rather than changing the least-squares coefficient itself. A short series limits the reliability of either conventional or robust uncertainty estimates. I would inspect residual dependence and report sensitivity, rather than treat a small p-value as proof of a useful business effect. Newey–West covariance combines lagged residual products with decreasing weights. Lag three is a stated analysis setting here, not a universally optimal setting or a correction for omitted-variable bias. The national trend report uses HAC with three lags alongside magnitude and descriptive plots. It does not establish what caused prescribing activity to change.

**Four points to retain**

- Monthly residuals may be correlated, making independent-error standard errors too optimistic.
- HAC changes uncertainty around the fitted trend, rather than changing the least-squares coefficient itself.
- A short series limits the reliability of either conventional or robust uncertainty estimates.
- I would inspect residual dependence and report sensitivity, rather than treat a small p-value as proof of a useful business effect.

**Technical explanation:** Newey–West covariance combines lagged residual products with decreasing weights. Lag three is a stated analysis setting here, not a universally optimal setting or a correction for omitted-variable bias.

**Project-specific example:** The national trend report uses HAC with three lags alongside magnitude and descriptive plots. It does not establish what caused prescribing activity to change.

**Likely follow-up:** How would you choose the lag with more history?

**Common mistake to avoid:** Claiming HAC fixes every model assumption.

## 24. Why combine Theil–Sen and Kendall with regression?
Category: Statistics

**Spoken answer**

Theil–Sen summarizes a median pairwise slope and is less sensitive to isolated extreme months. Kendall assesses monotonic ordering without assuming a linear change of equal size each month. Least squares provides a complementary magnitude estimate with an explicit fitted form. Agreement strengthens a descriptive interpretation, while disagreement prompts investigation of shape, outliers and sensitivity rather than a vote among methods. The methods answer different questions: robust slope, monotonic association and linear mean trend. Serial dependence still matters, and rank-based methods are not automatically valid causal tests. Phase 3 records multiple trend summaries for the same monthly activity series. They are cross-checks on historical direction, not extra independent observations or training labels.

**Four points to retain**

- Theil–Sen summarizes a median pairwise slope and is less sensitive to isolated extreme months.
- Kendall assesses monotonic ordering without assuming a linear change of equal size each month.
- Least squares provides a complementary magnitude estimate with an explicit fitted form.
- Agreement strengthens a descriptive interpretation, while disagreement prompts investigation of shape, outliers and sensitivity rather than a vote among methods.

**Technical explanation:** The methods answer different questions: robust slope, monotonic association and linear mean trend. Serial dependence still matters, and rank-based methods are not automatically valid causal tests.

**Project-specific example:** Phase 3 records multiple trend summaries for the same monthly activity series. They are cross-checks on historical direction, not extra independent observations or training labels.

**Likely follow-up:** What would disagreement tell you?

**Common mistake to avoid:** Counting three methods as three independent confirmations.

## 25. Can three years establish stable seasonality?
Category: Statistics

**Spoken answer**

Thirty-six months supply only three annual repetitions, which is weak support for stable seasonal behavior. A visible month pattern may reflect trend, changing presentation mix or reporting effects. I would examine detrended patterns and their consistency across years before assigning a business mechanism. More history and prospective checks would be needed before relying on the pattern in an operational planning system. Annual seasonality has period twelve in monthly data, so the effective number of observed cycles is small even though there are thirty-six individual monthly rows. The portfolio describes seasonality cautiously and retains a parsimonious nonseasonal ETS selection. A seasonal-naive model remains a useful benchmark rather than a guaranteed better model.

**Four points to retain**

- Thirty-six months supply only three annual repetitions, which is weak support for stable seasonal behavior.
- A visible month pattern may reflect trend, changing presentation mix or reporting effects.
- I would examine detrended patterns and their consistency across years before assigning a business mechanism.
- More history and prospective checks would be needed before relying on the pattern in an operational planning system.

**Technical explanation:** Annual seasonality has period twelve in monthly data, so the effective number of observed cycles is small even though there are thirty-six individual monthly rows.

**Project-specific example:** The portfolio describes seasonality cautiously and retains a parsimonious nonseasonal ETS selection. A seasonal-naive model remains a useful benchmark rather than a guaranteed better model.

**Likely follow-up:** What additional history would change your confidence?

**Common mistake to avoid:** Calling a decomposition plot proof of persistent annual seasonality.

## 26. What does weak lag-twelve autocorrelation imply?
Category: Statistics

**Spoken answer**

A weak lag-twelve correlation means limited evidence of a repeated annual relationship in that specific transformed series. It does not prove there is no seasonality, because trend removal, noise and the small sample affect the estimate. I would compare neighboring lags, year profiles and benchmark forecast performance rather than use a single coefficient as a model-selection rule. The practical question is whether a seasonal specification improves honest out-of-sample performance at the required horizon. Sample autocorrelation estimates a lagged linear relationship; its uncertainty grows when few lagged pairs are available. ACF interpretation also depends on whether the series is stationary or detrended. The project retains seasonal-naive results in model comparison while explicitly reporting limited annual-cycle evidence. The frozen choice is not changed after inspecting later targets.

**Four points to retain**

- A weak lag-twelve correlation means limited evidence of a repeated annual relationship in that specific transformed series.
- It does not prove there is no seasonality, because trend removal, noise and the small sample affect the estimate.
- I would compare neighboring lags, year profiles and benchmark forecast performance rather than use a single coefficient as a model-selection rule.
- The practical question is whether a seasonal specification improves honest out-of-sample performance at the required horizon.

**Technical explanation:** Sample autocorrelation estimates a lagged linear relationship; its uncertainty grows when few lagged pairs are available. ACF interpretation also depends on whether the series is stationary or detrended.

**Project-specific example:** The project retains seasonal-naive results in model comparison while explicitly reporting limited annual-cycle evidence. The frozen choice is not changed after inspecting later targets.

**Likely follow-up:** Would a seasonal model still be worth testing?

**Common mistake to avoid:** Treating one ACF bar as definitive evidence for or against seasonality.

## 27. What is STL useful for here?
Category: Statistics

**Spoken answer**

STL separates a historical series into smooth trend, seasonal and remainder components for exploration. That helps locate unusual months and explain what pattern a forecasting specification might need to represent. The decomposition is dependent on smoothing settings and the limited history, so its components are estimates rather than observed causes. A full-history decomposition is retrospective and must not be silently reused as a feature available at earlier forecast origins. STL uses local smoothing with a specified seasonal period. A component fitted with future observations can leak information when used in backtests unless recomputed using only origin-available history. Phase 3 STL supports exploratory review. Phase 4 uses its own origin-constrained training procedure instead of importing the retrospective decomposition into forecast features.

**Four points to retain**

- STL separates a historical series into smooth trend, seasonal and remainder components for exploration.
- That helps locate unusual months and explain what pattern a forecasting specification might need to represent.
- The decomposition is dependent on smoothing settings and the limited history, so its components are estimates rather than observed causes.
- A full-history decomposition is retrospective and must not be silently reused as a feature available at earlier forecast origins.

**Technical explanation:** STL uses local smoothing with a specified seasonal period. A component fitted with future observations can leak information when used in backtests unless recomputed using only origin-available history.

**Project-specific example:** Phase 3 STL supports exploratory review. Phase 4 uses its own origin-constrained training procedure instead of importing the retrospective decomposition into forecast features.

**Likely follow-up:** How would you safely use decomposition in a forecast?

**Common mistake to avoid:** Using a full-series trend component as if it existed in the past.

## 28. Why can month-on-month growth be misleading?
Category: Statistics

**Spoken answer**

A large percentage increase can arise from a small previous-month denominator rather than a large absolute activity change. Month length, recurring calendar effects and missing prior observations also complicate comparisons. I would show absolute change beside the percentage and require the immediately preceding calendar month to exist. For executive interpretation, same-month annual comparisons and longer aggregates can provide additional context without replacing the underlying monthly evidence. Growth is one hundred times current divided by previous minus one, with an undefined result when the prior denominator is zero or unavailable. Row adjacency alone does not ensure calendar adjacency. The analysis preserves absent region-presentation months and uses calendar-aware comparisons. It does not skip an absent month and label the next observed-row change as monthly growth.

**Four points to retain**

- A large percentage increase can arise from a small previous-month denominator rather than a large absolute activity change.
- Month length, recurring calendar effects and missing prior observations also complicate comparisons.
- I would show absolute change beside the percentage and require the immediately preceding calendar month to exist.
- For executive interpretation, same-month annual comparisons and longer aggregates can provide additional context without replacing the underlying monthly evidence.

**Technical explanation:** Growth is one hundred times current divided by previous minus one, with an undefined result when the prior denominator is zero or unavailable. Row adjacency alone does not ensure calendar adjacency.

**Project-specific example:** The analysis preserves absent region-presentation months and uses calendar-aware comparisons. It does not skip an absent month and label the next observed-row change as monthly growth.

**Likely follow-up:** Would you replace an undefined growth value with zero?

**Common mistake to avoid:** Reading a large percentage without checking its baseline.

## 29. How do you handle outliers without deleting important months?
Category: Statistics

**Spoken answer**

An unusual month is initially a review flag, not evidence that the source is wrong. Robust summaries can identify extremes while preserving the raw receipt and transformed record for investigation. I would inspect source completeness, category coverage and the effect of the month on conclusions before considering any correction. Any correction would need an explicit reason, retained provenance and a sensitivity comparison against the unmodified series. Median absolute deviation reduces the influence of extremes on the reference spread, but a robust anomaly score does not distinguish a data error from a genuine historical event. The Phase 3 anomaly outputs identify review candidates. Their retrospective flags are not silently converted into deleted observations or future-aware training features.

**Four points to retain**

- An unusual month is initially a review flag, not evidence that the source is wrong.
- Robust summaries can identify extremes while preserving the raw receipt and transformed record for investigation.
- I would inspect source completeness, category coverage and the effect of the month on conclusions before considering any correction.
- Any correction would need an explicit reason, retained provenance and a sensitivity comparison against the unmodified series.

**Technical explanation:** Median absolute deviation reduces the influence of extremes on the reference spread, but a robust anomaly score does not distinguish a data error from a genuine historical event.

**Project-specific example:** The Phase 3 anomaly outputs identify review candidates. Their retrospective flags are not silently converted into deleted observations or future-aware training features.

**Likely follow-up:** What evidence would justify correcting an observation?

**Common mistake to avoid:** Automatically removing all statistically unusual months.

## 30. Does the exact cost decomposition establish causality?
Category: Statistics

**Spoken answer**

It explains an accounting change through volume, presentation shares and within-presentation NIC-per-item ratios. A symmetric decomposition distributes interaction terms so the three contributions sum exactly to the observed difference. Those contributions describe the identity, not interventions or mechanisms such as negotiation, substitution or patent expiry. I would use them to prioritize questions for additional evidence rather than report a causal saving or claim a particular business action worked. For cost V times the sum of share times unit ratio, averaging all factor-change orderings allocates interactions without depending on one arbitrary sequence. Exact reconciliation is an algebraic property. The verified 2025 change has positive volume and mix contributions and a larger negative within-presentation contribution. This accounts for the NIC decline without identifying its cause.

**Four points to retain**

- It explains an accounting change through volume, presentation shares and within-presentation NIC-per-item ratios.
- A symmetric decomposition distributes interaction terms so the three contributions sum exactly to the observed difference.
- Those contributions describe the identity, not interventions or mechanisms such as negotiation, substitution or patent expiry.
- I would use them to prioritize questions for additional evidence rather than report a causal saving or claim a particular business action worked.

**Technical explanation:** For cost V times the sum of share times unit ratio, averaging all factor-change orderings allocates interactions without depending on one arbitrary sequence. Exact reconciliation is an algebraic property.

**Project-specific example:** The verified 2025 change has positive volume and mix contributions and a larger negative within-presentation contribution. This accounts for the NIC decline without identifying its cause.

**Likely follow-up:** What design would be needed to estimate a causal price effect?

**Common mistake to avoid:** Interpreting an exact accounting contribution as an experimentally identified effect.

## 31. Why use rolling-origin evaluation?
Category: Forecasting

**Spoken answer**

Random splitting breaks time order and can put later observations into training for earlier targets. Rolling origins repeatedly train on available history and predict the next required horizons. This approximates the information boundary of a historical forecasting decision, although source release timing remains a separate limitation. I would report both overall metrics and the number of valid origins at each horizon so the strength of the evidence is visible. Each prediction carries a series identifier, forecast origin, horizon and target date. Training ends at the origin, and evaluation joins predictions to the corresponding later actuals. The holdout has July–December 2025 targets, with six, five and four valid origin cells at horizons one, two and three. Those cells are overlapping evaluations.

**Four points to retain**

- Random splitting breaks time order and can put later observations into training for earlier targets.
- Rolling origins repeatedly train on available history and predict the next required horizons.
- This approximates the information boundary of a historical forecasting decision, although source release timing remains a separate limitation.
- I would report both overall metrics and the number of valid origins at each horizon so the strength of the evidence is visible.

**Technical explanation:** Each prediction carries a series identifier, forecast origin, horizon and target date. Training ends at the origin, and evaluation joins predictions to the corresponding later actuals.

**Project-specific example:** The holdout has July–December 2025 targets, with six, five and four valid origin cells at horizons one, two and three. Those cells are overlapping evaluations.

**Likely follow-up:** How is this different from a single train-test split?

**Common mistake to avoid:** Shuffling monthly rows before splitting a time series.

## 32. How did you prevent forecast leakage?
Category: Forecasting

**Spoken answer**

Training inputs and feature construction are limited to the history available at each recorded origin. Hyperparameter and model selection are fixed using the development period before evaluating later holdout targets. Scaling denominators and any normalization must also be computed from training history rather than the complete series. The audit checks dates and frozen configuration explicitly because a good metric alone cannot demonstrate an honest information boundary. Leakage can enter through targets, future transformations, revised source vintages or repeated model selection. Origin-constrained calculations prevent some forms, while publication-vintage limitations must still be disclosed. The independent Phase 7 checker reconstructs MASE scales from origin-only observations and checks target alignment. The frozen June 2025 selection is preserved even when a later comparator scores lower.

**Four points to retain**

- Training inputs and feature construction are limited to the history available at each recorded origin.
- Hyperparameter and model selection are fixed using the development period before evaluating later holdout targets.
- Scaling denominators and any normalization must also be computed from training history rather than the complete series.
- The audit checks dates and frozen configuration explicitly because a good metric alone cannot demonstrate an honest information boundary.

**Technical explanation:** Leakage can enter through targets, future transformations, revised source vintages or repeated model selection. Origin-constrained calculations prevent some forms, while publication-vintage limitations must still be disclosed.

**Project-specific example:** The independent Phase 7 checker reconstructs MASE scales from origin-only observations and checks target alignment. The frozen June 2025 selection is preserved even when a later comparator scores lower.

**Likely follow-up:** Does this prove a real-time source-vintage backtest?

**Common mistake to avoid:** Claiming that chronological splitting alone eliminates all leakage.

## 33. Why retain a naive benchmark?
Category: Forecasting

**Spoken answer**

A simple last-observation forecast establishes whether added model complexity produces useful improvement. It is easy to explain, inexpensive to run and often competitive for noisy short series. A seasonal-naive comparator tests whether copying the same month of the prior year adds value. I would compare models on common eligible origin-target cells so different coverage does not create an artificial advantage. A naive model predicts the most recent observed level. Benchmark comparison requires the same target, horizon, eligibility rules and error denominator as the candidate model. National ETS holdout MASE is about 0.888 against about 1.107 for naive on common support, an improvement of roughly 19.75 percent by that metric, not an impact estimate.

**Four points to retain**

- A simple last-observation forecast establishes whether added model complexity produces useful improvement.
- It is easy to explain, inexpensive to run and often competitive for noisy short series.
- A seasonal-naive comparator tests whether copying the same month of the prior year adds value.
- I would compare models on common eligible origin-target cells so different coverage does not create an artificial advantage.

**Technical explanation:** A naive model predicts the most recent observed level. Benchmark comparison requires the same target, horizon, eligibility rules and error denominator as the candidate model.

**Project-specific example:** National ETS holdout MASE is about 0.888 against about 1.107 for naive on common support, an improvement of roughly 19.75 percent by that metric, not an impact estimate.

**Likely follow-up:** What if the benchmark wins?

**Common mistake to avoid:** Comparing candidate and benchmark metrics from different sets of target cells.

## 34. Why keep ETS when Ridge has a lower holdout MASE?
Category: Forecasting

**Spoken answer**

The model choice was frozen using development evidence, which preserves a clean evaluation boundary. The later Ridge result is reported transparently as a comparator rather than used to retrospectively replace the chosen model. Reselecting after seeing holdout outcomes would turn evaluation evidence into additional tuning data. A future update could define a new selection procedure and validate on new observations, while retaining the original result as the historical portfolio record. Model selection and final evaluation have different roles. Choosing the minimum holdout metric after comparison introduces selection bias and makes that same holdout unsuitable for an untouched final assessment. National Ridge holdout MASE is about 0.872, below ETS at about 0.888. The dashboard still identifies the frozen national ETS selection and shows comparator performance honestly.

**Four points to retain**

- The model choice was frozen using development evidence, which preserves a clean evaluation boundary.
- The later Ridge result is reported transparently as a comparator rather than used to retrospectively replace the chosen model.
- Reselecting after seeing holdout outcomes would turn evaluation evidence into additional tuning data.
- A future update could define a new selection procedure and validate on new observations, while retaining the original result as the historical portfolio record.

**Technical explanation:** Model selection and final evaluation have different roles. Choosing the minimum holdout metric after comparison introduces selection bias and makes that same holdout unsuitable for an untouched final assessment.

**Project-specific example:** National Ridge holdout MASE is about 0.872, below ETS at about 0.888. The dashboard still identifies the frozen national ETS selection and shows comparator performance honestly.

**Likely follow-up:** How would you legitimately change the operational model?

**Common mistake to avoid:** Claiming ETS is the best holdout model when the comparator table says otherwise.

## 35. How is MASE computed and interpreted?
Category: Forecasting

**Spoken answer**

MASE scales absolute forecast error by a historical naive-error scale from the training observations. This makes error comparisons less dependent on the raw size of a region or presentation series. The scale must use only origin-available history, and a zero or unavailable scale makes the metric undefined. A value below one is relative to that scaling baseline; it does not automatically prove superiority to every holdout benchmark. The denominator is the mean absolute adjacent-period difference in the training series for the stated nonseasonal scaling. Each origin can have a different denominator, so pooled calculations must preserve origin-level scaling. The independent audit reconstructs the training scale for each stored forecast cell. It separately compares national ETS with the evaluated naive forecast rather than treating MASE below one as that comparison.

**Four points to retain**

- MASE scales absolute forecast error by a historical naive-error scale from the training observations.
- This makes error comparisons less dependent on the raw size of a region or presentation series.
- The scale must use only origin-available history, and a zero or unavailable scale makes the metric undefined.
- A value below one is relative to that scaling baseline; it does not automatically prove superiority to every holdout benchmark.

**Technical explanation:** The denominator is the mean absolute adjacent-period difference in the training series for the stated nonseasonal scaling. Each origin can have a different denominator, so pooled calculations must preserve origin-level scaling.

**Project-specific example:** The independent audit reconstructs the training scale for each stored forecast cell. It separately compares national ETS with the evaluated naive forecast rather than treating MASE below one as that comparison.

**Likely follow-up:** Why can naive holdout MASE differ from one?

**Common mistake to avoid:** Using the full series, including holdout actuals, to compute the scale.

## 36. Why report WAPE rather than rely on MAPE?
Category: Forecasting

**Spoken answer**

MAPE can become undefined or disproportionately large when individual actual observations are zero or very small. WAPE divides aggregate absolute error by aggregate actual activity on the same evaluation support. That gives an interpretable volume-weighted relative error, although large series and months dominate the result. I would retain absolute errors and scaled metrics beside it, since no single measure captures all planning concerns. WAPE is one hundred times the sum of absolute errors divided by the sum of absolute actuals. It is not the unweighted mean of row-level absolute percentage errors. The national ETS holdout WAPE is about 3.684 percent. The audit recomputes its numerator and denominator directly from common-support cells, preserving undefined zero-denominator cases.

**Four points to retain**

- MAPE can become undefined or disproportionately large when individual actual observations are zero or very small.
- WAPE divides aggregate absolute error by aggregate actual activity on the same evaluation support.
- That gives an interpretable volume-weighted relative error, although large series and months dominate the result.
- I would retain absolute errors and scaled metrics beside it, since no single measure captures all planning concerns.

**Technical explanation:** WAPE is one hundred times the sum of absolute errors divided by the sum of absolute actuals. It is not the unweighted mean of row-level absolute percentage errors.

**Project-specific example:** The national ETS holdout WAPE is about 3.684 percent. The audit recomputes its numerator and denominator directly from common-support cells, preserving undefined zero-denominator cases.

**Likely follow-up:** When could aggregate WAPE hide a weak small series?

**Common mistake to avoid:** Averaging percentages and labeling the result WAPE.

## 37. Why are there no prediction intervals?
Category: Forecasting

**Spoken answer**

The implemented residual-calibration procedure requires at least twenty suitable development residuals per horizon. Development calibration provides only six, five and four residuals at the three horizons, below that stated threshold; holdout is never used to calibrate. Reporting a numeric interval anyway would suggest calibrated uncertainty that the evidence does not support. The interface therefore exposes unavailable intervals and manual-review limits rather than replacing them with zero-width or invented bounds. A prediction interval needs a justified uncertainty procedure and enough relevant calibration evidence. The project threshold belongs to its implemented method and is not a universal impossibility result for every forecasting approach. All operational interval fields remain unavailable under the documented rule. The lack of intervals is explicitly discussed in the forecasting defense and dashboard reliability explanations.

**Four points to retain**

- The implemented residual-calibration procedure requires at least twenty suitable development residuals per horizon.
- Development calibration provides only six, five and four residuals at the three horizons, below that stated threshold; holdout is never used to calibrate.
- Reporting a numeric interval anyway would suggest calibrated uncertainty that the evidence does not support.
- The interface therefore exposes unavailable intervals and manual-review limits rather than replacing them with zero-width or invented bounds.

**Technical explanation:** A prediction interval needs a justified uncertainty procedure and enough relevant calibration evidence. The project threshold belongs to its implemented method and is not a universal impossibility result for every forecasting approach.

**Project-specific example:** All operational interval fields remain unavailable under the documented rule. The lack of intervals is explicitly discussed in the forecasting defense and dashboard reliability explanations.

**Likely follow-up:** Could a parametric interval be explored as a separate method?

**Common mistake to avoid:** Inventing bounds or saying no interval method could ever work with this history.

## 38. Are the holdout forecast errors independent?
Category: Forecasting

**Spoken answer**

They are not safely treated as independent because origins and horizons share training observations and some targets. Six months of holdout targets create only a small evidence window even though there are fifteen forecast cells per series. I would report horizon counts and avoid precise confidence claims based on counting every cell as a new independent sample. A longer prospective evaluation could support more stable comparisons and better uncertainty calibration. Overlapping multi-horizon forecasts induce dependence among errors. Effective information is smaller than the raw number of cells, especially with repeated targets and expanding training windows. For thirty-six eligible series, the project stores fifteen holdout cells each across horizons one to three. That does not become fifteen independent future months per series.

**Four points to retain**

- They are not safely treated as independent because origins and horizons share training observations and some targets.
- Six months of holdout targets create only a small evidence window even though there are fifteen forecast cells per series.
- I would report horizon counts and avoid precise confidence claims based on counting every cell as a new independent sample.
- A longer prospective evaluation could support more stable comparisons and better uncertainty calibration.

**Technical explanation:** Overlapping multi-horizon forecasts induce dependence among errors. Effective information is smaller than the raw number of cells, especially with repeated targets and expanding training windows.

**Project-specific example:** For thirty-six eligible series, the project stores fifteen holdout cells each across horizons one to three. That does not become fifteen independent future months per series.

**Likely follow-up:** How would you assess uncertainty in model comparisons?

**Common mistake to avoid:** Presenting overlapping forecast cells as independent replications.

## 39. Why do national and regional forecasts not necessarily sum?
Category: Forecasting

**Spoken answer**

Observed regional totals reconcile to the national total because they describe the same historical accounting scope. Forecasts are fitted independently at each level and therefore need not satisfy that identity automatically. The portfolio reports coherence gaps as a diagnostic instead of silently changing forecasts after evaluation. A future hierarchy-reconciliation method would need a stated procedure, error assumptions and its own out-of-sample assessment. Independent model fitting is not equivalent to coherent hierarchical forecasting. Bottom-up or reconciliation methods can enforce sums, but those are additional modeling choices with accuracy tradeoffs. The saved national, seven regional and twenty-eight region-presentation series are separate forecast products. The dashboard shows observed reconciliation separately from forecast coherence diagnostics.

**Four points to retain**

- Observed regional totals reconcile to the national total because they describe the same historical accounting scope.
- Forecasts are fitted independently at each level and therefore need not satisfy that identity automatically.
- The portfolio reports coherence gaps as a diagnostic instead of silently changing forecasts after evaluation.
- A future hierarchy-reconciliation method would need a stated procedure, error assumptions and its own out-of-sample assessment.

**Technical explanation:** Independent model fitting is not equivalent to coherent hierarchical forecasting. Bottom-up or reconciliation methods can enforce sums, but those are additional modeling choices with accuracy tradeoffs.

**Project-specific example:** The saved national, seven regional and twenty-eight region-presentation series are separate forecast products. The dashboard shows observed reconciliation separately from forecast coherence diagnostics.

**Likely follow-up:** Would you use bottom-up or MinT with this amount of history?

**Common mistake to avoid:** Assuming historical accounting identities guarantee forecast identities.

## 40. Why forecast only twenty-eight region-presentation series?
Category: Forecasting

**Spoken answer**

Forecasting requires enough valid history under the project eligibility rules, rather than merely an identifier appearing once. Sparse or incomplete combinations can make lag features, estimation and evaluation unreliable. The selected twenty-eight series are therefore a restricted modeling scope within a larger descriptive region-presentation dataset. I would show eligibility reasons and coverage rather than extrapolate the forecast result to every presentation combination. Eligibility is separate from model quality: a series first satisfies the historical support contract, then models are evaluated on eligible forecast cells. Missing activity is not filled with invented zeros to increase eligibility. There are thirty-six modeled series in total: one national, seven regional and twenty-eight region-presentation. The descriptive data include additional combinations outside that forecast scope.

**Four points to retain**

- Forecasting requires enough valid history under the project eligibility rules, rather than merely an identifier appearing once.
- Sparse or incomplete combinations can make lag features, estimation and evaluation unreliable.
- The selected twenty-eight series are therefore a restricted modeling scope within a larger descriptive region-presentation dataset.
- I would show eligibility reasons and coverage rather than extrapolate the forecast result to every presentation combination.

**Technical explanation:** Eligibility is separate from model quality: a series first satisfies the historical support contract, then models are evaluated on eligible forecast cells. Missing activity is not filled with invented zeros to increase eligibility.

**Project-specific example:** There are thirty-six modeled series in total: one national, seven regional and twenty-eight region-presentation. The descriptive data include additional combinations outside that forecast scope.

**Likely follow-up:** How would you forecast intermittent or newly introduced series?

**Common mistake to avoid:** Claiming that twenty-eight modeled combinations cover all observed prescribing combinations.

## 41. How does the direct Ridge model work?
Category: Forecasting

**Spoken answer**

Ridge uses regularized regression to relate recorded historical features to a future target. A direct strategy fits horizon-specific relationships instead of repeatedly feeding one-step predictions back into later steps. Regularization limits coefficient instability when features overlap and the training sample is short. Feature construction and hyperparameter selection must remain inside the development and origin boundaries, with scaling treated consistently. The Ridge penalty shrinks coefficients through an L2 term. Direct multi-horizon models have separate targets for each horizon, which avoids recursive error propagation but reduces the training support available for longer horizons. The frozen region-presentation choice uses Ridge with alpha ten. Its saved configuration and origin-level features are reviewed without refitting or tuning against the later holdout.

**Four points to retain**

- Ridge uses regularized regression to relate recorded historical features to a future target.
- A direct strategy fits horizon-specific relationships instead of repeatedly feeding one-step predictions back into later steps.
- Regularization limits coefficient instability when features overlap and the training sample is short.
- Feature construction and hyperparameter selection must remain inside the development and origin boundaries, with scaling treated consistently.

**Technical explanation:** The Ridge penalty shrinks coefficients through an L2 term. Direct multi-horizon models have separate targets for each horizon, which avoids recursive error propagation but reduces the training support available for longer horizons.

**Project-specific example:** The frozen region-presentation choice uses Ridge with alpha ten. Its saved configuration and origin-level features are reviewed without refitting or tuning against the later holdout.

**Likely follow-up:** Why not choose a more complex boosted model?

**Common mistake to avoid:** Assuming regularization removes the need for honest temporal validation.

## 42. Is the forecast a genuine real-time December 2025 release?
Category: Forecasting

**Spoken answer**

It is a retrospective forecast with a December 2025 observation cutoff, not proof of what data were available on that calendar date. NHSBSA publication delay means observation month and actual release month are different information boundaries. Archived receipts establish what this project downloaded, but do not reconstruct every historical publication or revision vintage. I would require release-aware snapshots before presenting the backtest as a live operational simulation. An as-of backtest needs both event time and information-availability time. Restricting observations to a cutoff does not account for a source that publishes those observations later. The saved January–March 2026 point forecasts use history through December 2025. No 2026 actuals are present, so the project cannot claim observed accuracy for those forecast months.

**Four points to retain**

- It is a retrospective forecast with a December 2025 observation cutoff, not proof of what data were available on that calendar date.
- NHSBSA publication delay means observation month and actual release month are different information boundaries.
- Archived receipts establish what this project downloaded, but do not reconstruct every historical publication or revision vintage.
- I would require release-aware snapshots before presenting the backtest as a live operational simulation.

**Technical explanation:** An as-of backtest needs both event time and information-availability time. Restricting observations to a cutoff does not account for a source that publishes those observations later.

**Project-specific example:** The saved January–March 2026 point forecasts use history through December 2025. No 2026 actuals are present, so the project cannot claim observed accuracy for those forecast months.

**Likely follow-up:** How would you build a publication-vintage evaluation?

**Common mistake to avoid:** Calling retrospective future-dated forecasts contemporaneously issued or already validated.

## 43. What does the five-component priority score mean?
Category: Decision intelligence

**Spoken answer**

It is an illustrative analytical-review score built from activity, change, cost, forecast and quality evidence. Each component is transformed to a comparable percentile scale before the stated weights are applied. The result ranks questions for review within the chosen scope, rather than measuring demand potential, profit or patient benefit. A domain user would need to approve the objectives and weight policy before operational use. The weights are 0.25, 0.20, 0.20, 0.20 and 0.15 and sum to one. A complete weighted score preserves component lineage; missing required evidence remains unscored. The dashboard exposes both the aggregate priority and its contributing evidence, allowing a reviewer to distinguish high activity from a quality concern or forecast-risk contribution.

**Four points to retain**

- It is an illustrative analytical-review score built from activity, change, cost, forecast and quality evidence.
- Each component is transformed to a comparable percentile scale before the stated weights are applied.
- The result ranks questions for review within the chosen scope, rather than measuring demand potential, profit or patient benefit.
- A domain user would need to approve the objectives and weight policy before operational use.

**Technical explanation:** The weights are 0.25, 0.20, 0.20, 0.20 and 0.15 and sum to one. A complete weighted score preserves component lineage; missing required evidence remains unscored.

**Project-specific example:** The dashboard exposes both the aggregate priority and its contributing evidence, allowing a reviewer to distinguish high activity from a quality concern or forecast-risk contribution.

**Likely follow-up:** Who should set the weights?

**Common mistake to avoid:** Presenting an illustrative score as a validated commercial opportunity model.

## 44. How do percentile ranks handle ties?
Category: Decision intelligence

**Spoken answer**

Tied values receive midranks so arbitrary row order does not decide their apparent priority. Percentiles depend on the comparison population and are relative rather than absolute business thresholds. Direction must be defined before ranking, because high activity and poor quality have different analytical meanings. I would show the source measure with its transformed score so reviewers can interpret equal ranks correctly. The independent checker counts values below and equal to each observation to reconstruct the documented midrank transformation. This avoids merely calling the production rank function again. Phase 7 recomputes every stored decision component from pairwise comparisons and reconciles the resulting weighted scores, including tied values and unavailable components. Regional ranks compare seven regions rather than the pooled region-presentation combinations.

**Four points to retain**

- Tied values receive midranks so arbitrary row order does not decide their apparent priority.
- Percentiles depend on the comparison population and are relative rather than absolute business thresholds.
- Direction must be defined before ranking, because high activity and poor quality have different analytical meanings.
- I would show the source measure with its transformed score so reviewers can interpret equal ranks correctly.

**Technical explanation:** The independent checker counts values below and equal to each observation to reconstruct the documented midrank transformation. This avoids merely calling the production rank function again.

**Project-specific example:** Phase 7 recomputes every stored decision component from pairwise comparisons and reconciles the resulting weighted scores, including tied values and unavailable components. Regional ranks compare seven regions rather than the pooled region-presentation combinations.

**Likely follow-up:** How would adding another region affect a percentile?

**Common mistake to avoid:** Treating a percentile score as a stable unit with an absolute business interpretation.

## 45. Why assign fifty to a constant component?
Category: Decision intelligence

**Spoken answer**

A constant component contains no information for distinguishing entities in that comparison scope. The documented neutral value fifty prevents a constant from creating an artificial best or worst entity. It still contributes the same weighted amount to every complete score, so it does not change their relative order by itself. I would state this convention and test sensitivity rather than imply that fifty represents measured medium performance. Percentile transformation of a degenerate distribution needs an explicit convention. Neutral treatment is a policy choice and differs from dropping the component and renormalizing weights. The independent score audit handles constant components explicitly. The quality documentation explains that the fixed weights and constant-component convention are illustrative analysis rules.

**Four points to retain**

- A constant component contains no information for distinguishing entities in that comparison scope.
- The documented neutral value fifty prevents a constant from creating an artificial best or worst entity.
- It still contributes the same weighted amount to every complete score, so it does not change their relative order by itself.
- I would state this convention and test sensitivity rather than imply that fifty represents measured medium performance.

**Technical explanation:** Percentile transformation of a degenerate distribution needs an explicit convention. Neutral treatment is a policy choice and differs from dropping the component and renormalizing weights.

**Project-specific example:** The independent score audit handles constant components explicitly. The quality documentation explains that the fixed weights and constant-component convention are illustrative analysis rules.

**Likely follow-up:** Would you renormalize instead?

**Common mistake to avoid:** Describing neutral fifty as a measured halfway business outcome.

## 46. Why are thirteen presentation priorities unscored?
Category: Decision intelligence

**Spoken answer**

Those rows lack the positive or complete evidence required by the scoring contract. Replacing missing components with zero would conflate unavailable evidence with low priority. Renormalizing over the remaining components would create a different score definition and reduce comparability. The interface therefore exposes an unscored state and lets the analyst inspect the missing-evidence reason. Complete-case scoring requires all specified components and valid required denominators. Null is a meaningful state in the contract, not a numeric score waiting to be filled. Thirteen presentation priorities remain unavailable in the saved outputs. Phase 7 verifies that both the independently computed and stored scores remain null for those rows. A ranking view cannot treat those thirteen rows as lower-ranked scored presentations.

**Four points to retain**

- Those rows lack the positive or complete evidence required by the scoring contract.
- Replacing missing components with zero would conflate unavailable evidence with low priority.
- Renormalizing over the remaining components would create a different score definition and reduce comparability.
- The interface therefore exposes an unscored state and lets the analyst inspect the missing-evidence reason.

**Technical explanation:** Complete-case scoring requires all specified components and valid required denominators. Null is a meaningful state in the contract, not a numeric score waiting to be filled.

**Project-specific example:** Thirteen presentation priorities remain unavailable in the saved outputs. Phase 7 verifies that both the independently computed and stored scores remain null for those rows. A ranking view cannot treat those thirteen rows as lower-ranked scored presentations.

**Likely follow-up:** Could a separate partial-evidence score be useful?

**Common mistake to avoid:** Quietly assigning zero or an apparently precise rank to missing evidence.

## 47. What does regional rank instability tell you?
Category: Decision intelligence

**Spoken answer**

All seven regional rankings are sensitive to the tested weight policies under the stated stability rule. That means the displayed ordering should be treated as conditional on the current scoring policy. It does not mean the underlying prescribing totals are wrong or that the entire analysis is unusable. I would emphasize component-level evidence and stakeholder objectives before turning a ranking into a business recommendation. Sensitivity analysis changes policy assumptions while holding observed inputs fixed. Rank movement measures dependence on that policy, not uncertainty in all underlying data or a probability of being the best region. The regional dashboard identifies the unstable ranking status, and the defense material avoids naming a stable top commercial opportunity from these illustrative scores.

**Four points to retain**

- All seven regional rankings are sensitive to the tested weight policies under the stated stability rule.
- That means the displayed ordering should be treated as conditional on the current scoring policy.
- It does not mean the underlying prescribing totals are wrong or that the entire analysis is unusable.
- I would emphasize component-level evidence and stakeholder objectives before turning a ranking into a business recommendation.

**Technical explanation:** Sensitivity analysis changes policy assumptions while holding observed inputs fixed. Rank movement measures dependence on that policy, not uncertainty in all underlying data or a probability of being the best region.

**Project-specific example:** The regional dashboard identifies the unstable ranking status, and the defense material avoids naming a stable top commercial opportunity from these illustrative scores.

**Likely follow-up:** How could stakeholders use an unstable ranking?

**Common mistake to avoid:** Calling a displayed top rank a robust winner despite the saved sensitivity result.

## 48. How were alternative weight policies evaluated?
Category: Decision intelligence

**Spoken answer**

Each policy is applied to the same component evidence so the comparison isolates the scoring-policy choice. The audit checks that weights and rank movements match the saved sensitivity outputs. Labels such as activity-heavy should describe the actual numerical policy rather than conceal a changed formula. I would preserve the original policy as the portfolio baseline and introduce any future stakeholder policy as a separately versioned configuration. Policy sensitivity is a controlled recalculation of the weighted aggregation, including the same missing-data rules. It is not retraining a prediction model or validating that one policy causes better outcomes. Phase 7 checks the frozen weights and saved rank-stability evidence rather than rewriting the scoring rule to make the rankings look more stable.

**Four points to retain**

- Each policy is applied to the same component evidence so the comparison isolates the scoring-policy choice.
- The audit checks that weights and rank movements match the saved sensitivity outputs.
- Labels such as activity-heavy should describe the actual numerical policy rather than conceal a changed formula.
- I would preserve the original policy as the portfolio baseline and introduce any future stakeholder policy as a separately versioned configuration.

**Technical explanation:** Policy sensitivity is a controlled recalculation of the weighted aggregation, including the same missing-data rules. It is not retraining a prediction model or validating that one policy causes better outcomes.

**Project-specific example:** Phase 7 checks the frozen weights and saved rank-stability evidence rather than rewriting the scoring rule to make the rankings look more stable.

**Likely follow-up:** How would you validate a stakeholder-selected policy?

**Common mistake to avoid:** Relabeling a policy while silently changing its weights or missing-data handling.

## 49. Does forecast risk measure market demand?
Category: Decision intelligence

**Spoken answer**

Forecast-risk evidence describes limitations or errors in a forecast product, not an underlying business opportunity. A large error can indicate model weakness, volatility, incomplete support or a mismatch between model and series. That can justify manual review without establishing that activity will rise or that investment will pay off. I would keep reliability labels beside the forecast and separate them from observed activity and hypothetical commercial assumptions. Prediction reliability is evaluated against observed targets on specified support. It is different from estimating future addressable market size or the causal return to a commercial intervention. Fifteen of the thirty-six modeled series require manual review under saved reliability rules. That status is shown as an evidence limitation rather than an upside opportunity.

**Four points to retain**

- Forecast-risk evidence describes limitations or errors in a forecast product, not an underlying business opportunity.
- A large error can indicate model weakness, volatility, incomplete support or a mismatch between model and series.
- That can justify manual review without establishing that activity will rise or that investment will pay off.
- I would keep reliability labels beside the forecast and separate them from observed activity and hypothetical commercial assumptions.

**Technical explanation:** Prediction reliability is evaluated against observed targets on specified support. It is different from estimating future addressable market size or the causal return to a commercial intervention.

**Project-specific example:** Fifteen of the thirty-six modeled series require manual review under saved reliability rules. That status is shown as an evidence limitation rather than an upside opportunity.

**Likely follow-up:** What action should follow a manual-review flag?

**Common mistake to avoid:** Interpreting model uncertainty or error as latent demand growth.

## 50. How are proposed investigations traceable?
Category: Decision intelligence

**Spoken answer**

A proposed investigation records a rule, entity and supporting source output rather than just a free-form recommendation. This lets the reviewer reproduce why the question was raised and distinguish its evidence class. The item remains a suggested analytical investigation until additional domain evidence and an authorized decision process exist. I would evaluate usefulness with actual analysts before claiming the register improves decisions or produces savings. Traceability links a derived recommendation candidate to input identifiers and a rule version. It supports auditability but does not validate the business effectiveness of the proposed response. The saved register contains 225 proposed investigations and 88 hypotheses. The portfolio presents them as generated review candidates, not executed commercial interventions or delivered client outcomes.

**Four points to retain**

- A proposed investigation records a rule, entity and supporting source output rather than just a free-form recommendation.
- This lets the reviewer reproduce why the question was raised and distinguish its evidence class.
- The item remains a suggested analytical investigation until additional domain evidence and an authorized decision process exist.
- I would evaluate usefulness with actual analysts before claiming the register improves decisions or produces savings.

**Technical explanation:** Traceability links a derived recommendation candidate to input identifiers and a rule version. It supports auditability but does not validate the business effectiveness of the proposed response.

**Project-specific example:** The saved register contains 225 proposed investigations and 88 hypotheses. The portfolio presents them as generated review candidates, not executed commercial interventions or delivered client outcomes.

**Likely follow-up:** How would you assess false positives in the register?

**Common mistake to avoid:** Claiming that generating recommendations means they were adopted or successful.

## 51. Why is the NIC scenario multiplicative?
Category: Scenario simulation

**Spoken answer**

The accounting identity is item count multiplied by average NIC per item. Changing both factors requires multiplying their change factors, which includes their interaction automatically. The result is hypothetical because the inputs are assumptions selected by the user rather than estimated causal responses. I would show the baseline, both assumptions and the resulting amount together so the arithmetic can be checked directly. For volume change v and ratio change c, hypothetical NIC equals baseline NIC times (1+v/100) times (1+c/100). Adding the percentages omits the interaction term. The dashboard sliders use the saved accounting algebra. Phase 7 independently verifies scenarios and tests the real browser values against the corresponding baseline identity.

**Four points to retain**

- The accounting identity is item count multiplied by average NIC per item.
- Changing both factors requires multiplying their change factors, which includes their interaction automatically.
- The result is hypothetical because the inputs are assumptions selected by the user rather than estimated causal responses.
- I would show the baseline, both assumptions and the resulting amount together so the arithmetic can be checked directly.

**Technical explanation:** For volume change v and ratio change c, hypothetical NIC equals baseline NIC times (1+v/100) times (1+c/100). Adding the percentages omits the interaction term.

**Project-specific example:** The dashboard sliders use the saved accounting algebra. Phase 7 independently verifies scenarios and tests the real browser values against the corresponding baseline identity.

**Likely follow-up:** What if item volume and unit ratio are economically dependent?

**Common mistake to avoid:** Treating independently selected sliders as estimated behavioral relationships.

## 52. Why does plus five and minus five not break even?
Category: Scenario simulation

**Spoken answer**

The two changes apply to different multiplicative factors, so equal opposite percentages do not cancel. Multiplying 1.05 by 0.95 gives 0.9975, a quarter-percent decrease in hypothetical NIC. To offset a five-percent item increase exactly, the ratio must fall by about 4.7619 percent. This is an accounting calculation, not a claim that a real-world price or reimbursement change can be achieved. The break-even ratio change is one hundred times the reciprocal of (1+v/100) minus one. The formula requires a positive resulting volume factor. Using the 2025 observed baseline, plus-five volume and minus-five NIC per item produces about £75,783,764.03, while plus-five volume alone produces about £79,772,383.19. The observed baseline remains unchanged when the hypothetical result is exported or recalculated.

**Four points to retain**

- The two changes apply to different multiplicative factors, so equal opposite percentages do not cancel.
- Multiplying 1.05 by 0.95 gives 0.9975, a quarter-percent decrease in hypothetical NIC.
- To offset a five-percent item increase exactly, the ratio must fall by about 4.7619 percent.
- This is an accounting calculation, not a claim that a real-world price or reimbursement change can be achieved.

**Technical explanation:** The break-even ratio change is one hundred times the reciprocal of (1+v/100) minus one. The formula requires a positive resulting volume factor.

**Project-specific example:** Using the 2025 observed baseline, plus-five volume and minus-five NIC per item produces about £75,783,764.03, while plus-five volume alone produces about £79,772,383.19. The observed baseline remains unchanged when the hypothetical result is exported or recalculated.

**Likely follow-up:** What happens near a minus-one-hundred-percent volume change?

**Common mistake to avoid:** Adding percentage changes and reporting exact cancellation.

## 53. Why is the simulator not a causal model?
Category: Scenario simulation

**Spoken answer**

It applies a transparent identity to user-entered assumptions rather than estimating how the world responds to an intervention. There is no experiment, identification strategy or behavioral equation connecting the sliders to patient or market outcomes. The calculations are still useful for understanding sensitivity and checking the implications of explicit assumptions. I would label every result hypothetical and request additional evidence before using it for an actual pricing or volume decision. A deterministic accounting map can be numerically exact while its assumed inputs remain unvalidated. Correct arithmetic is distinct from causal identification or calibrated probabilistic prediction. The scenario page keeps hypothetical evidence separate from observed historical KPIs and model forecasts. Its exports retain baseline context and the selected percentage changes.

**Four points to retain**

- It applies a transparent identity to user-entered assumptions rather than estimating how the world responds to an intervention.
- There is no experiment, identification strategy or behavioral equation connecting the sliders to patient or market outcomes.
- The calculations are still useful for understanding sensitivity and checking the implications of explicit assumptions.
- I would label every result hypothetical and request additional evidence before using it for an actual pricing or volume decision.

**Technical explanation:** A deterministic accounting map can be numerically exact while its assumed inputs remain unvalidated. Correct arithmetic is distinct from causal identification or calibrated probabilistic prediction.

**Project-specific example:** The scenario page keeps hypothetical evidence separate from observed historical KPIs and model forecasts. Its exports retain baseline context and the selected percentage changes.

**Likely follow-up:** What would be needed for an intervention-response model?

**Common mistake to avoid:** Calling the scenario output predicted savings or expected commercial impact.

## 54. How is a presentation-mix transfer constrained?
Category: Scenario simulation

**Spoken answer**

A mix transfer reallocates activity between presentations rather than creating extra total items. The proposed transfer must fit the available source presentation amount and retain nonnegative quantities. Cost changes then follow from the stated presentation ratios under a fixed-ratio assumption. I would check conservation and feasibility before displaying a result, since a plausible-looking chart can otherwise hide impossible allocations. The transfer decreases one presentation and increases another by the same amount. Conservation of total items and nonnegative post-transfer values are separate invariants from the NIC calculation. The independent numerical audit checks item conservation for saved mix scenarios, while the dashboard validates user inputs before invoking the shared scenario engine. This constraint still does not establish that changing between those presentations is clinically appropriate.

**Four points to retain**

- A mix transfer reallocates activity between presentations rather than creating extra total items.
- The proposed transfer must fit the available source presentation amount and retain nonnegative quantities.
- Cost changes then follow from the stated presentation ratios under a fixed-ratio assumption.
- I would check conservation and feasibility before displaying a result, since a plausible-looking chart can otherwise hide impossible allocations.

**Technical explanation:** The transfer decreases one presentation and increases another by the same amount. Conservation of total items and nonnegative post-transfer values are separate invariants from the NIC calculation.

**Project-specific example:** The independent numerical audit checks item conservation for saved mix scenarios, while the dashboard validates user inputs before invoking the shared scenario engine. This constraint still does not establish that changing between those presentations is clinically appropriate.

**Likely follow-up:** Are two presentations clinically interchangeable?

**Common mistake to avoid:** Inferring clinical substitution feasibility from an arithmetic mix transfer.

## 55. What assumption is used when attaching NIC to a volume forecast?
Category: Scenario simulation

**Spoken answer**

A forecast of prescription items does not automatically provide a forecast of ingredient cost. Applying a historical NIC-per-item ratio to forecast volume adds an explicit fixed-ratio assumption. Future presentation mix, reimbursement and within-presentation ratios could change, so that assumption needs separate review. I would keep the original volume forecast and the hypothetical cost translation visibly distinct in charts and exports. Multiplying a model point forecast by an observed historical average is a conditional accounting translation. It is not a separately trained cost model or a joint forecast of volume and unit ratios. The operational forecast uses a December 2025 observation cutoff, while scenario baselines retain their historical scope. No actual January–March 2026 cost outcome validates the hypothetical translation.

**Four points to retain**

- A forecast of prescription items does not automatically provide a forecast of ingredient cost.
- Applying a historical NIC-per-item ratio to forecast volume adds an explicit fixed-ratio assumption.
- Future presentation mix, reimbursement and within-presentation ratios could change, so that assumption needs separate review.
- I would keep the original volume forecast and the hypothetical cost translation visibly distinct in charts and exports.

**Technical explanation:** Multiplying a model point forecast by an observed historical average is a conditional accounting translation. It is not a separately trained cost model or a joint forecast of volume and unit ratios.

**Project-specific example:** The operational forecast uses a December 2025 observation cutoff, while scenario baselines retain their historical scope. No actual January–March 2026 cost outcome validates the hypothetical translation.

**Likely follow-up:** How would you build and evaluate a cost forecast?

**Common mistake to avoid:** Presenting a fixed historical ratio as a modeled future price forecast.

## 56. Why run both AppTest and real browser QA?
Category: Streamlit and software engineering

**Spoken answer**

AppTest verifies rendered values, widget state and exceptions efficiently without relying on screenshot appearance. A real browser checks navigation, viewport behavior, actual downloads and client-side interactions that AppTest cannot fully establish. I would keep those evidence types separate, because a passing simulated page does not prove mobile readability. The final audit records actual screenshots and browser results only when Chrome has executed the corresponding checks. Streamlit testing exercises application execution and widget state, whereas Playwright interacts with the running HTTP application and browser DOM. They cover overlapping but distinct failure modes. Phase 6 included fourteen AppTest checks. Phase 7 adds Chrome runs for six pages at four widths, a filtered CSV download and scenario-slider arithmetic checks.

**Four points to retain**

- AppTest verifies rendered values, widget state and exceptions efficiently without relying on screenshot appearance.
- A real browser checks navigation, viewport behavior, actual downloads and client-side interactions that AppTest cannot fully establish.
- I would keep those evidence types separate, because a passing simulated page does not prove mobile readability.
- The final audit records actual screenshots and browser results only when Chrome has executed the corresponding checks.

**Technical explanation:** Streamlit testing exercises application execution and widget state, whereas Playwright interacts with the running HTTP application and browser DOM. They cover overlapping but distinct failure modes.

**Project-specific example:** Phase 6 included fourteen AppTest checks. Phase 7 adds Chrome runs for six pages at four widths, a filtered CSV download and scenario-slider arithmetic checks.

**Likely follow-up:** What did the browser catch that static tests missed?

**Common mistake to avoid:** Calling a generated mockup or an AppTest result a real browser screenshot.

## 57. How do caching and session isolation coexist?
Category: Streamlit and software engineering

**Spoken answer**

Immutable data reads can be cached to avoid repeating expensive loading work. User-specific filter and scenario choices belong in each session and must not mutate the shared cached dataset. A returned frame should be treated as immutable or copied before any transformation that changes values. I would test two independent sessions with different choices to detect accidental shared state rather than infer isolation from the framework name. Caching keys identify function inputs and implementation, while session state identifies a particular user interaction context. Shared cached mutable objects can still leak changes if application code modifies them. The scenario module returns new derived frames from validated baselines and keeps controls in Streamlit state. Analytical Parquet inputs remain read-only and hash protected.

**Four points to retain**

- Immutable data reads can be cached to avoid repeating expensive loading work.
- User-specific filter and scenario choices belong in each session and must not mutate the shared cached dataset.
- A returned frame should be treated as immutable or copied before any transformation that changes values.
- I would test two independent sessions with different choices to detect accidental shared state rather than infer isolation from the framework name.

**Technical explanation:** Caching keys identify function inputs and implementation, while session state identifies a particular user interaction context. Shared cached mutable objects can still leak changes if application code modifies them.

**Project-specific example:** The scenario module returns new derived frames from validated baselines and keeps controls in Streamlit state. Analytical Parquet inputs remain read-only and hash protected.

**Likely follow-up:** What would you cache if the source updated daily?

**Common mistake to avoid:** Storing a user-modified scenario frame in a global mutable variable.

## 58. How do you prevent stale KPIs and mismatched CSVs?
Category: Streamlit and software engineering

**Spoken answer**

The same validated selection scope should drive displayed totals and exported rows. A control change triggers a rerun, so browser checks must wait for the updated output rather than click during an incomplete transition. Empty selections need an explicit state instead of retaining a previous successful chart. I would reconcile the downloaded file against the active year and entities, not merely confirm that a download button exists. A UI export contract includes filters, row grain, units and aggregation rules. Synchronization matters in browser testing because Streamlit reruns can temporarily expose the preceding render while the new one is computing. The Chrome check selects 2024 on the regional page and sums the downloaded seven-row CSV against that year’s source total after confirming the rerun has settled.

**Four points to retain**

- The same validated selection scope should drive displayed totals and exported rows.
- A control change triggers a rerun, so browser checks must wait for the updated output rather than click during an incomplete transition.
- Empty selections need an explicit state instead of retaining a previous successful chart.
- I would reconcile the downloaded file against the active year and entities, not merely confirm that a download button exists.

**Technical explanation:** A UI export contract includes filters, row grain, units and aggregation rules. Synchronization matters in browser testing because Streamlit reruns can temporarily expose the preceding render while the new one is computing.

**Project-specific example:** The Chrome check selects 2024 on the regional page and sums the downloaded seven-row CSV against that year’s source total after confirming the rerun has settled.

**Likely follow-up:** How would you test a rapid sequence of filter changes?

**Common mistake to avoid:** Calling a successful file download proof that its data match the visible filters.

## 59. What does the clean-environment test prove?
Category: Streamlit and software engineering

**Spoken answer**

It verifies the packaged dashboard starts and renders using a separate checkout and fresh Python environment. That reduces the risk of an undeclared dependency or accidental reference to the developer workspace. It does not prove that the entire acquisition-to-model pipeline was rebuilt, because the runtime uses preserved analytical marts. I would document direct dependencies, the captured transitive lock and the separate full analytical regression evidence. A runtime reproduction and a full source-data regeneration have different contracts. The clean environment disables system site packages and receives only declared application sources and the manifest-listed runtime files. Phase 7 installs the dashboard requirements into an isolated environment and runs entrypoint, six-page rendering, manifest and HTTP smoke checks without retraining the frozen forecasts.

**Four points to retain**

- It verifies the packaged dashboard starts and renders using a separate checkout and fresh Python environment.
- That reduces the risk of an undeclared dependency or accidental reference to the developer workspace.
- It does not prove that the entire acquisition-to-model pipeline was rebuilt, because the runtime uses preserved analytical marts.
- I would document direct dependencies, the captured transitive lock and the separate full analytical regression evidence.

**Technical explanation:** A runtime reproduction and a full source-data regeneration have different contracts. The clean environment disables system site packages and receives only declared application sources and the manifest-listed runtime files.

**Project-specific example:** Phase 7 installs the dashboard requirements into an isolated environment and runs entrypoint, six-page rendering, manifest and HTTP smoke checks without retraining the frozen forecasts.

**Likely follow-up:** Could the lightweight CI job replace full analytical regression?

**Common mistake to avoid:** Describing a dashboard smoke test as a complete clean pipeline rebuild.

## 60. Why validate data contracts at dashboard startup?
Category: Streamlit and software engineering

**Spoken answer**

A dashboard can produce plausible but wrong results if an expected column, grain or artifact is silently missing. Startup contracts check that the required runtime files and their hashes match the declared manifest. Page logic then works against known units and schemas rather than improvising fallbacks that hide missing data. A clear relative-path error helps a user fix packaging while avoiding exposure of developer-specific filesystem locations. A contract joins file presence, schema, unique grain and provenance to the consumer’s assumptions. Failure should stop the affected calculation rather than substitute an empty or zero-filled dataset. The dashboard consumes fifty-two manifest-listed Parquet files. The clean-package test checks those exact files and the lightweight tests exercise duplicate-grain and missing-manifest errors.

**Four points to retain**

- A dashboard can produce plausible but wrong results if an expected column, grain or artifact is silently missing.
- Startup contracts check that the required runtime files and their hashes match the declared manifest.
- Page logic then works against known units and schemas rather than improvising fallbacks that hide missing data.
- A clear relative-path error helps a user fix packaging while avoiding exposure of developer-specific filesystem locations.

**Technical explanation:** A contract joins file presence, schema, unique grain and provenance to the consumer’s assumptions. Failure should stop the affected calculation rather than substitute an empty or zero-filled dataset.

**Project-specific example:** The dashboard consumes fifty-two manifest-listed Parquet files. The clean-package test checks those exact files and the lightweight tests exercise duplicate-grain and missing-manifest errors.

**Likely follow-up:** How would you version a schema change?

**Common mistake to avoid:** Silently swallowing a contract failure and displaying zero activity.

## 61. What are the three biggest limitations and production priorities?
Category: Limitations and defense

**Spoken answer**

The data are public community prescribing proxies, not manufacturer sales or a complete market demand measure. The history and holdout are short, with limited independent evidence and unavailable residual-calibrated intervals. The review weights and scenarios are illustrative policies that have not been validated with real business users. Production priorities are authorized decision-specific data, publication-aware prospective evaluation and user-reviewed governance before adding more modeling complexity. Production readiness requires availability-aware ingestion, monitored contracts, calibrated evaluation and a decision process. Portfolio regression and numerical reconciliation establish technical evidence without establishing operational adoption or business impact. The scorecard separates completed local checks from cloud, remote CI, accessibility review and user validation that were not performed. The project does not claim those gaps are resolved.

**Four points to retain**

- The data are public community prescribing proxies, not manufacturer sales or a complete market demand measure.
- The history and holdout are short, with limited independent evidence and unavailable residual-calibrated intervals.
- The review weights and scenarios are illustrative policies that have not been validated with real business users.
- Production priorities are authorized decision-specific data, publication-aware prospective evaluation and user-reviewed governance before adding more modeling complexity.

**Technical explanation:** Production readiness requires availability-aware ingestion, monitored contracts, calibrated evaluation and a decision process. Portfolio regression and numerical reconciliation establish technical evidence without establishing operational adoption or business impact.

**Project-specific example:** The scorecard separates completed local checks from cloud, remote CI, accessibility review and user validation that were not performed. The project does not claim those gaps are resolved.

**Likely follow-up:** Which priority would you address first for a named business decision?

**Common mistake to avoid:** Listing only cosmetic limitations while claiming production readiness.

## 62. Can these findings transfer to India or another medicine?
Category: Limitations and defense

**Spoken answer**

The architecture and analytical techniques can be reused, but the observed conclusions belong to atorvastatin community prescribing in England. Another country or medicine changes coverage, identifiers, reimbursement definitions, units and decision context. I would establish a new source contract and reconcile its measures before transferring any KPI, score policy or model. The existing results remain a reference implementation rather than evidence of another market’s demand or economics. Transferability of software design differs from transportability of statistical or business conclusions. A new dataset requires harmonization, eligibility review and fresh temporal evaluation under its own publication process. The portfolio uses seven English regions and NHS ingredient-cost definitions. It contains no Indian sales, distributor stock, patient-level records or regional commercial outcomes.

**Four points to retain**

- The architecture and analytical techniques can be reused, but the observed conclusions belong to atorvastatin community prescribing in England.
- Another country or medicine changes coverage, identifiers, reimbursement definitions, units and decision context.
- I would establish a new source contract and reconcile its measures before transferring any KPI, score policy or model.
- The existing results remain a reference implementation rather than evidence of another market’s demand or economics.

**Technical explanation:** Transferability of software design differs from transportability of statistical or business conclusions. A new dataset requires harmonization, eligibility review and fresh temporal evaluation under its own publication process.

**Project-specific example:** The portfolio uses seven English regions and NHS ingredient-cost definitions. It contains no Indian sales, distributor stock, patient-level records or regional commercial outcomes.

**Likely follow-up:** What would you request for an Indian pharmaceutical distributor?

**Common mistake to avoid:** Reusing English prescribing ratios as measured Indian market economics.

## 63. How should you explain AI assistance honestly?
Category: Limitations and defense

**Spoken answer**

I would say that Codex generated and executed substantial implementation, testing and documentation work in this project. My interview claims should identify the parts I personally reviewed, understood or changed rather than imply sole manual authorship. I would explain a specific calculation, its assumptions and its validation evidence to demonstrate ownership of understanding. Any unfamiliar implementation detail should be reviewed before the interview instead of being defended through memorized AI-generated wording. Attribution and competence are separate: disclosing assistance does not replace understanding, while passing tests does not establish that the interview candidate personally wrote every line. The README and demo include an AI-assistance disclosure. This question bank is explicitly practice material and avoids invented stories about client work or personal debugging experience.

**Four points to retain**

- I would say that Codex generated and executed substantial implementation, testing and documentation work in this project.
- My interview claims should identify the parts I personally reviewed, understood or changed rather than imply sole manual authorship.
- I would explain a specific calculation, its assumptions and its validation evidence to demonstrate ownership of understanding.
- Any unfamiliar implementation detail should be reviewed before the interview instead of being defended through memorized AI-generated wording.

**Technical explanation:** Attribution and competence are separate: disclosing assistance does not replace understanding, while passing tests does not establish that the interview candidate personally wrote every line.

**Project-specific example:** The README and demo include an AI-assistance disclosure. This question bank is explicitly practice material and avoids invented stories about client work or personal debugging experience.

**Likely follow-up:** Which part can you explain without looking at the code?

**Common mistake to avoid:** Claiming sole manual authorship or invented personal experiences.

## 64. How was AI-generated code independently checked?
Category: Limitations and defense

**Spoken answer**

I would describe the evidence, not simply say that another model approved the code. The audit reconstructs source totals, decomposition terms, forecast errors and percentile scores using independent arithmetic. Protected hashes detect accidental changes, while browser and isolated-environment checks test runtime behavior outside a narrow unit-test path. Those checks reduce specific risks but do not prove every business assumption, causal claim or future operational outcome. Independent validation uses a different derivation or information path where possible. Calling the production helper twice checks consistency, whereas a separately derived sum or identity checks whether its result agrees with the specification. The initial reconciliation draft exposed a support-denominator mismatch in the checker itself. It was corrected to the documented common-support metric without changing any frozen analytical outputs.

**Four points to retain**

- I would describe the evidence, not simply say that another model approved the code.
- The audit reconstructs source totals, decomposition terms, forecast errors and percentile scores using independent arithmetic.
- Protected hashes detect accidental changes, while browser and isolated-environment checks test runtime behavior outside a narrow unit-test path.
- Those checks reduce specific risks but do not prove every business assumption, causal claim or future operational outcome.

**Technical explanation:** Independent validation uses a different derivation or information path where possible. Calling the production helper twice checks consistency, whereas a separately derived sum or identity checks whether its result agrees with the specification.

**Project-specific example:** The initial reconciliation draft exposed a support-denominator mismatch in the checker itself. It was corrected to the documented common-support metric without changing any frozen analytical outputs.

**Likely follow-up:** What was the most technically difficult issue in the evidence chain?

**Common mistake to avoid:** Treating tests that mirror implementation as complete independent verification.

## 65. What would a credible next version add?
Category: Limitations and defense

**Spoken answer**

I would start with a named user decision and measure whether the existing evidence actually helps that user. More history and release-aware snapshots would support prospective forecast evaluation and better uncertainty work. Authorized commercial fields could enable a separate sales or inventory analysis with correct units and business definitions. Only then would I add model complexity or automated recommendations, with acceptance criteria and monitoring established in advance. A future roadmap should distinguish planned work from delivered functionality. Prospective evaluation needs new actuals, while operational governance needs users, owners, thresholds and an escalation process. The portfolio already exposes missing intervals, unstable regional ranks and hypothetical assumptions. A next version would address those evidence gaps rather than relabel the current outputs as validated business actions.

**Four points to retain**

- I would start with a named user decision and measure whether the existing evidence actually helps that user.
- More history and release-aware snapshots would support prospective forecast evaluation and better uncertainty work.
- Authorized commercial fields could enable a separate sales or inventory analysis with correct units and business definitions.
- Only then would I add model complexity or automated recommendations, with acceptance criteria and monitoring established in advance.

**Technical explanation:** A future roadmap should distinguish planned work from delivered functionality. Prospective evaluation needs new actuals, while operational governance needs users, owners, thresholds and an escalation process.

**Project-specific example:** The portfolio already exposes missing intervals, unstable regional ranks and hypothetical assumptions. A next version would address those evidence gaps rather than relabel the current outputs as validated business actions.

**Likely follow-up:** What measurable acceptance criterion would you choose?

**Common mistake to avoid:** Presenting roadmap ideas as implemented or validated features.
