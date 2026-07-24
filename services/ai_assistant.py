import json
import os
from typing import Any

from google import genai
from google.genai import types


DEFAULT_MODEL = os.getenv(
    "VALUEBRIDGE_AI_MODEL",
    "gemini-2.5-flash",
)

GOOGLE_CLOUD_PROJECT = os.getenv(
    "GOOGLE_CLOUD_PROJECT",
    "",
)

GOOGLE_CLOUD_LOCATION = os.getenv(
    "GOOGLE_CLOUD_LOCATION",
    "global",
)


SYSTEM_INSTRUCTION = """
You are the analysis engine for ValueBridge, an internal sales enablement
platform.

Your job is to help sales professionals turn incomplete customer information
into a credible, decision-ready internal business case.

Rules:
- Use only information provided by the user.
- Never invent customer statements, financial impact, technical requirements,
  timelines, commitments, or internal decisions.
- Clearly distinguish confirmed facts from information that is not yet known.
- When information is missing, use language such as "Not yet confirmed."
- Ask only questions that meaningfully improve the business case.
- Do not repeat questions already answered in the provided information.
- Keep follow-up questions concise and easy for a salesperson to answer.
- Use formal, professional business language.
- Return valid JSON only.
"""


BUSINESS_CASE_FIELDS = [
    "executive_summary",
    "customer_need",
    "business_impact",
    "recommended_stakeholder",
    "recommended_approach",
    "open_questions",
]


def _get_client() -> genai.Client:
    if not GOOGLE_CLOUD_PROJECT:
        raise RuntimeError(
            "GOOGLE_CLOUD_PROJECT is not configured."
        )

    return genai.Client(
        vertexai=True,
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION,
    )


def _format_revenue(value: Any) -> str:
    if value in (None, ""):
        return "Not provided"

    try:
        number = float(value)

        if number <= 0:
            return "Not provided"

        return f"${number:,.2f}"

    except (TypeError, ValueError):
        return str(value)


def _base_context(case_data: dict[str, Any]) -> str:
    account_name = (
        case_data.get("account_name")
        or "Not provided"
    )

    deal_stage = (
        case_data.get("deal_stage")
        or "Not provided"
    )

    revenue_impact = _format_revenue(
        case_data.get("revenue_impact")
    )

    decision_date = (
        case_data.get("decision_date")
        or "Not provided"
    )

    situation = (
        case_data.get("situation")
        or "Not provided"
    )

    evidence = (
        case_data.get("evidence")
        or "Not provided"
    )

    return f"""
ACCOUNT OR OPPORTUNITY
{account_name}

DEAL STAGE
{deal_stage}

REVENUE OR COMMERCIAL IMPACT
{revenue_impact}

TARGET DECISION OR CLOSE DATE
{decision_date}

SALES SITUATION
{situation}

EVIDENCE OR ADDITIONAL CONTEXT
{evidence}
"""


def generate_discovery_questions(
    case_data: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Analyze the initial sales information and return only the most useful
    follow-up questions.

    Each item contains:
    - id
    - question
    - reason
    - placeholder
    """

    client = _get_client()

    prompt = f"""
Review the following sales information.

{_base_context(case_data)}

Identify the most important missing information needed to create a useful
internal business case.

Ask no more than five follow-up questions.

Prioritize questions about:
- The customer's desired outcome
- The business problem or obstacle
- Commercial impact
- Risk of inaction
- Decision timing or urgency
- Evidence supporting the request
- The person or team that raised the request
- Any known technical, operational, legal, or compliance dependencies

Do not ask for information already provided.

If the existing information is already sufficient, return an empty questions
array.

Return JSON in exactly this structure:

{{
  "questions": [
    {{
      "id": "short_unique_id",
      "question": "The question shown to the user",
      "reason": "Why this information matters",
      "placeholder": "A brief example of the type of answer expected"
    }}
  ]
}}
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise RuntimeError(
            "ValueBridge AI returned an empty response."
        )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "ValueBridge AI returned invalid discovery questions."
        ) from exc

    raw_questions = result.get("questions", [])

    if not isinstance(raw_questions, list):
        return []

    cleaned_questions: list[dict[str, str]] = []

    for index, item in enumerate(
        raw_questions[:5],
        start=1,
    ):
        if not isinstance(item, dict):
            continue

        question = str(
            item.get("question", "")
        ).strip()

        if not question:
            continue

        question_id = str(
            item.get("id")
            or f"question_{index}"
        ).strip()

        cleaned_questions.append(
            {
                "id": question_id,
                "question": question,
                "reason": str(
                    item.get("reason", "")
                ).strip(),
                "placeholder": str(
                    item.get("placeholder", "")
                ).strip(),
            }
        )

    return cleaned_questions


def _format_discovery_answers(
    case_data: dict[str, Any],
) -> str:
    discovery_answers = case_data.get(
        "discovery_answers",
        [],
    )

    if not discovery_answers:
        return "No additional discovery answers were provided."

    formatted_items: list[str] = []

    for item in discovery_answers:
        if not isinstance(item, dict):
            continue

        question = str(
            item.get("question", "")
        ).strip()

        answer = str(
            item.get("answer", "")
        ).strip()

        if not answer:
            answer = "Not yet confirmed"

        formatted_items.append(
            f"Question: {question}\nAnswer: {answer}"
        )

    if not formatted_items:
        return "No additional discovery answers were provided."

    return "\n\n".join(formatted_items)


def analyze_business_case(
    case_data: dict[str, Any],
) -> dict[str, str]:
    client = _get_client()

    discovery_context = _format_discovery_answers(
        case_data
    )

    prompt = f"""
Create a formal internal business case using the information below.

{_base_context(case_data)}

FOLLOW-UP DISCOVERY
{discovery_context}

Create these six sections:

1. executive_summary
Provide a concise overview of the opportunity, customer issue, commercial
importance, and recommended internal direction.

2. customer_need
Explain the customer or partner need, the underlying business problem, and the
desired outcome. Clearly identify anything that is not yet confirmed.

3. business_impact
Explain the commercial, operational, retention, expansion, revenue, or customer
experience impact. Do not invent financial impact. State when impact has not
yet been quantified.

4. recommended_stakeholder
Identify one primary internal stakeholder or team and explain why that group is
the appropriate starting point.

5. recommended_approach
Provide a practical internal request, recommended positioning, and next steps.
When the information is incomplete, recommend discovery or validation rather
than presenting assumptions as conclusions.

6. open_questions
List the remaining information, assumptions, dependencies, or evidence that
must still be confirmed. Use "Not yet confirmed" where appropriate.

Return JSON in exactly this structure:

{{
  "executive_summary": "string",
  "customer_need": "string",
  "business_impact": "string",
  "recommended_stakeholder": "string",
  "recommended_approach": "string",
  "open_questions": "string"
}}
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise RuntimeError(
            "ValueBridge AI returned an empty response."
        )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "ValueBridge AI returned an invalid business case."
        ) from exc

    cleaned_result: dict[str, str] = {}

    for field in BUSINESS_CASE_FIELDS:
        value = result.get(field, "")

        if isinstance(value, list):
            value = "\n".join(
                f"- {item}"
                for item in value
            )

        cleaned_result[field] = str(
            value
        ).strip()

    return cleaned_result
