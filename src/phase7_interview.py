"""Practice answers, grounded in artifacts rather than invented personal history."""
import json
from .common import ROOT

# Question, four speaking points, technical explanation, example, follow-up, mistake.
QA=[]

def add(category,question,points,technical,example,followup,mistake):
    QA.append((category,question,points.split('|'),technical,example,followup,mistake))

add('Business framing','Why call this pharmaceutical intelligence when it uses NHS prescribing data?',
'I would define the intelligence narrowly: it organizes observed dispensing activity, ingredient cost, forecast reliability and analytical review questions for a pharmaceutical context.|The public source makes the work inspectable, but it cannot replace manufacturer sales, distribution, contracting or patient-level evidence required for many commercial decisions.|The design connects executive summaries to their evidence, so an analyst can distinguish a descriptive finding from model performance and an illustrative planning assumption.|For an interview, the value is demonstrating disciplined analysis and communication across those layers rather than presenting public records as a complete pharmaceutical market.',
'The unit of analysis is recorded prescription activity, not receipts earned by a manufacturer.',
'The dashboard explicitly states that NIC is NHS ingredient cost and labels monitoring scores as analytical priorities.',
'What would change with authorized commercial sales data?',
'Equating prescribing intelligence with measured sales opportunity.')
add('Business framing','Is prescription-item count the same as pharmaceutical demand?',
'An item is a recorded occurrence of a dispensed prescription product, so it is a useful activity measure with a precise administrative definition.|It is not a unique patient, treatment course, tablet count or all demand, because repeat prescriptions and different presentations can contribute multiple items.|The source excludes activity outside its stated community-reimbursement scope, and some observed absence can reflect reporting or applicability rather than no patient need.|I would call the forecast a forecast of recorded activity and request utilization, stock, population and commercial data before interpreting it as total market demand.',
'Separate the measured target from the broader latent business concept it only partially represents.',
'The forecast target is prescription_items; physical total_quantity is retained with unit and not pooled across tablet and liquid records.',
'How would you connect this proxy to an actual demand planning decision?',
'Renaming item totals as patient counts or total market volume.')
add('Business framing','Why did the project use public data instead of manufacturer sales data?',
'Public NHSBSA records allow source attribution, fixed snapshots and independent reconciliation without claiming access to proprietary data that was not supplied.|They still support analyst-relevant questions about data quality, SQL grains, cost ratios, time-series evaluation and transparent dashboard communication across an end-to-end pipeline.|The tradeoff is that commercial variables such as net sales, discounts, channel inventory and promotion are missing, so commercial impact cannot be estimated honestly.|If authorized company data became available, I would redefine measures and joins first, then validate a separate analysis rather than transferring these public-source conclusions directly.',
'Data suitability depends on the decision, grain, provenance and missing business variables, not on whether a dataset is large.',
'The repository records an NHSBSA chemical filter and immutable receipts rather than an Axtria or manufacturer connection.',
'Which commercial fields would you request first?',
'Implying proprietary access or client delivery.')
add('Business framing','What exactly does NIC represent?',
'NIC means net ingredient cost in this source, an administrative ingredient-cost measure associated with recorded dispensing rather than a manufacturer revenue measure.|An analyst needs to preserve that definition when displaying pounds, because the word cost alone can invite an unsupported interpretation as final expenditure or profit.|The weighted NIC-per-item ratio describes the average accounting amount per recorded item within a scope, but presentation mix and unit-cost changes can both affect it.|I would explain the source definition beside the KPI and keep financial planning claims conditional on additional reimbursement, discount and business-accounting information.',
'The dashboard calculates aggregate NIC divided by aggregate items; that is not a mean of row-level unit ratios.',
'The executive page displays the statement “NIC is NHS net ingredient cost, not manufacturer sales revenue.”',
'Does lower NIC/item establish an efficiency improvement?',
'Calling NIC manufacturer sales, realized margin or final total NHS spend.')
add('Business framing','Why did NIC fall while item volume increased?',
'The observed totals can move in opposite directions because ingredient cost is item volume multiplied by a weighted per-item amount influenced by presentation mix.|The project separates volume, presentation mix and within-presentation NIC-per-item contributions using an exact symmetric accounting decomposition whose components reconcile to the observed change.|The within-presentation contribution is sufficiently negative to offset positive volume and mix contributions in the latest annual comparison, which explains the identity mathematically.|That does not identify the real-world cause of lower ratios; evidence about pricing, reimbursement, supply and other mechanisms would be needed for a causal explanation.',
'Use C = V × Σ(s_j × p_j), where the three factors are aggregate volume, item shares and presentation-specific NIC/item.',
'The verified 2025 comparison shows positive volume and mix effects but a negative within-presentation ratio effect.',
'Could patent expiry or negotiation explain the result?',
'Asserting a price mechanism or realized savings from an accounting identity.')
add('Business framing','What business value does this portfolio demonstrate?',
'It demonstrates how an analyst can convert administrative data into a coherent evidence chain, from acquisition and definitions through SQL and a usable executive interface.|A reviewer can inspect denominators, forecast origins, missing evidence and scenario assumptions rather than relying on an attractive chart with unclear business meaning.|The monitoring register makes analytical investigations explicit, while sensitivity tests reveal which apparent priorities depend on policy choices that need domain-user agreement.|I would describe these capabilities as decision support and interview evidence, not quantified company impact, because no intervention or actual client adoption occurred in the project.',
'Business usefulness is demonstrated through traceability and decision boundaries; realized business outcomes require a separate adoption and outcome evaluation.',
'Each proposed investigation links to a supporting source output and rule, while hypothetical scenarios have separate evidence labels.',
'How would you measure usefulness with actual business users?',
'Inventing sales uplift, cost reduction or production adoption.')

add('Data engineering','What is the difference between source rows and analytical rows?',
'Source rows preserve the administrative granularity returned by the API, including available dimensions needed to understand repeated product, region and month records.|The cleaned monthly dataset aggregates compatible records to an explicit business grain, so fewer rows do not imply that useful item or cost totals were discarded.|Before aggregation, source keys and optional fields are validated; afterwards the monthly key and reconciliation checks verify uniqueness and conservation of the additive measures.|I would explain both grains before presenting row counts, because a simple count of duplicates at the wrong grain can confuse legitimate dimensional variation with duplicate data.',
'Aggregation should conserve additive measures while retaining identifiers and units required for subsequent joins.',
'The verified project transforms 50,456 source rows into 3,920 monthly analytical rows with matching item and NIC totals.',
'Which source dimensions disappear during monthly aggregation?',
'Calling every repeated product-month source row a duplicate.')
add('Data engineering','How does the project retain acquisition provenance?',
'Acquisition stores filtered API responses and receipts rather than treating the online endpoint as a permanently unchanged input that can be refreshed invisibly.|Each receipt records the request reference, download information and a content hash, so the analytical release can be tied to the records actually used.|The pipeline refuses to overwrite existing raw evidence during refresh, and later phases compare protected hashes before consuming cleaned or analytical artifacts.|That makes a revised download a new vintage requiring versioned validation, which is important because source corrections can alter a historical series without any code change.',
'SHA-256 checks detect byte differences; they support integrity but do not by themselves establish the truth of a source record.',
'The raw directory includes monthly filtered response files and corresponding receipt JSON files for the fixed extract.',
'What happens if the provider revises a past month?',
'Assuming a reproducible request URL guarantees identical future responses.')
add('Data engineering','How are identifier types preserved during ingestion?',
'Presentation and chemical codes are identifiers, so they should be loaded as strings rather than numeric measures even when some characters look like digits.|Otherwise leading zeros can disappear, and that seemingly minor type conversion can break filters, joins, source comparisons or a supposedly unique business key.|The ingestion checks required columns and configured chemical identity before normalizing dates and measures, keeping physical units and optional missing fields explicit.|I would test type handling at boundaries and reject malformed required identifiers instead of silently coercing them into an alternative code that appears to work.',
'Identifiers carry categorical meaning; numerical operations on them have no business interpretation.',
'The ingestion reader specifies string dtypes and retains the leading-zero atorvastatin chemical code used in the API filter.',
'How would you validate an unexpected identifier format?',
'Converting BNF identifiers to integers because they resemble numbers.')
add('Data engineering','How did the project handle missing months?',
'It constructs a calendar-aware coverage view so that an unobserved month can be distinguished from a recorded zero rather than disappearing in a sorted table.|Coverage diagnostics identify internal gaps and never-observed combinations, and reporting formulas disclose when a comparison lacks sufficient observed periods or a valid denominator.|For forecasting, eligible histories must satisfy documented contiguous-history requirements; incomplete series are not silently repaired simply to increase the number of fitted models.|The interpretation remains cautious because absence can reflect applicability, reporting, launch or discontinuation mechanisms, none of which can be established from a missing cell alone.',
'A complete diagnostic spine and observed fact have different purposes; the spine preserves unknown cells without creating observed activity.',
'The dashboard coverage grid combines observed rows with the absence-only table rather than assuming the absence file already contains every calendar cell.',
'Would you impute gaps for a different operational application?',
'Treating an unobserved row as a known zero.')
add('Data engineering','Why did you avoid zero-filling missing values?',
'Zero is an observed numerical statement, while missing means the activity is not known in the extract, so replacing one with the other changes the meaning of evidence.|That change can bias item totals, growth rates, variability, forecast scales and model comparisons, particularly for sparse presentation-region combinations or newly appearing products.|The project retains nulls in the coverage spine and uses explicit eligibility or unavailable statuses where a required calculation cannot be supported by observed data.|If a business rule later established that a particular absence truly means no activity, I would encode that rule with provenance and test it in a separate version.',
'Imputation is a modeling assumption or a source-defined semantic rule, not a neutral formatting choice.',
'Empty dashboard selections show a no-observations message, and unscored presentations are not assigned zero performance.',
'How would you distinguish a legitimate observed zero?',
'Using fillna(0) to make every chart and metric convenient.')
add('Data engineering','How are anomalous records handled?',
'An anomaly flag indicates a need for review, not a confirmed data error, especially when a small presentation can show large relative changes from a low baseline.|The project preserves the original observations and IQR flags, then adds retrospective MAD, calendar-change and prior rolling-median diagnostics with explicit interpretations.|Robustness analysis examines whether broad findings depend on flagged observations or dominant presentations, while original analytical results remain traceable and unchanged.|I would seek external source confirmation before correcting or deleting a suspicious value, and keep diagnostic exclusions separate from the primary reported dataset and forecast treatment.',
'Retrospective classifications may inspect later observations; they cannot be imported as future-known training interventions.',
'The anomaly code retains legacy flags and describes potential structural shifts without asserting that they are confirmed errors.',
'When would an extreme point justify correction?',
'Deleting outliers automatically or using future anomaly labels during backtesting.')
add('Data engineering','How does hash protection improve reproducibility?',
'It provides a concrete comparison between the artifacts used at baseline and the files present after a later phase, rather than relying on a statement that nothing changed.|The protected inventory covers raw data, cleaned tables, frozen selections, prior reports and executed notebooks, with explicit handling of missing as well as changed files.|New portfolio materials and authorized presentation edits are recorded separately, so the audit can show additions without silently expanding what counts as historical evidence.|I would pair hashes with numerical checks because identical bytes confirm preservation, while independent reductions test whether the preserved calculations and interpretations are internally consistent.',
'Integrity, reproducibility and validity are related but different: a hash only addresses the first directly.',
'Phase 7 captures its protected manifest before portfolio edits and compares every named file at final audit.',
'What if a protected file needs a genuine correction?',
'Updating the baseline hash to hide a discrepancy.')
add('Data engineering','How would you extend the pipeline to more medicines?',
'I would first generalize the configured chemical scope and identifiers while keeping a clear source-to-fact grain, because medicine categories can have different presentations and units.|Partitioning acquisition and validated storage by medicine and month would improve maintainability, but the same dimensional uniqueness and conservation checks would still be required.|Forecast eligibility, feature behavior and monitoring normalization would need review for each scope; scores across unrelated medicine cohorts should not be compared without a meaningful shared policy.|I would add representative fixture tests, capacity measurements and release-aware provenance before scaling the dashboard, rather than assuming that a larger extraction preserves every current analytical assumption.',
'Scaling means validating grains, denominators, storage and modeling assumptions, not just enlarging the API filter.',
'The current repository explicitly scopes one atorvastatin chemical; generalizing it is proposed future work, not an executed multi-medicine result.',
'How would you organize partitions and incremental updates?',
'Claiming performance or validity at a scale that was never tested.')

add('SQL and database design','Why was DuckDB a suitable choice?',
'DuckDB supports analytical SQL over local data and integrates with pandas and Parquet, which suits a reproducible portfolio that does not require a managed database service.|It makes reporting definitions inspectable in SQL, including calendar logic, grouped totals, window comparisons and controlled dimensional joins that can be checked against independent Python calculations.|The local deployment reduces infrastructure and credential requirements, but it is not evidence that the same architecture would satisfy a large multi-user transactional or distributed workload.|I would reassess storage, concurrency and operational requirements for production while retaining the benefit of explicit metric definitions and portable reporting artifacts for the dashboard.',
'The dashboard consumes exported Parquet marts read-only; it does not execute database writes on every interaction.',
'The project validates DuckDB reporting views against saved outputs, then registers the dashboard datasets with schema and hash contracts.',
'When would you choose a server database instead?',
'Calling a local analytical engine a proven enterprise-scale service.')
add('SQL and database design','Why create a fact table instead of analyzing a single flat file?',
'A fact table declares the grain of additive measures, which makes it easier to understand exactly what one row represents before building summaries or joins.|Separate dimensions hold descriptive labels and identifiers, preventing repeated descriptive fields from obscuring which relationships must be unique when a report joins them.|A calendar and coverage model can then preserve time semantics independently of observed rows, allowing meaningful missingness diagnostics and adjacent-month comparisons.|The benefit is not architectural decoration; it is reducing double counting, ambiguous denominators and inconsistent report definitions while making the model understandable to another analyst.',
'Fact grain and join cardinality are contracts that should be validated before interpreting a grouped result.',
'The SQL model supports month-region-presentation reporting while keeping item counts and NIC distinct from physical quantities.',
'What makes a dimension join safe?',
'Adding star-schema labels without validating the actual grain.')
add('SQL and database design','What is the grain of the monthly analytical fact?',
'The fact represents a month, reported region and BNF presentation combination, with the physical unit retained in the source-normalized analytical definition.|That is more specific than medicine by month, so regional and presentation summaries are derived aggregations rather than independent source facts that can be added together.|Business keys must remain populated and unique, and identifiers must have stable types so that label joins do not create additional rows or erase valid combinations.|I would state the grain before discussing totals, because both duplicate prevention and missing-cell interpretation depend on knowing which combinations are expected versus actually observed.',
'One month-region-presentation row contains additive observed item and NIC measures; it is not a patient or manufacturer sales transaction.',
'The dashboard contract checks uniqueness of month, region_code and presentation_key in cost_analytics.',
'Why does the physical unit still matter?',
'Treating a presentation row as a unique patient or ignoring unit distinctions.')
add('SQL and database design','How do you prevent duplicate aggregation?',
'I would validate the source business key at its true dimensional grain first, because repeated simpler product-month keys may be legitimate rather than accidental duplicates.|After monthly aggregation, the fact key must be unique, and any dimension or reference join must enforce the intended many-to-one or one-to-one relationship.|Reconciliation then checks additive totals before and after transformation, so a join that duplicates rows is detected even if a final chart looks plausible.|The dashboard follows the same discipline by loading contract-validated products and calculating scoped summaries from a single observed fact rather than summing overlapping report tables.',
'Uniqueness and measure conservation together are stronger than a blanket drop_duplicates operation.',
'The project tests source and monthly keys, SQL joins and the conservation of historical items and NIC.',
'How would you diagnose a many-to-many join?',
'Using DISTINCT after a faulty join to conceal duplicated measures.')
add('SQL and database design','How are calendar month changes calculated correctly?',
'A row-based lag on an incomplete series can compare March with January and wrongly label the difference as a monthly change when February is absent.|The reporting model uses explicit calendar relationships so that a previous-month comparison refers to the adjacent month rather than merely the previous observed row.|If a required month or denominator is missing, the growth result should remain unavailable or carry an explanatory status instead of receiving a convenient zero.|The same reasoning applies to annual comparisons: the project distinguishes complete aggregate years from partial selected windows, so a filter cannot silently change the meaning of annual growth.',
'Time adjacency is a calendar condition, not just a row-order condition.',
'The executive page withholds annual growth when the selected window does not contain both complete comparison years.',
'What would a missing-February fixture test assert?',
'Applying LAG to observed rows and calling every difference month-on-month.')
add('SQL and database design','Why use a ratio of sums for NIC per item?',
'A row with a small number of items should not have the same influence on an overall per-item amount as a row contributing a large volume.|Summing NIC and dividing by summed items produces the quantity-weighted accounting ratio for the displayed scope, which reconciles back to its additive inputs.|An unweighted average of row ratios answers a different question and can change substantially when the data is split into more rows or grouped differently.|I would make the denominator explicit and leave the result unavailable when aggregate items are not positive, rather than returning zero or an arbitrary replacement.',
'Weighted NIC/item = Σ NIC / Σ items; equivalent row-ratio weights are items_i / Σ items.',
'The executive, regional and presentation KPI calculations all use the aggregate ratio for their active filters.',
'When would an unweighted average be meaningful?',
'Averaging regional or presentation unit ratios to calculate the national ratio.')
add('SQL and database design','How are contribution shares scoped?',
'A share is meaningful only relative to a specified denominator, so both its period and entity population need to be visible when users filter a report.|Regional contribution uses all reported regions in the selected year, even if the display shows a smaller region subset; otherwise selecting one region would misleadingly create a 100% share.|Presentation shares use all presentations within the selected regions and year, while the displayed numerator follows the selected presentation choices.|I would test those distinct scopes and label them beside the view, because a technically correct percentage can still communicate the wrong business meaning if its denominator is hidden.',
'Numerator filters and denominator filters need not be identical, but their difference must be intentional and disclosed.',
'The regional page explicitly captions the all-region denominator and downloads the same filtered summary it displays.',
'Should shares sum to 100% after selecting a subset?',
'Recomputing every filtered subset share as if it were the full observed market.')
add('SQL and database design','Why export reporting marts to Parquet?',
'Parquet preserves column types and supports efficient local reads, making it suitable for a dashboard that needs stable reporting products rather than repeatedly rebuilding analytical queries.|The export creates a clear boundary between validated analysis and presentation, so dashboard interaction cannot accidentally retrain models or alter the historical SQL database.|A manifest records schema, business keys, row counts and content hashes; the loader rejects critical mismatches and returns copies of cached frames to prevent shared mutation.|CSV remains useful for human downloads, but runtime calculations use typed validated data so that dates, identifiers and missing values do not rely on implicit text parsing.',
'The dashboard manifest is a versioned runtime data contract, not a license to accept arbitrary files with matching names.',
'All registered Phase 6 datasets are checked against their Parquet hashes before being used by page calculations.',
'How do you handle a new validated data release?',
'Regenerating the manifest solely to make a corrupted file pass.')

def build(root=ROOT):
    if len(QA)==22:
        from .phase7_questions_extra import extend
        extend(add)
    lines=['# Technical interview practice — 65 substantial answers','',
        'Practice material, not a claim that the user personally performed every implementation step. Codex generated and executed substantial work. Explain only reviewed evidence and actual personal contributions. Answers target roughly 45–90 seconds at a conversational pace; rehearse and adapt rather than memorize.','']
    for i,(category,q,points,technical,example,followup,mistake) in enumerate(QA,1):
        answer=' '.join(points)+' '+technical+' '+example
        lines += [f'## {i:02d}. {q}',f'Category: {category}','', '**Spoken answer**','',answer,'',
            '**Four points to retain**','',*['- '+p for p in points],'', '**Technical explanation:** '+technical,'',
            '**Project-specific example:** '+example,'','**Likely follow-up:** '+followup,'','**Common mistake to avoid:** '+mistake,'']
    (root/'docs/PHASE7_INTERVIEW_QA.md').write_text('\n'.join(lines),encoding='utf-8')
    meta={'questions':len(QA),'categories':{},'answer_word_counts':[len((' '.join(p)+' '+t+' '+e).split()) for _,_,p,t,e,_,_ in QA]}
    for category,*_ in QA: meta['categories'][category]=meta['categories'].get(category,0)+1
    (root/'outputs/phase7/validation/interview_inventory.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    return meta

if __name__=='__main__': build()
