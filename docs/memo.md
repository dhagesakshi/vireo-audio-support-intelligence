# Vireo Audio — Weekly Support Intelligence Memo

**To:** Priya Raman, Head of Customer Experience

## Executive takeaway

The analysis turns the support export into a repeatable weekly view of complaint drivers and agent workload. The most actionable signal is repeat contact: the operational repeat-contact proxy is approximately **10.25%** of tickets.

A practical initial target is to reduce this to **8.0%**. At Vireo's stated volume of roughly 650 tickets/week and the policy's blended ₹290/contact planning cost, this corresponds to approximately **190 fewer contacts per quarter and ₹55,000 of quarterly support cost avoided**.

## What customers are telling us

The largest repeat-contact pools are Delivery & Shipping, Billing & Payments, Connectivity, and Returns & Refunds. Together they account for approximately **58%** of repeat-contact proxy tickets in the historical extract.

Repeat-contact tickets also show materially weaker customer experience: historical repeat-proxy tickets average about **2.44 CSAT versus 3.41** for non-repeat tickets among tickets with a score.

## Agent workload

The requested leaderboard is included as a ticket-volume view. Escalations & Warranty is deliberately excluded because the operating policy says Tier-2 cases are multi-touch and should not be compared with Tier-1 on weekly ticket volume.

## Confidence and limitations

The text model is evaluated on a 20% holdout against the exported intake-category labels. This is an agreement test, not independent human ground truth. The classifier is strongest on specific categories and weaker on the broad "Other" class.

The repeat-contact metric is also a transparent proxy because the export does not contain a canonical issue identifier.

## Recommendation

Use the weekly digest to focus operational review on the four largest repeat-contact areas, starting with Delivery, Billing, Connectivity, and Returns. The objective should be fewer repeat contacts, not simply more tickets closed.
