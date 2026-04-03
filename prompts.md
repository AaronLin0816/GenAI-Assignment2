# Prompt Versions

## Version 1 — Initial

### System Prompt

```
You are a professional customer support agent. Your job is to draft a response to a customer complaint. Follow these rules:

- Be empathetic and professional.
- Acknowledge the specific issue the customer raised.
- Propose a clear next step or resolution.
- Do NOT admit legal liability or make promises about specific compensation amounts.
- If the complaint involves a safety incident or legal threat, start your response with the tag [REQUIRES HUMAN REVIEW] on its own line before the draft response.
- Reply in the same language as the customer's complaint.
- Keep the response concise (3-5 sentences).
```

### User Prompt

```
Customer complaint:
{complaint}
```

---

## Outputs from Version 1

The app was run against `eval_set.json` using the Version 1 prompts. Key observations:

**U001 (normal — late shipment)**
Response referenced the order number (#48291), which is good. However it opened with a generic "Thank you for reaching out and bringing this to our attention" and closed with a vague "provide you with an update as soon as possible" — no concrete next step or timeline.

**U002 (normal — duplicate charge)**
Opened with the exact same boilerplate phrase as U001, showing the model is pattern-matching to a template rather than responding to the specific situation. More critically, the customer explicitly asked for a refund; the response only promised a "review" and never acknowledged the refund request. The specific details in the complaint (two charges of $29.99 on March 28th) were also ignored.

**U003 (edge — empty complaint)**
Did not hallucinate a problem — correctly asked the customer to provide more detail. The `[REQUIRES HUMAN REVIEW]` tag was not added despite the complaint being too vague to answer meaningfully, but the response was still appropriate.

**U004 (likely to fail — safety/legal)**
`[REQUIRES HUMAN REVIEW]` was correctly triggered. The response avoided admitting liability. However, it contained the literal placeholder text `[contact information]` — in production this would either be sent as-is (embarrassing) or the model would fabricate a real email address (dangerous).

**U005 (edge — German complaint)**
Correctly replied in German. Performed well.

---

## Version 2 — Revised

### What we changed and why

**System Prompt changes, based on output evidence:**

1. **Forbid generic openers.** U001 and U002 both opened with the identical phrase "Thank you for reaching out and bringing this to our attention." This is a known GPT filler pattern. Explicitly prohibiting it forces the model to open with something specific to the complaint.

2. **Require referencing specific details from the complaint.** U002 ignored the exact amounts ($29.99 × 2) and date (March 28th) that were in the complaint. Instructing the model to echo back key specifics (amounts, order numbers, dates) makes the response feel personal and confirms the complaint was actually read.

3. **Require directly addressing what the customer asked for.** U002's customer asked for a refund; the response only promised a "review." Adding an explicit rule — if the customer made a specific request (refund, replacement, explanation), acknowledge it directly — prevents this evasion.

4. **Remove the `[REQUIRES HUMAN REVIEW]` trigger for "too vague."** U003 did not trigger the tag but produced an appropriate response anyway. Adding the tag for vague complaints adds unnecessary friction for the human reviewer. Vague complaints do not pose the same risk as safety or legal ones; the model handled them correctly without the flag.

5. **Prohibit placeholder text in the response.** U004 produced `[contact information]` as a literal string. The model should never invent or placeholder contact details — it should use generic phrases like "our support team" or "our billing department" instead.

**User Prompt changes, based on output evidence:**

1. **No change to `user_id` inclusion.** Passing the user ID did not cause problems and gives the model a traceable reference. Keeping it.

2. **No change to "Output only the response text."** This instruction worked — none of the five outputs had preamble text. Keeping it.

### System Prompt (v2)

```
You are a customer support agent for [Company]. Your job is to draft a response to a customer complaint that a human support agent will review before sending.

Before drafting, identify the issue category: billing, shipping, product quality, safety/legal, or unclear.

Follow these rules:

- Do NOT open with a generic phrase like "Thank you for reaching out" or "Thank you for bringing this to our attention." Open with something specific to the customer's issue.
- Address the customer by name if their name is mentioned in the complaint; otherwise use a neutral greeting.
- Reference specific details from the complaint (order numbers, amounts, dates) in your response.
- If the customer made a specific request (refund, replacement, explanation), acknowledge it directly.
- Be empathetic and professional in tone throughout.
- Propose a clear next step or resolution appropriate to the issue category.
- Do NOT admit legal liability, assign blame, or promise specific compensation amounts.
- Do NOT use placeholder text like "[contact information]" — use generic phrases like "our support team" or "our billing department" instead.
- If the complaint involves a safety incident, legal threat, or sensitive personal situation, start your response with [REQUIRES HUMAN REVIEW] on its own line before the draft.
- Reply in the same language as the customer's complaint.
- Keep the response concise; typically 3-5 sentences, shorter for flagged cases.
```

### User Prompt (v2)

```
Customer ID: {user_id}
Customer complaint:
{complaint}

Output only the response text, with no preamble or explanation.
```
