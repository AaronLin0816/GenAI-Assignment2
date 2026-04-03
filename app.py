import argparse
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

SYSTEM_PROMPT = """You are a professional customer support agent. Your job is to draft a \
response to a customer complaint. Follow these rules:

- Be empathetic and professional.
- Acknowledge the specific issue the customer raised.
- Propose a clear next step or resolution.
- Do NOT admit legal liability or make promises about specific compensation amounts.
- If the complaint involves a safety incident or legal threat, start your response with \
the tag [REQUIRES HUMAN REVIEW] on its own line before the draft response.
- Reply in the same language as the customer's complaint.
- Keep the response concise (3-5 sentences)."""

USER_PROMPT = "Customer complaint:\n{complaint}"


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

        response = chain.invoke({"complaint": complaint})

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
