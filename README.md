# Customer Support Response Drafting Agent

## Overview

This project implements an AI-powered agent that automatically drafts responses to customer complaints. The agent follows a multi-step workflow: it reads an input file of customer complaints, analyzes each complaint for tone, intent, and key issues, and produces a professionally drafted response for each one. A human support agent reviews and sends the final responses, keeping a human in the loop for quality assurance.

## Who Is the User

The intended user is a **customer support representative** or **support team lead** at a company receiving a high volume of written complaints. The user may not have deep technical expertise but needs to process many complaints quickly and consistently. This tool acts as a drafting assistant — it reduces the time spent writing from scratch while the human retains final judgment.

## Input

The system receives a **plain text or structured file** (e.g., `.txt`, `.csv`, or `.json`) containing one or more customer complaints. Each complaint entry includes:

- A customer identifier (name or ID)
- The complaint text submitted by the client

Example input file: `complaints.txt`

## Output

For each complaint in the input file, the system produces a **drafted response** that:

- Acknowledges the customer's concern empathetically
- Addresses the specific issue raised
- Proposes a resolution or next step
- Maintains a professional and brand-appropriate tone

Responses are written to an output file (e.g., `responses.txt`) for the support agent to review and send.

## Why This Task Is Valuable to Automate

Customer support teams routinely handle hundreds of repetitive complaints — billing issues, shipping delays, product defects — that follow predictable patterns. Writing each response manually is time-consuming, error-prone, and leads to inconsistent quality across agents. Automating the drafting step:

1. **Saves time** — agents focus on review and edge cases rather than writing from scratch.
2. **Improves consistency** — every response follows the same quality standard and tone.
3. **Scales with volume** — handles complaint spikes (e.g., after a product recall) without hiring additional staff.
4. **Reduces burnout** — repetitive writing is one of the leading causes of support agent fatigue.

Partial automation (human-in-the-loop review) is the right balance: the AI handles the routine drafting, and the human ensures accuracy and empathy before anything is sent to a real customer.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py --input complaints.txt --output responses.txt
```

## Files

- `app.py` — Main application and agent workflow
- `eval_set.md` — Evaluation dataset with sample complaints and expected responses
- `report.md` — Project report and findings
