# Data source evaluation

Research performed 11 October 2026 (Asia/Kolkata). Verification levels below distinguish
publisher metadata, acquired records and unverified third-party descriptions. Counts that were not
measured are deliberately left unknown. The final acquired dimensions are in INITIAL_DATA_ASSESSMENT.md.

| Candidate / publisher | Official source | License / permitted use | Fields and grain | Coverage and records | Suitability and decision |
|---|---|---|---|---|---|
| PCA monthly administrative data / NHS Business Services Authority | [Dataset](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data), [API metadata](https://opendata.nhsbsa.net/api/3/action/package_show?id=prescription-cost-analysis-pca-monthly-data) | OGL 3.0, attribution required; reuse and commercial use allowed subject to license conditions | Monthly community dispensing; BNF presentation, SNOMED, supplier, region, STP/ICB, dispenser account type, preparation classes, items, quantity/unit, NIC | England community dispensing; metadata says January 2021 onward. Saved metadata lists 67 monthly resources. January 2021 schema probe API total: 574,680 rows in that full resource, not the chosen extract. Full multi-month record count not acquired | Selected. Credible public cost/volume and geography; bounded extract supports demand-proxy forecasting later. NIC is not company revenue; excludes hospital/private dispensing |
| OpenPrescribing / Bennett Institute, University of Oxford; underlying NHSBSA data | [About](https://openprescribing.net/about/), [API](https://openprescribing.net/api/) | Underlying prescribing data uses OGL; attribute NHSBSA and OpenPrescribing. Website code MIT is a separate license | Monthly primary-care prescribing, product/BNF selection and organisation aggregations; API field/schema details not independently verified in this run | England; site describes monthly NHSBSA inputs. Exact accessible API coverage/count unknown because download endpoint returned HTTP 403 | Strong accessible-analysis design in principle, but rejected for this run's acquisition because endpoint was blocked. Do not treat GP prescribing and PCA dispensing as identical populations |
| PCA annual accredited official statistics / NHSBSA | [Publication collection](https://www.nhsbsa.nhs.uk/statistical-collections/prescription-cost-analysis-england), [data portal](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-annual-statistics) | Portal lists OGL 3.0, with attribution | Annual dispensing volumes and net ingredient cost, product/BNF hierarchy, national and ICB summaries | England; multiple annual editions; historical sources linked back to 1998. Exact records and continuous coverage of a single schema not downloaded/verified | Useful official benchmark; annual grain is weaker for monthly seasonality. Administrative monthly and annual geographic conventions can differ |
| Pharma sales data / Milan Zdravkovic (Kaggle) | [Publisher page](https://www.kaggle.com/datasets/milanzdravkovic/pharma-sales-data) | Original page yielded no inspectable content. [Third-party mirror](https://github.com/mcallara/pharma-sales-data) claims CC BY-NC 4.0; original license not independently verified. No commercial-use assumption | Mirror says hourly/daily/weekly/monthly sales in eight ATC categories; revenue, geography and physical units not independently confirmed | Mirror says 2014–2019; country, monthly record count and full original provenance unknown in this run | Potential compact volume forecasting exercise; weaker provenance and licensing confidence than NHSBSA. Not downloaded or selected. Mirror claims are not original-source verification |
| UCI pharmaceutical sales search / UCI Machine Learning Repository | [Sales catalog search](https://archive.ics.uci.edu/datasets?search=sales), [Drug Consumption](https://archive.ics.uci.edu/ml/datasets/Drug) | The inspected Drug Consumption page lists CC BY 4.0; no pharmaceutical-sales candidate license established | Catalog includes generic weekly sales and drug-related research, but an eligible pharmaceutical commercial monthly-sales dataset was not located. Drug Consumption describes personality/substance-use risk, not pharmaceutical transactions | Eligible pharmaceutical-sales fields, record count, geography and time coverage: not established | Not selected. Search did not verify a UCI pharma-sales dataset; this is not a claim that none exists. Drug Consumption cannot answer commercial demand questions |

## Selection and extract design

Use NHSBSA PCA monthly data for January 2023–December 2025, filtered to the source-confirmed
chemical code **0212000B0 (Atorvastatin)**. Keep every matching presentation and dispensing geography.
This gives three complete calendar years, limits transfer size, and preserves real product variation.
It is a one-chemical portfolio scope, not a representative sample of the pharmaceutical market.
No forecasting is implemented in Phase 1. Later phases must select series with adequate history.

The source has 26 columns in the January 2021 schema probe; later resources use ICB instead of STP
columns. The acquisition manifest records the actual chosen source schema and rows. All code values
are treated as strings to preserve leading zeros. Quantities are never aggregated across units.
The executed 2023–2025 extract has a 27-column union: PHARMACY_ADVANCED_SERVICE appears from
February 2024. Earlier resources have 26 fields; this is recorded per page and treated as structural
schema absence rather than missing dispensing data.

## Verification and acquisition findings

- The original attachment's requested UCI search did not identify a verified pharma-sales dataset.
- OpenPrescribing's sample API request returned HTTP 403 after network access was permitted.
- NHSBSA package_show succeeded; original publisher JSON is preserved in data/raw/source_metadata.json.
- NHSBSA datastore_search takes filter **array values**, e.g. `{"BNF_CHEMICAL_SUBSTANCE_CODE":["0212000B0"]}`.
  Scalar filters silently returned empty arrays. Preserved source probes demonstrate this behavior.
- A drug-name probe returned Atorvastatin and its current source code; inferred historical BNF codes
  were not used after verification. The earlier empty response is retained as acquisition research evidence.
- The API's `total` is the full resource total even with filters in inspected responses. Pagination therefore
  uses returned page length and includes a final empty page when needed; it does not assume total is filtered.
- Individual acquired pages have receipts recording exact UTC download times and SHA-256 hashes.
  The initial metadata was saved during research before receipt logging; its exact download timestamp was
  not recorded and is not fabricated. It was accessed on 11 October 2026.

## Hybrid design and license attribution

Real observed prescribing data can support cost and dispensing intelligence. Commercial sales-force,
promotion and realized revenue questions need separately labeled synthetic scenario tables in future
phases; no synthetic revenue is created in Phase 1. `--synthetic` is an explicit, seeded offline fallback,
with `data_origin=synthetic_demo`; it is never silently substituted for an unsuccessful download.

Attribution: NHS Business Services Authority, “Prescription Cost Analysis (PCA) Monthly Administrative
Data”, accessed 11 October 2026, [official source](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data).
Contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
The publisher asks people planning publication to contact its data service to avoid misrepresentation;
this local portfolio implementation does not publish data or send messages.

## Manual download if API access changes

Open the official monthly dataset page, locate each PCA_YYYYMM resource for 202301 through 202512,
and select its CSV download. Save the original CSVs separately under data/raw/manual. Source URLs and
resource IDs are also available in the saved metadata. `src.ingest.load_csv` handles UTF-8 BOM/CP1252
and preserves identifiers, but the normal pipeline expects API evidence; manual files require an explicit
adapter and equivalent manifest before being substituted. Alternatively use `python run_pipeline.py
--synthetic` for a clearly marked demo. No manual download is claimed here.
