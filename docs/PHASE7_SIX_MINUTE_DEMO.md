# Six-minute interview demonstration

Practice script; describe the project as AI-assisted and adapt ownership claims to work you actually reviewed. Open the local app before the interview. Avoid live dependency installation or model fitting.

| Time | Page / exact action | Metric and spoken explanation | Transition |
|---|---|---|---|
| 0:00–0:40 | Executive Overview, default full window | “This independent project turns NHSBSA atorvastatin community-dispensing records into traceable prescribing intelligence. It covers 36 months, 7 regions and 17 presentations. Items are recorded prescription occurrences; NIC is ingredient cost, not manufacturer revenue.” | “I first made the grain and provenance explicit.” |
| 0:40–1:25 | Open architecture diagram and SQL grain; return Executive | “50,456 source rows become 3,920 monthly rows without losing item or NIC totals. DuckDB separates dimensions, facts, calendar coverage and reporting views. Missing activity remains unknown, and quantities in different units stay separate.” | “That foundation makes the aggregate story defensible.” |
| 1:25–2:15 | Executive annual growth; complete-year decomposition choose 2025 vs 2024 | “2025 item volume increased 7.58%, while NIC changed -39.93%. Volume and mix contributions were positive; the within-presentation ratio contribution was negative. This reconciles an accounting identity rather than explaining a causal price mechanism.” | “I then tested whether the activity could be forecast.” |
| 2:15–3:20 | Forecasting, national/holdout; change horizon 1→3 and inspect hover | “The operational model was frozen using development only. Final holdout errors use true horizons and origin-only scales. ETS MASE pooled over horizons is 0.8883; this screen's selected-horizon cards may differ. Ridge's lower final observed error never changes the frozen selection. Short calibration support means no interval bands.” | “Forecast uncertainty feeds analyst review, not an opportunity claim.” |
| 3:20–4:25 | Decision Intelligence, regional then presentation; inspect evidence and alternate policy | “All seven regional ranks are policy-sensitive. Thirteen presentations lack required forecast evidence and remain unscored, rather than receiving a bad rank. Weights prioritize investigation, and each recommendation links to a source row.” | “The last page makes planning assumptions explicit.” |
| 4:25–5:20 | Scenario Simulator, observed 2025/all regions/all presentations; set +5 and −5 sliders | “NIC is baseline items times the volume multiplier times baseline NIC/item times its multiplier. These changes yield £75,783,764.03 hypothetical NIC. A 5% volume increase requires −4.761905% unit-cost change for accounting equality. No realized savings, causality or clinical substitution is implied.” | “The useful outcome is transparent analysis with testable boundaries.” |
| 5:20–6:00 | Open Phase 7 audit and limitations | “The project is reproducible from preserved evidence, with independent arithmetic, UI tests and real-browser checks. It is not company deployment or patient-level analysis. I would first add release-aware fresh data and business-user validation before operational decisions.” | Invite a question about SQL, leakage, weights or accounting. |

## Interruptions and recovery

- **“Why no manufacturer sales?”** Explain public data availability and the distinction between dispensing and commercial sales. Return to the displayed scope, not a hypothetical revenue estimate.
- **“Why isn't Ridge selected?”** Point to development freeze; clarify holdout must remain evaluation. Resume with horizon support.
- **“Did you write all of this manually?”** State that Codex generated and executed substantial implementation and audit work. Explain only the parts you personally reviewed and can reproduce; never imply independent manual authorship.
- **“Where is the deployed app?”** State actual local/browser status. A release package and guide are not cloud deployment.
- **Technical delay:** Use the actual captured screenshots and presentation; say that the fallback is a captured view, not a live interaction. Do not fabricate a successful control response.

- [Executive Overview](assets/screenshots/01_executive_overview.png)
- [Regional Intelligence](assets/screenshots/02_regional_intelligence.png)
- [Presentation Intelligence](assets/screenshots/03_presentation_intelligence.png)
- [Forecasting & Model Evaluation](assets/screenshots/04_forecasting.png)
- [Decision Intelligence](assets/screenshots/05_decision_intelligence.png)
- [Scenario Simulator](assets/screenshots/06_scenario_simulator.png)
