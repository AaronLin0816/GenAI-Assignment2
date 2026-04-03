import argparse
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

SYSTEM_PROMPT = """You are a customer support agent for [Company]. Your job is to draft a \
response to a customer complaint that a human support agent will review before sending.

Before drafting, identify the issue category: billing, shipping, product quality, \
safety/legal, or unclear.

Follow these rules:

- Address the customer by name if their name is mentioned in the complaint; otherwise \
use a neutral greeting.
- Be empathetic and professional in tone throughout.
- Acknowledge the specific issue the customer raised without minimizing it.
- Propose a clear next step or resolution appropriate to the issue category.
- Do NOT admit legal liability, assign blame, or promise specific compensation amounts.
- If the complaint involves a safety incident, legal threat, sensitive personal situation, \
or is too vague to respond to meaningfully, start your response with \
[REQUIRES HUMAN REVIEW] on its own line before the draft.
- Reply in the same language as the customer's complaint.
- Keep the response concise; typically 3-5 sentences, shorter for flagged cases."""

USER_PROMPT = """Customer ID: {user_id}
Customer complaint:
{complaint}

Output only the response text, with no preamble or explanation."""


def build_chain():
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])
    return prompt | llm | StrOutputParser()


def process_complaints(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        complaints = json.load(f)

    chain = build_chain()
    results = []

    for item in complaints:
        user_id = item["user_id"]
        complaint = item["complaint"]
        print(f"Processing user_id={user_id} ...")

        response = chain.invoke({"user_id": user_id, "complaint": complaint})

        results.append({
            "user_id": user_id,
            "complaint": complaint,
            "drafted_response": response,
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(results)} response(s) written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Draft customer support responses from a JSON complaints file."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the input JSON file containing complaints."
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to the output JSON file where drafted responses will be saved."
    )
    args = parser.parse_args()
    process_complaints(args.input, args.output)


if __name__ == "__main__":
    main()
