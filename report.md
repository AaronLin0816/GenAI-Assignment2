# Project Report: Customer Support Response Drafting Agent

## Business Use Case

Customer support teams at product companies routinely receive high volumes of written complaints that follow predictable patterns: late shipments, billing errors, defective items, account access issues. Each complaint requires a written response that acknowledges the issue, proposes a resolution, and maintains a professional tone. Writing these from scratch is time-consuming and leads to inconsistent quality across agents and shifts. This project automates the drafting step — the system reads a JSON file of customer complaints and produces a first-draft response for each one. A human support agent reviews and sends the final text. The goal is not to remove the human from the loop, but to eliminate the blank-page problem and let agents focus on review rather than composition.

## Model Choice

The system uses **GPT-4o-mini** via the OpenAI API. This choice was primarily practical: an `OPENAI_API_KEY` was already available in the environment, and `langchain-openai` was already installed, whereas the initially planned model (Claude Haiku via `langchain-anthropic`) required separate credential setup that was not available at evaluation time.

Within the constraints of GPT-4o-mini, the model performed adequately for routine cases and correctly triggered the `[REQUIRES HUMAN REVIEW]` flag for the safety/legal complaint. A stronger model (GPT-4o or Claude Sonnet) would likely produce more nuanced responses and be more reliable on the edge cases, at higher cost per call. For a production deployment where volume is high and cost matters, GPT-4o-mini is a reasonable choice provided the prompt guardrails are tight — which is exactly what the iteration below was aimed at.

## Baseline vs. Final Design: Prompt Iteration

The system was first run against all five evaluation cases using the initial (v1) prompts. The outputs revealed three concrete problems that informed a revised (v2) prompt.

**Problem 1: Identical boilerplate openers.**
U001 (late shipment) and U002 (duplicate charge) both opened with the exact same phrase: *"Thank you for reaching out and bringing this to our attention."* This phrase carries no information and signals to the customer that their complaint was processed by a template, not read by a person. The v2 system prompt explicitly forbids this pattern and requires the opener to be specific to the complaint.

**Problem 2: Evasion of the customer's actual request.**
U002's customer explicitly asked for a refund. The v1 response promised only to "initiate a review" — it never acknowledged the refund request and ignored the specific amounts ($29.99 × 2) and date (March 28th) that were in the complaint. This is a meaningful quality failure: a customer who asked for a concrete action and received a vague process response is likely to escalate. The v2 prompt adds two rules: reference specific details from the complaint, and directly acknowledge any specific request the customer made.

**Problem 3: Placeholder text in production-bound output.**
U004 (product fire, legal threat) correctly triggered `[REQUIRES HUMAN REVIEW]`, but the draft response contained the literal string `[contact information]`. In production, this would either be sent verbatim (unprofessional) or the model would hallucinate a real email address (dangerous). The v2 prompt explicitly prohibits placeholder text and instructs the model to use generic department names instead.

One v1 behavior that worked well and was preserved: U003 (empty complaint, a single period) did not trigger `[REQUIRES HUMAN REVIEW]` but correctly asked the customer to provide more detail without fabricating a problem. The original intent to flag vague complaints was removed from v2 since the model handled them appropriately without it, and unnecessary flags create friction for the human reviewer.

U005 (complaint in German) worked correctly in both versions — the model replied in German without instruction failures.

## Where the Prototype Still Fails

The most significant remaining failure mode is the **safety and legal case (U004)**. Although the `[REQUIRES HUMAN REVIEW]` flag is correctly applied, the draft response underneath still contains language that a legal team would likely object to ("Your safety and satisfaction are incredibly important to us" in the context of a product fire can be read as soft admission of a duty of care). The system currently has no mechanism to prevent a rushed human reviewer from sending a flagged draft without actually reading it — the flag is advisory only. Beyond the legal case, the system has no awareness of prior interactions: it cannot tell whether this is a customer's first complaint or their fifth, whether a previous agent already made a promise, or whether the account has been flagged for fraud. Any of these contexts could make a confidently drafted response wrong or harmful. A single round of prompt iteration on five cases is not sufficient to characterize the full failure distribution.

## Deployment Recommendation

This prototype is not ready for unsupervised deployment. It is ready for a **supervised pilot** under the following conditions:

1. **Mandatory human review for all flagged cases.** The `[REQUIRES HUMAN REVIEW]` tag must be treated as a hard gate, not a suggestion. Flagged drafts should require a second approval step before they can be sent.

2. **No auto-send capability.** Every drafted response, flagged or not, must pass through a human review queue. The value of the system is in reducing drafting time, not in removing human judgment from the loop entirely.

3. **Replacement of placeholder company name.** The string `[Company]` in the system prompt must be replaced with the actual company name before any production use.

4. **Escalation path for the legal/safety case.** The current draft for U004-type complaints is still too verbose and warm-toned for a legal threat situation. A stricter response template — or a rule to produce no draft at all and route directly to legal — should replace the current behavior for this class of complaint.

5. **Evaluation on a larger, real complaint sample.** Five synthetic cases are enough to find obvious prompt failures but not enough to characterize tail behavior. Before wider rollout, the prompt should be tested against at least 50-100 real complaints spanning the full range of issue types and tones the team actually receives.

Under these conditions, the system offers genuine value: it eliminates the blank-page problem for routine cases, enforces consistent tone, and surfaces high-risk complaints for prioritized review. The risk of harm comes not from the model itself but from process failures around it — specifically, from a human reviewer who treats the draft as final without reading it. That risk is manageable with the right workflow controls, but it must be designed in deliberately before deployment.
