# Vireo Audio — Submission Form



 1. What did you build, and what business outcome does it move?

I built a lightweight AI-assisted support intelligence pipeline and Streamlit dashboard that classifies support tickets, produces a weekly complaint digest, and provides a weekly Tier-1 ticket-volume leaderboard.

The business target is to reduce the repeat-contact proxy from approximately 10.25% to 8.0%. At about 650 tickets/week, this represents roughly 190 fewer repeat contacts per quarter. Using Vireo's ₹290 blended cost per support contact, that is approximately ₹55,000 in quarterly support cost avoided.

This is an estimated opportunity, not a guaranteed saving.



 2. What does one run cost, and what is the monthly cost at \~650 tickets/week?

The runtime classifier uses local TF-IDF + Logistic Regression, so there are no paid external AI/API inference calls.



- External AI/API cost per run: ₹0

- Approximate monthly volume: 650 × 4.33 = \~2,815 tickets/month

- Variable AI/API cost per month: 2,815 × ₹0 = ₹0


Local compute is not separately metered, so the ₹0 figure refers specifically to external AI/API inference cost.



 3. How do you know it works?

I evaluated the classifier on a stratified 20% holdout sample of 2,375 tickets.



- Agreement with the exported intake labels: 82.3%

- Macro-F1: 0.822

- Disagreement against the exported intake labels: approximately 17.7%

This is agreement with the source labels, not independent human-ground-truth accuracy.

The system also includes deterministic checks for ticket reconciliation, weekly aggregation, business metrics, and leaderboard calculations.



4. Did you change, narrow, or push back on the client ask?

Yes.

I kept the requested leaderboard but narrowed its interpretation to ticket volume/workload rather than agent performance. This avoids treating raw ticket counts as a quality or productivity score.

I also excluded Escalations \& Warranty from the requested weekly volume leaderboard because the supplied policy indicates that Tier-2/warranty cases are handled differently and measured in days rather than simple weekly ticket volume.

For repeat contact, the policy's exact definition requires identifying the same issue. The export did not contain a canonical issue ID, so I implemented a transparent proxy using the same customer, product, intake category, and a new contact within 30 days after the prior resolution.


5. What is wrong with what you are handing us?

The main limitations are:



- Repeat contact is a proxy rather than exact first-contact resolution because the export lacks a canonical issue ID.

- Model validation is against exported intake labels rather than independently reviewed human labels.

- The leaderboard measures ticket volume/workload only and should not be interpreted as an overall agent performance score.

- Very sparse trailing weeks are excluded from the default executive/leaderboard view to avoid misleading comparisons.



6. What did you deliberately leave out, and why?


I deliberately left out:

- An external LLM call for every ticket, to avoid unnecessary per-ticket cost and dependency on an API key.

- A composite agent-performance score, because ticket count alone does not measure quality, complexity, or customer outcomes.

- An exact FCR calculation, because the source data does not contain a canonical issue identifier.

- A larger production platform, because the requested outcome can be delivered more simply within the stated effort constraint.


7. Anything you built/found that nobody asked for?

Yes.

I added data-quality and reconciliation checks, model validation reporting, SLA-breach and transfer metrics, a quantified business case, and an explicit methodology/limitations section.

These make the weekly output more auditable and help distinguish measured facts from assumptions and proxies.



 8. What did you use AI for?


I used ChatGPT during development for architecture decisions, code drafting/review, debugging, documentation, and analysis of implementation choices.

The runtime classification model is local TF-IDF + Logistic Regression rather than an external LLM.

I considered a per-ticket external LLM approach but deliberately discarded it because it would add unnecessary cost, latency, and API dependency for this use case.

Recording:

https://drive.google.com/file/d/1RkogDpCmMdYYOFeHU0oaI2urZviBSqCy/view?usp=sharing



 9. Monday handoff — three things they need to know


1. Run `python -m src.pipeline` to process the supplied data and generate the analysis outputs.

2. Run `streamlit run app/dashboard.py` to open the dashboard.

3. The key business metric is the repeat-contact proxy: approximately 10.25% currently versus an 8.0% target. The leaderboard is a ticket-volume/workload view, not an overall agent-performance score.



 10. Honest hours spent

 3.6 hours



 11. GitHub Repo Link

https://github.com/dhagesakshi/vireo-audio-support-intelligenc

