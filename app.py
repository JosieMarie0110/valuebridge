import html
import logging
from typing import Any

import streamlit as st

from database import (
    DatabaseError,
    create_request,
    list_requests,
    test_connection,
)


st.set_page_config(
    page_title="ValueBridge",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


logging.basicConfig(level=logging.INFO)


REQUEST_CATEGORIES = {
    "Dealer & F&I Enrollment": [
        "Enrollment workflow improvement",
        "F&I presentation support",
        "Dealer activation issue",
        "Enrollment exception",
        "Dealer training or adoption need",
        "Multi-rooftop enrollment request",
    ],
    "Partner Performance & Retention": [
        "Dealer performance reporting",
        "Low program utilization",
        "Dealer retention risk",
        "Dealer follow-up automation",
        "Partner engagement improvement",
        "Regional performance visibility",
    ],
    "Member Payment Experience": [
        "Payment schedule concern",
        "Payment posting issue",
        "Member portal improvement",
        "Loan payoff experience",
        "Member communication improvement",
        "Cancellation or retention concern",
    ],
    "Technology & Integrations": [
        "DMS integration",
        "CRM integration",
        "Lender integration",
        "API enhancement",
        "Data synchronization",
        "Partner portal enhancement",
        "Electronic signature improvement",
    ],
    "Operations & Support": [
        "Dealer support process",
        "Member support process",
        "Manual workflow automation",
        "Escalation process improvement",
        "Operational reporting",
        "Training process improvement",
    ],
    "Compliance & Risk": [
        "Consumer disclosure requirement",
        "Payment compliance requirement",
        "Data privacy requirement",
        "Access-control change",
        "Audit or documentation need",
        "Complaint management concern",
    ],
}


STAKEHOLDER_ROLES = {
    "Dealer Sales": {
        "roles": [
            "Dealer Development Manager",
            "Regional Sales Manager",
            "Sales Director",
            "VP of Sales",
        ],
        "priority": (
            "Dealer growth, enrollment performance, partner relationships, "
            "and revenue opportunity"
        ),
        "concern": (
            "The request may not produce enough dealer impact, enrollment "
            "growth, or commercial value."
        ),
        "framing": (
            "Connect the request to dealer adoption, enrollment volume, "
            "retention, revenue opportunity, or competitive positioning."
        ),
        "questions": [
            "How many dealers or rooftops are affected?",
            "Could this improve enrollment or partner retention?",
            "What commercial opportunity is at risk if the issue is not addressed?",
        ],
    },
    "Dealer Success": {
        "roles": [
            "Dealer Success Manager",
            "Dealer Support Manager",
            "Regional Dealer Manager",
            "Training Manager",
        ],
        "priority": (
            "Dealer activation, adoption, training, support quality, "
            "and consistent program utilization"
        ),
        "concern": (
            "The request may add complexity for dealers or create an "
            "ongoing support burden."
        ),
        "framing": (
            "Show how the request reduces dealer friction, improves training, "
            "increases adoption, or creates a more consistent partner experience."
        ),
        "questions": [
            "Is this affecting one dealer or a broader dealer segment?",
            "Could training or process clarification solve the problem?",
            "What support materials or follow-up would be required?",
        ],
    },
    "Member Services": {
        "roles": [
            "Member Services Manager",
            "Customer Care Manager",
            "Escalation Manager",
            "Member Experience Lead",
        ],
        "priority": (
            "Member satisfaction, clear communication, issue resolution, "
            "and retention"
        ),
        "concern": (
            "The request may increase call volume, create member confusion, "
            "or introduce inconsistent service."
        ),
        "framing": (
            "Explain how the request improves member clarity, payment confidence, "
            "issue resolution, or retention."
        ),
        "questions": [
            "How many members may be affected?",
            "What member confusion or service issue is occurring?",
            "Would communication, training, or workflow changes reduce the issue?",
        ],
    },
    "Payment Operations": {
        "roles": [
            "Payment Operations Manager",
            "Operations Analyst",
            "Processing Manager",
            "Reconciliation Lead",
        ],
        "priority": (
            "Payment accuracy, processing reliability, reconciliation, "
            "and operational efficiency"
        ),
        "concern": (
            "The request may introduce processing risk, reconciliation issues, "
            "or additional manual work."
        ),
        "framing": (
            "Describe the payment or operational problem, affected volume, "
            "current manual effort, and required controls."
        ),
        "questions": [
            "What payment or processing workflow is affected?",
            "How often does the issue occur?",
            "What controls, reconciliation, or exception handling are required?",
        ],
    },
    "Product": {
        "roles": [
            "Product Manager",
            "Product Owner",
            "Head of Product",
            "Product Operations",
        ],
        "priority": (
            "Roadmap alignment, repeatable dealer or member demand, "
            "and measurable product value"
        ),
        "concern": (
            "The request may solve a single partner issue without enough "
            "broader value."
        ),
        "framing": (
            "Show that the problem is repeatable, affects a meaningful dealer "
            "or member segment, and supports adoption, retention, or efficiency."
        ),
        "questions": [
            "Does this issue appear across multiple dealers or members?",
            "Does it align with an existing product objective?",
            "Could a smaller discovery effort validate demand first?",
        ],
    },
    "Engineering": {
        "roles": [
            "Software Engineer",
            "Engineering Manager",
            "Technical Lead",
            "Solutions Architect",
        ],
        "priority": (
            "Clear requirements, secure implementation, system reliability, "
            "and maintainability"
        ),
        "concern": (
            "The request may contain unclear scope, hidden dependencies, "
            "or long-term maintenance cost."
        ),
        "framing": (
            "Describe the dealer, member, or operational problem clearly "
            "without prescribing the only technical solution."
        ),
        "questions": [
            "Which systems, integrations, or data flows are involved?",
            "Can an existing service or API support the request?",
            "What dependencies or maintenance responsibilities would be created?",
        ],
    },
    "Compliance & Legal": {
        "roles": [
            "Compliance Manager",
            "Legal Counsel",
            "Risk Manager",
            "Consumer Affairs Manager",
        ],
        "priority": (
            "Consumer protection, payment compliance, disclosures, privacy, "
            "and auditability"
        ),
        "concern": (
            "The request may create disclosure, consent, privacy, complaint, "
            "or regulatory risk."
        ),
        "framing": (
            "Identify the affected consumers, payment activity, disclosures, "
            "data, jurisdictions, and documentation requirements."
        ),
        "questions": [
            "What consumer disclosure or consent requirements may apply?",
            "What personal or payment data is involved?",
            "What documentation, review, or audit evidence is required?",
        ],
    },
    "Leadership": {
        "roles": [
            "Executive Sponsor",
            "VP of Sales",
            "VP of Operations",
            "Chief Product Officer",
        ],
        "priority": (
            "Strategic alignment, dealer and member value, revenue, risk, "
            "and return on investment"
        ),
        "concern": (
            "The request may have unclear business value, high cost, "
            "or limited strategic importance."
        ),
        "framing": (
            "Lead with dealer impact, member impact, revenue, retention, "
            "risk, cost of inaction, and the decision required."
        ),
        "questions": [
            "What measurable business result is influenced?",
            "What happens if the request is deferred?",
            "What investment, sponsorship, or ownership is required?",
        ],
    },
}


URGENCY_OPTIONS = [
    "Low",
    "Moderate",
    "High",
    "Dealer escalation",
    "Revenue risk",
    "Member-impacting issue",
    "Compliance deadline",
]


BUSINESS_OUTCOMES = [
    "Increase dealer enrollment",
    "Improve dealer activation",
    "Increase program utilization",
    "Protect dealer relationships",
    "Improve F&I adoption",
    "Improve member retention",
    "Reduce enrollment friction",
    "Reduce dealer support effort",
    "Reduce member support effort",
    "Improve payment reliability",
    "Improve operational efficiency",
    "Improve partner reporting",
    "Meet regulatory or compliance needs",
]


SUPPORT_TYPES = [
    "Initial feedback",
    "Dealer workflow review",
    "Technical feasibility assessment",
    "Product discovery",
    "Payment operations review",
    "Compliance review",
    "Effort estimate",
    "Approval",
    "Prioritization",
    "Executive sponsorship",
    "Alternative solution",
]


IMPACT_TYPES = [
    "Revenue influenced",
    "Dealers affected",
    "Rooftops affected",
    "Members affected",
    "Monthly enrollments affected",
    "Retention risk",
    "Operational hours affected",
]


EXAMPLE_REQUESTS = [
    {
        "title": "Reduce F&I enrollment friction",
        "problem": (
            "F&I managers report that the enrollment process takes too long "
            "during a time-sensitive vehicle sale."
        ),
        "outcome": (
            "Make enrollment easier to complete within the dealership's "
            "existing sales process."
        ),
        "stakeholder": "Product Manager",
        "ask": (
            "Review the enrollment workflow and determine whether the issue "
            "is product friction, integration limitations, or dealer training."
        ),
        "color": "blue",
    },
    {
        "title": "Improve dealer utilization reporting",
        "problem": (
            "Dealer-facing teams do not have a consistent view of enrollment "
            "activity, program utilization, or declining participation."
        ),
        "outcome": (
            "Help account teams identify performance gaps and dealers that "
            "may need training, outreach, or additional support."
        ),
        "stakeholder": "Product Operations",
        "ask": (
            "Review available dealer data and identify the measures needed "
            "for a useful performance and retention dashboard."
        ),
        "color": "orange",
    },
    {
        "title": "Connect dealer activity to the CRM",
        "problem": (
            "Sales and dealer-success teams must review multiple systems "
            "to understand partner activity and enrollment performance."
        ),
        "outcome": (
            "Provide relevant dealer, rooftop, and enrollment information "
            "inside the team's existing CRM workflow."
        ),
        "stakeholder": "Solutions Architect",
        "ask": (
            "Assess whether existing APIs and data sources can support a "
            "limited CRM integration and identify major dependencies."
        ),
        "color": "purple",
    },
    {
        "title": "Reduce payment-related member escalations",
        "problem": (
            "Member Services receives repeated questions about payment timing, "
            "posting, and account status."
        ),
        "outcome": (
            "Improve member communication and reduce avoidable service contacts "
            "without creating additional payment risk."
        ),
        "stakeholder": "Payment Operations Manager",
        "ask": (
            "Review the most common escalation reasons and determine whether "
            "process, portal, or communication changes would reduce them."
        ),
        "color": "green",
    },
]


def clean(value: Any) -> str:
    return html.escape(str(value or ""))


def render_html(content: str) -> None:
    st.html(content)


def apply_styles() -> None:
    render_html(
        """
        <style>
        :root {
            --blue: #0879bd;
            --blue-dark: #05567f;
            --blue-deep: #063c59;
            --blue-light: #d7ebf7;

            --green: #6cac3d;
            --green-dark: #477b27;
            --green-light: #e1efd7;

            --orange: #f5a316;
            --orange-dark: #a95f00;
            --orange-light: #ffe8bd;

            --purple: #9d45a2;
            --purple-dark: #67296b;
            --purple-light: #ead4ec;

            --coral: #ee5838;
            --coral-dark: #a93420;
            --coral-light: #fbd8d0;

            --yellow: #f8bf25;

            --page: #cbd5dc;
            --surface: #ffffff;
            --surface-alt: #edf2f5;

            --text: #1e252b;
            --text-soft: #414a52;
            --muted: #626f79;

            --border: #84939e;
            --border-dark: #5b6a75;

            --shadow: 0 10px 26px rgba(23, 34, 43, 0.15);
            --shadow-soft: 0 4px 12px rgba(23, 34, 43, 0.11);
        }

        * {
            box-sizing: border-box;
        }

        .stApp {
            background:
                linear-gradient(
                    135deg,
                    rgba(8, 121, 189, 0.11),
                    transparent 27%
                ),
                linear-gradient(
                    225deg,
                    rgba(108, 172, 61, 0.08),
                    transparent 26%
                ),
                var(--page);
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        div[data-testid="stToolbar"],
        #MainMenu,
        footer {
            display: none;
        }

        .block-container {
            max-width: 1460px;
            padding-top: 1rem;
            padding-bottom: 4rem;
        }

        h1,
        h2,
        h3,
        h4,
        p {
            color: var(--text);
        }

        .app-header {
            position: relative;
            overflow: hidden;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.15rem 1.35rem;
            margin-bottom: 0.9rem;
            box-shadow: var(--shadow);
        }

        .app-header::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 7px;
            background: linear-gradient(
                90deg,
                var(--coral),
                var(--orange),
                var(--green),
                var(--blue),
                var(--purple),
                var(--yellow)
            );
        }

        .brand {
            color: var(--text);
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: -0.04em;
        }

        .brand span {
            color: var(--blue);
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: 0.84rem;
            margin-top: 0.35rem;
        }

        .cloud-status {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.42rem 0.75rem;
            font-size: 0.76rem;
            font-weight: 800;
        }

        .cloud-online {
            color: var(--green-dark);
            background: var(--green-light);
            border: 1px solid #82a96b;
        }

        .cloud-local {
            color: var(--orange-dark);
            background: var(--orange-light);
            border: 1px solid #c58f37;
        }

        div.stButton > button {
            min-height: 43px;
            border: 1px solid var(--border-dark);
            border-radius: 9px;
            background: var(--surface);
            color: var(--text);
            font-weight: 750;
            box-shadow: var(--shadow-soft);
        }

        div.stButton > button:hover {
            border-color: var(--blue-dark);
            background: var(--blue-light);
            color: var(--blue-dark);
        }

        div.stButton > button[kind="primary"] {
            border-color: var(--green-dark);
            background: linear-gradient(
                135deg,
                var(--green),
                var(--green-dark)
            );
            color: white;
        }

        div[data-testid="stExpander"] {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: var(--shadow-soft);
            margin-bottom: 0.8rem;
            overflow: hidden;
        }

        div[data-testid="stExpander"] details {
            background: white;
        }

        div[data-testid="stExpander"] summary {
            color: var(--text);
            font-weight: 800;
        }

        div[data-testid="stExpander"] p {
            color: var(--text-soft);
        }

        .how-to-callout {
            background: var(--blue-light);
            border: 1px solid #82a9c0;
            border-left: 6px solid var(--blue);
            border-radius: 9px;
            padding: 0.85rem 1rem;
            color: var(--blue-deep);
            font-size: 0.88rem;
            font-weight: 750;
            line-height: 1.5;
            margin-top: 0.9rem;
        }

        .value-callout {
            background: var(--green-light);
            border: 1px solid #8bad75;
            border-left: 6px solid var(--green);
            border-radius: 9px;
            padding: 0.85rem 1rem;
            color: var(--green-dark);
            font-size: 0.88rem;
            font-weight: 750;
            line-height: 1.5;
            margin-top: 0.9rem;
        }

        .hero {
            background:
                radial-gradient(
                    circle at 87% 110%,
                    rgba(157, 69, 162, 0.52),
                    transparent 38%
                ),
                linear-gradient(
                    125deg,
                    var(--blue-deep),
                    var(--blue) 72%,
                    #1597dc
                );
            border: 1px solid var(--blue-deep);
            border-radius: 18px;
            padding: 2.6rem;
            margin-bottom: 1.2rem;
            box-shadow: var(--shadow);
        }

        .hero h1 {
            color: white;
            margin: 0 0 0.75rem;
            font-size: 2.4rem;
        }

        .hero p {
            color: white;
            max-width: 860px;
            margin: 0;
            font-size: 1.04rem;
            line-height: 1.65;
        }

        .page-heading {
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 8px solid var(--blue);
            border-radius: 14px;
            padding: 1.3rem 1.45rem;
            margin: 1.15rem 0;
            box-shadow: var(--shadow);
        }

        .page-eyebrow {
            color: var(--orange-dark);
            font-size: 0.75rem;
            font-weight: 850;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .page-heading h1 {
            margin: 0.3rem 0 0;
            font-size: 2rem;
        }

        .page-heading p {
            color: var(--text-soft);
            max-width: 850px;
            margin: 0.5rem 0 0;
        }

        .workflow {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.8rem;
            margin-bottom: 1.25rem;
        }

        .workflow-step {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            box-shadow: var(--shadow-soft);
        }

        .workflow-step:nth-child(1) {
            border-top: 7px solid var(--blue);
        }

        .workflow-step:nth-child(2) {
            border-top: 7px solid var(--orange);
        }

        .workflow-step:nth-child(3) {
            border-top: 7px solid var(--purple);
        }

        .workflow-number {
            display: inline-flex;
            width: 31px;
            height: 31px;
            align-items: center;
            justify-content: center;
            margin-right: 0.45rem;
            border-radius: 8px;
            background: var(--blue-light);
            color: var(--blue-dark);
            font-weight: 850;
        }

        .workflow-step:nth-child(2) .workflow-number {
            background: var(--orange-light);
            color: var(--orange-dark);
        }

        .workflow-step:nth-child(3) .workflow-number {
            background: var(--purple-light);
            color: var(--purple-dark);
        }

        .workflow-label {
            color: var(--text);
            font-weight: 800;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: white;
            border: 1px solid var(--border) !important;
            border-radius: 15px !important;
            box-shadow: var(--shadow);
            overflow: hidden;
            margin-bottom: 1.25rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
        > div[data-testid="stVerticalBlock"] {
            padding: 0 1.45rem 1.45rem;
            gap: 1rem;
        }

        .section-banner {
            margin: 0 -1.45rem 0.45rem;
            padding: 1rem 1.3rem;
            border-bottom: 1px solid var(--border-dark);
        }

        .section-blue {
            background: linear-gradient(
                90deg,
                var(--blue-deep),
                var(--blue)
            );
        }

        .section-orange {
            background: linear-gradient(
                90deg,
                var(--orange-dark),
                var(--orange)
            );
        }

        .section-purple {
            background: linear-gradient(
                90deg,
                var(--purple-dark),
                var(--purple)
            );
        }

        .section-green {
            background: linear-gradient(
                90deg,
                var(--green-dark),
                var(--green)
            );
        }

        .section-title {
            color: white;
            font-size: 1.08rem;
            font-weight: 850;
        }

        .section-description {
            color: white;
            font-size: 0.84rem;
            margin-top: 0.25rem;
        }

        .section-number {
            display: inline-flex;
            width: 30px;
            height: 30px;
            align-items: center;
            justify-content: center;
            margin-right: 0.55rem;
            border: 1px solid rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.16);
        }

        label[data-testid="stWidgetLabel"] p {
            color: var(--text) !important;
            font-size: 0.92rem !important;
            font-weight: 800 !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
            background: white !important;
            border: 2px solid var(--border) !important;
            border-radius: 9px !important;
            box-shadow: 0 2px 5px rgba(20, 31, 40, 0.10) !important;
        }

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {
            border-color: var(--blue-dark) !important;
            box-shadow: 0 0 0 4px rgba(8, 121, 189, 0.20) !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="select"] span {
            color: var(--text) !important;
            background: white !important;
        }

        input::placeholder,
        textarea::placeholder {
            color: #68747d !important;
            opacity: 1 !important;
        }

        .metric-card {
            height: 100px;
            background: white;
            border: 1px solid var(--border);
            border-left: 7px solid var(--blue);
            border-radius: 11px;
            padding: 0.75rem 1rem;
            box-shadow: var(--shadow-soft);
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
        }

        .metric-orange {
            border-left-color: var(--orange);
        }

        .metric-purple {
            border-left-color: var(--purple);
        }

        .metric-green {
            border-left-color: var(--green);
        }

        .metric-label {
            color: var(--text-soft);
            font-size: 0.78rem;
            font-weight: 750;
            line-height: 1.1;
        }

        .metric-value {
            min-height: 1.6rem;
            color: var(--blue-dark);
            margin-top: 0.12rem;
            font-size: 1.35rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .metric-orange .metric-value {
            color: var(--orange-dark);
        }

        .metric-purple .metric-value {
            color: var(--purple-dark);
        }

        .metric-green .metric-value {
            color: var(--green-dark);
        }

        .metric-note {
            color: var(--muted);
            font-size: 0.7rem;
            line-height: 1.2;
            margin-top: 0.1rem;
        }

        .section-intro {
            color: var(--text-soft);
            margin: -0.35rem 0 1rem;
            font-size: 0.92rem;
        }

        .example-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .example-card {
            min-height: 100%;
            background: white;
            border: 1px solid var(--border);
            border-top: 8px solid var(--blue);
            border-radius: 13px;
            padding: 1.2rem;
            box-shadow: var(--shadow-soft);
        }

        .example-orange {
            border-top-color: var(--orange);
        }

        .example-purple {
            border-top-color: var(--purple);
        }

        .example-green {
            border-top-color: var(--green);
        }

        .example-title {
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 850;
            margin-bottom: 0.9rem;
        }

        .example-row {
            margin-top: 0.75rem;
        }

        .example-label {
            color: var(--blue-dark);
            font-size: 0.68rem;
            font-weight: 850;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }

        .example-orange .example-label {
            color: var(--orange-dark);
        }

        .example-purple .example-label {
            color: var(--purple-dark);
        }

        .example-green .example-label {
            color: var(--green-dark);
        }

        .example-value {
            color: var(--text-soft);
            font-size: 0.87rem;
            line-height: 1.5;
            margin-top: 0.18rem;
        }

        .request-card {
            background: white;
            border: 1px solid var(--border);
            border-left: 8px solid var(--blue);
            border-radius: 12px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.7rem;
            box-shadow: var(--shadow-soft);
        }

        .request-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 800;
            margin-top: 0.55rem;
        }

        .request-meta {
            color: var(--text-soft);
            font-size: 0.82rem;
            margin-top: 0.25rem;
        }

        .empty-state {
            background: white;
            border: 1px dashed var(--border-dark);
            border-radius: 13px;
            padding: 1.5rem;
            margin-bottom: 0.9rem;
            box-shadow: var(--shadow-soft);
        }

        .empty-state-title {
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 850;
        }

        .empty-state-text {
            color: var(--text-soft);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-top: 0.35rem;
        }

        .pill {
            display: inline-block;
            padding: 0.28rem 0.62rem;
            margin-right: 0.25rem;
            border-radius: 999px;
            font-size: 0.71rem;
            font-weight: 800;
        }

        .pill-green {
            background: var(--green-light);
            color: var(--green-dark);
            border: 1px solid #82a96b;
        }

        .pill-purple {
            background: var(--purple-light);
            color: var(--purple-dark);
            border: 1px solid #a870ab;
        }

        .pill-orange {
            background: var(--orange-light);
            color: var(--orange-dark);
            border: 1px solid #c58f37;
        }

        .pill-coral {
            background: var(--coral-light);
            color: var(--coral-dark);
            border: 1px solid #cb7d6c;
        }

        .summary-card {
            background: white;
            border: 1px solid var(--border);
            border-left: 7px solid var(--blue);
            border-radius: 11px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.65rem;
            box-shadow: var(--shadow-soft);
        }

        .summary-orange {
            border-left-color: var(--orange);
        }

        .summary-purple {
            border-left-color: var(--purple);
        }

        .summary-coral {
            border-left-color: var(--coral);
        }

        .summary-green {
            border-left-color: var(--green);
        }

        .summary-label {
            color: var(--blue-dark);
            font-size: 0.7rem;
            font-weight: 850;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }

        .summary-orange .summary-label {
            color: var(--orange-dark);
        }

        .summary-purple .summary-label {
            color: var(--purple-dark);
        }

        .summary-coral .summary-label {
            color: var(--coral-dark);
        }

        .summary-green .summary-label {
            color: var(--green-dark);
        }

        .summary-value {
            color: var(--text);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-top: 0.25rem;
        }

        .stakeholder-panel {
            background: var(--surface-alt);
            border: 1px solid var(--border);
            border-top: 8px solid var(--purple);
            border-radius: 13px;
            padding: 1.2rem;
            box-shadow: var(--shadow-soft);
        }

        .stakeholder-title {
            color: var(--purple-dark);
            font-size: 0.75rem;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .stakeholder-role {
            color: var(--text);
            font-size: 1.15rem;
            font-weight: 850;
            margin-top: 0.4rem;
        }

        .stakeholder-text {
            color: var(--text-soft);
            font-size: 0.9rem;
            line-height: 1.55;
            margin-top: 0.65rem;
        }

        @media (max-width: 900px) {
            .example-grid,
            .workflow {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 520px) {
            .block-container {
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }

            .cloud-status {
                display: none;
            }

            .hero {
                padding: 1.7rem;
            }

            .hero h1 {
                font-size: 1.85rem;
            }

            .metric-card {
                height: 94px;
            }
        }
        </style>
        """
    )


def initialize_state() -> None:
    defaults = {
        "page": "Dashboard",
        "selected_request_index": 0,
        "requests_loaded": False,
        "requests": [],
        "database_connected": False,
        "database_message": "Checking storage",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.requests_loaded:
        refresh_requests()


def refresh_requests() -> None:
    try:
        st.session_state.requests = list_requests()

        connected, message = test_connection()
        st.session_state.database_connected = connected
        st.session_state.database_message = message

    except DatabaseError:
        st.session_state.requests = []
        st.session_state.database_connected = False
        st.session_state.database_message = "Local preview mode"

    st.session_state.requests_loaded = True


def navigate(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def render_header() -> None:
    connected = st.session_state.database_connected
    status_class = "cloud-online" if connected else "cloud-local"

    render_html(
        f"""
        <div class="app-header">
            <div>
                <div class="brand">
                    <span>Value</span>Bridge
                </div>

                <div class="brand-subtitle">
                    Dealer, member, and cross-functional alignment workspace
                </div>
            </div>

            <div class="cloud-status {status_class}">
                {clean(st.session_state.database_message)}
            </div>
        </div>
        """
    )

    columns = st.columns([1, 1, 1, 1, 3])

    pages = [
        "Dashboard",
        "New Request",
        "Request Detail",
        "Meeting Brief",
    ]

    for column, page in zip(columns, pages):
        with column:
            if st.button(
                page,
                key=f"nav_{page}",
                type=(
                    "primary"
                    if st.session_state.page == page
                    else "secondary"
                ),
                use_container_width=True,
            ):
                navigate(page)


def render_page_heading(
    eyebrow: str,
    title: str,
    description: str,
) -> None:
    render_html(
        f"""
        <div class="page-heading">
            <div class="page-eyebrow">{clean(eyebrow)}</div>
            <h1>{clean(title)}</h1>
            <p>{clean(description)}</p>
        </div>
        """
    )


def render_section_banner(
    number: int,
    title: str,
    description: str,
    color: str,
) -> None:
    render_html(
        f"""
        <div class="section-banner section-{clean(color)}">
            <div class="section-title">
                <span class="section-number">{number}</span>
                {clean(title)}
            </div>

            <div class="section-description">
                {clean(description)}
            </div>
        </div>
        """
    )


def render_workflow() -> None:
    render_html(
        """
        <div class="workflow">
            <div class="workflow-step">
                <span class="workflow-number">1</span>
                <span class="workflow-label">Define the dealer or member need</span>
            </div>

            <div class="workflow-step">
                <span class="workflow-number">2</span>
                <span class="workflow-label">Establish the business impact</span>
            </div>

            <div class="workflow-step">
                <span class="workflow-number">3</span>
                <span class="workflow-label">Select the right stakeholder</span>
            </div>
        </div>
        """
    )


def render_request_selector(key: str) -> dict[str, Any] | None:
    requests = st.session_state.requests

    if not requests:
        st.info("Create a request first.")
        return None

    options = [
        (
            f"{request.get('title', 'Untitled')} — "
            f"{request.get('stakeholder_role', 'Unmapped')}"
        )
        for request in requests
    ]

    selected_index = st.selectbox(
        "Select request",
        range(len(options)),
        index=min(
            st.session_state.selected_request_index,
            len(options) - 1,
        ),
        format_func=lambda index: options[index],
        key=key,
    )

    st.session_state.selected_request_index = selected_index

    return requests[selected_index]


def get_stakeholder_guidance(
    request: dict[str, Any],
) -> dict[str, Any]:
    team = request.get("stakeholder_team", "Product")

    return STAKEHOLDER_ROLES.get(
        team,
        STAKEHOLDER_ROLES["Product"],
    )


def render_guidance_sections() -> None:
    with st.expander("How to use ValueBridge", expanded=False):
        st.markdown(
            """
            **1. Start with the dealer or member problem**  
            Describe what the dealer, F&I team, member, or internal team is
            trying to accomplish and what is preventing progress.

            **2. Explain the business impact**  
            Add the expected outcome, urgency, supporting evidence, and the
            number of dealers, rooftops, members, enrollments, or dollars affected.

            **3. Identify the right stakeholder**  
            Choose the team and role whose input, approval, review, or support
            is needed.

            **4. Prepare the conversation**  
            Review the stakeholder perspective and use the meeting brief to
            present a clear, business-focused request.
            """
        )

        render_html(
            """
            <div class="how-to-callout">
                A strong request explains the dealer or member problem, the
                measurable impact, the evidence, and the specific decision or
                support needed.
            </div>
            """
        )

    with st.expander("Why ValueBridge matters", expanded=False):
        st.markdown(
            """
            **Improves cross-team collaboration**  
            Gives Dealer Sales, Dealer Success, Member Services, Payment
            Operations, Product, Engineering, Compliance, and leadership a
            shared view of the request.

            **Creates clearer requests**  
            Separates the underlying dealer or member problem from the proposed
            solution and identifies the support that is actually needed.

            **Connects requests to business value**  
            Captures enrollment impact, dealer retention, member experience,
            payment reliability, operational effort, revenue, and compliance risk.

            **Prepares better conversations**  
            Helps sales and dealer-facing teams anticipate stakeholder priorities,
            concerns, dependencies, and questions before the meeting.

            **Supports faster decisions**  
            Creates a concise request and meeting brief that makes ownership,
            decisions, and next steps easier to define.
            """
        )

        render_html(
            """
            <div class="value-callout">
                ValueBridge helps AutoPayPlus teams turn dealer and member needs
                into clear, business-focused requests that improve alignment,
                collaboration, and decision-making across the organization.
            </div>
            """
        )


def render_example_requests() -> None:
    st.subheader("What a strong request looks like")

    render_html(
        """
        <div class="section-intro">
            These examples show how dealer, member, payment, and partner needs
            can be translated into a clear business problem, measurable outcome,
            stakeholder, and specific ask.
        </div>
        """
    )

    cards = []

    for example in EXAMPLE_REQUESTS:
        css_class = f"example-{example['color']}"

        cards.append(
            f"""
            <div class="example-card {css_class}">
                <div class="example-title">
                    {clean(example["title"])}
                </div>

                <div class="example-row">
                    <div class="example-label">Business problem</div>
                    <div class="example-value">
                        {clean(example["problem"])}
                    </div>
                </div>

                <div class="example-row">
                    <div class="example-label">Requested outcome</div>
                    <div class="example-value">
                        {clean(example["outcome"])}
                    </div>
                </div>

                <div class="example-row">
                    <div class="example-label">Stakeholder</div>
                    <div class="example-value">
                        {clean(example["stakeholder"])}
                    </div>
                </div>

                <div class="example-row">
                    <div class="example-label">Specific ask</div>
                    <div class="example-value">
                        {clean(example["ask"])}
                    </div>
                </div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="example-grid">
            {''.join(cards)}
        </div>
        """
    )


def render_dashboard() -> None:
    render_html(
        """
        <section class="hero">
            <h1>Turn sales insight into decision-ready business cases.</h1>

            <p>
                Capture customer demand, quantify commercial impact, align the
                right cross-functional stakeholders, and prepare a clear request
                for action.
            </p>
        </section>
        """
    )

    render_guidance_sections()

    requests = st.session_state.requests

    total_impact = sum(
        int(request.get("impact_value", request.get("revenue", 0)))
        for request in requests
        if request.get("impact_type", "Revenue influenced")
        == "Revenue influenced"
    )

    high_priority = sum(
        request.get("urgency") in {
            "High",
            "Dealer escalation",
            "Revenue risk",
            "Member-impacting issue",
            "Compliance deadline",
        }
        for request in requests
    )

    stakeholder_teams = {
        request.get("stakeholder_team")
        for request in requests
        if request.get("stakeholder_team")
    }

    st.subheader("Workspace overview")

    columns = st.columns(4)

    metrics = [
        (
            "Active Requests",
            len(requests),
            "Dealer and member business cases",
            "",
        ),
        (
            "High Priority",
            high_priority,
            "Requires timely discussion",
            "metric-orange",
        ),
        (
            "Teams Engaged",
            len(stakeholder_teams),
            "Cross-functional groups",
            "metric-purple",
        ),
        (
            "Revenue Influenced",
            f"${total_impact:,.0f}",
            "Revenue-based requests",
            "metric-green",
        ),
    ]

    for column, metric in zip(columns, metrics):
        label, value, note, css_class = metric

        with column:
            render_html(
                f"""
                <div class="metric-card {css_class}">
                    <div class="metric-label">{clean(label)}</div>
                    <div class="metric-value">{clean(value)}</div>
                    <div class="metric-note">{clean(note)}</div>
                </div>
                """
            )

    render_example_requests()

    st.subheader("Recent requests")

    if not requests:
        render_html(
            """
            <div class="empty-state">
                <div class="empty-state-title">
                    No requests have been created yet.
                </div>

                <div class="empty-state-text">
                    Create the first dealer, member, payment, operational, or
                    compliance request when the team is ready.
                </div>
            </div>
            """
        )

        empty_action, _ = st.columns([1.2, 4])

        with empty_action:
            if st.button(
                "Create First Request",
                type="primary",
                use_container_width=True,
                key="create_first_request",
            ):
                navigate("New Request")

        return

    for index, request in enumerate(requests):
        urgency = request.get("urgency", "Moderate")

        if urgency in {
            "Dealer escalation",
            "Revenue risk",
            "Member-impacting issue",
            "Compliance deadline",
        }:
            urgency_class = "pill-coral"
        elif urgency == "High":
            urgency_class = "pill-orange"
        else:
            urgency_class = "pill-green"

        impact_type = request.get(
            "impact_type",
            "Revenue influenced",
        )

        impact_value = int(
            request.get(
                "impact_value",
                request.get("revenue", 0),
            )
        )

        if impact_type == "Revenue influenced":
            impact_text = f"${impact_value:,.0f} revenue influenced"
        else:
            impact_text = f"{impact_value:,} {impact_type.lower()}"

        render_html(
            f"""
            <div class="request-card">
                <span class="pill pill-purple">
                    {clean(request.get("stakeholder_team", "Unmapped"))}
                </span>

                <span class="pill {urgency_class}">
                    {clean(urgency)}
                </span>

                <div class="request-title">
                    {clean(request.get("title", "Untitled request"))}
                </div>

                <div class="request-meta">
                    {clean(request.get("account", request.get("customer", "No dealer or member assigned")))}
                    · {clean(request.get("request_type", "Request"))}
                    · {clean(impact_text)}
                </div>
            </div>
            """
        )

        if st.button(
            "Open request",
            key=f"open_{request.get('id', index)}",
            use_container_width=True,
        ):
            st.session_state.selected_request_index = index
            navigate("Request Detail")


def render_new_request() -> None:
    render_page_heading(
        "Request workspace",
        "Create a dealer or member business request",
        (
            "Capture the information needed to explain the need, quantify the "
            "impact, and prepare for the appropriate cross-functional conversation."
        ),
    )

    render_workflow()

    with st.container(border=True):
        render_section_banner(
            1,
            "Define the request",
            (
                "Describe the dealer, member, payment, operational, "
                "or compliance problem."
            ),
            "blue",
        )

        category_column, type_column = st.columns(2)

        with category_column:
            category = st.selectbox(
                "Request category",
                list(REQUEST_CATEGORIES),
                key="request_category",
            )

        with type_column:
            request_type = st.selectbox(
                "Request type",
                REQUEST_CATEGORIES[category],
                key=f"request_type_{category}",
            )

        title_column, account_column = st.columns([1.3, 1])

        with title_column:
            title = st.text_input(
                "Request title",
                placeholder="Reduce F&I enrollment friction",
                key="request_title",
            )

        with account_column:
            account = st.text_input(
                "Dealer, rooftop, member group, or opportunity",
                placeholder=(
                    "Dealer group, rooftop, member segment, partner, "
                    "or market"
                ),
                key="request_account",
            )

        problem = st.text_area(
            "Business problem",
            placeholder=(
                "What is preventing the dealer, F&I team, member, or internal "
                "team from reaching the desired result?"
            ),
            height=125,
            key="request_problem",
        )

        desired_outcome = st.text_area(
            "Requested outcome",
            placeholder=(
                "What should become easier, faster, more reliable, more compliant, "
                "or more effective?"
            ),
            height=100,
            key="request_desired_outcome",
        )

        proposed_solution = st.text_area(
            "Proposed solution",
            placeholder=(
                "Optional. Capture the current idea without treating it as "
                "the only possible solution."
            ),
            height=90,
            key="request_solution",
        )

    with st.container(border=True):
        render_section_banner(
            2,
            "Establish the business impact",
            (
                "Show how the request affects dealers, members, enrollments, "
                "payments, revenue, retention, or operations."
            ),
            "orange",
        )

        impact_type_column, impact_value_column = st.columns(2)

        with impact_type_column:
            impact_type = st.selectbox(
                "Primary impact measure",
                IMPACT_TYPES,
                key="request_impact_type",
            )

        with impact_value_column:
            impact_value = st.number_input(
                "Estimated impact",
                min_value=0,
                step=1 if impact_type != "Revenue influenced" else 10000,
                format="%d",
                key="request_impact_value",
            )

        urgency_column, outcome_column = st.columns(2)

        with urgency_column:
            urgency = st.selectbox(
                "Urgency",
                URGENCY_OPTIONS,
                key="request_urgency",
            )

        with outcome_column:
            business_outcome = st.selectbox(
                "Primary business outcome",
                BUSINESS_OUTCOMES,
                key="request_business_outcome",
            )

        evidence = st.text_area(
            "Supporting evidence",
            placeholder=(
                "Dealer enrollment trends, F&I feedback, dealer support cases, "
                "member complaints, payment posting issues, cancellation activity, "
                "CRM notes, training completion, partner utilization, lender "
                "exceptions, or repeated requests from multiple rooftops."
            ),
            height=120,
            key="request_evidence",
        )

    with st.container(border=True):
        render_section_banner(
            3,
            "Select the stakeholder",
            (
                "Identify the person whose input, review, approval, "
                "or support is needed."
            ),
            "purple",
        )

        team_column, role_column = st.columns(2)

        with team_column:
            stakeholder_team = st.selectbox(
                "Stakeholder team",
                list(STAKEHOLDER_ROLES),
                key="stakeholder_team",
            )

        stakeholder_config = STAKEHOLDER_ROLES[stakeholder_team]

        with role_column:
            stakeholder_role = st.selectbox(
                "Stakeholder role",
                stakeholder_config["roles"],
                key=f"role_{stakeholder_team}",
            )

        support_type = st.selectbox(
            "Support needed",
            SUPPORT_TYPES,
            key="request_support_type",
        )

        stakeholder_ask = st.text_area(
            "Specific ask",
            placeholder=(
                "Example: Review the dealer enrollment workflow and determine "
                "whether the issue is product friction, integration limitations, "
                "or training."
            ),
            height=110,
            key="request_stakeholder_ask",
        )

        render_html(
            f"""
            <div class="stakeholder-panel">
                <div class="stakeholder-title">
                    Stakeholder perspective
                </div>

                <div class="stakeholder-role">
                    {clean(stakeholder_role)}
                </div>

                <div class="stakeholder-text">
                    <strong>Primary consideration:</strong><br>
                    {clean(stakeholder_config["priority"])}
                </div>

                <div class="stakeholder-text">
                    <strong>Possible concern:</strong><br>
                    {clean(stakeholder_config["concern"])}
                </div>
            </div>
            """
        )

        submitted = st.button(
            "Save Request",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    validation_errors = []

    if not title.strip():
        validation_errors.append("Enter a request title.")

    if not problem.strip():
        validation_errors.append("Describe the business problem.")

    if not desired_outcome.strip():
        validation_errors.append("Describe the requested outcome.")

    if not stakeholder_ask.strip():
        validation_errors.append("Enter a specific stakeholder ask.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)

        return

    request_record = {
        "title": title.strip(),
        "account": account.strip() or "No dealer or member assigned",
        "customer": account.strip() or "No dealer or member assigned",
        "category": category,
        "request_type": request_type,
        "status": "Draft",
        "problem": problem.strip(),
        "desired_outcome": desired_outcome.strip(),
        "solution": proposed_solution.strip(),
        "impact_type": impact_type,
        "impact_value": int(impact_value),
        "revenue": (
            int(impact_value)
            if impact_type == "Revenue influenced"
            else 0
        ),
        "urgency": urgency,
        "business_outcome": business_outcome,
        "evidence": evidence.strip(),
        "stakeholder_team": stakeholder_team,
        "stakeholder_role": stakeholder_role,
        "support_type": support_type,
        "stakeholder_ask": stakeholder_ask.strip(),
    }

    try:
        saved_request = create_request(request_record)

        if st.session_state.database_connected:
            st.session_state.requests_loaded = False
            refresh_requests()
        else:
            st.session_state.requests.insert(0, saved_request)

        st.session_state.selected_request_index = 0

        if st.session_state.database_connected:
            st.success("Request saved.")
        else:
            st.success("Request saved for this session.")

    except DatabaseError as exc:
        local_record = {
            **request_record,
            "id": f"local-{len(st.session_state.requests) + 1}",
        }

        st.session_state.requests.insert(0, local_record)
        st.session_state.selected_request_index = 0

        st.warning(
            f"{exc} The request was retained in this session only."
        )

    if st.button(
        "Open Request Detail",
        type="primary",
        use_container_width=True,
        key="open_saved_request",
    ):
        navigate("Request Detail")


def format_impact(request: dict[str, Any]) -> str:
    impact_type = request.get(
        "impact_type",
        "Revenue influenced",
    )

    impact_value = int(
        request.get(
            "impact_value",
            request.get("revenue", 0),
        )
    )

    if impact_type == "Revenue influenced":
        return f"${impact_value:,.0f}"

    return f"{impact_value:,} {impact_type.lower()}"


def render_request_detail() -> None:
    render_page_heading(
        "Request analysis",
        "Request detail",
        (
            "Review the dealer, member, payment, or operational business case "
            "and how it should be presented to the selected stakeholder."
        ),
    )

    request = render_request_selector("detail_request")

    if not request:
        return

    guidance = get_stakeholder_guidance(request)

    left, right = st.columns([1.1, 1])

    with left:
        with st.container(border=True):
            render_section_banner(
                1,
                "Business request",
                (
                    "The core problem, requested outcome, and measurable "
                    "dealer or member impact."
                ),
                "blue",
            )

            items = [
                (
                    "Request",
                    request.get("title"),
                    "",
                ),
                (
                    "Dealer, member group, or opportunity",
                    request.get(
                        "account",
                        request.get("customer"),
                    ),
                    "",
                ),
                (
                    "Business problem",
                    request.get("problem"),
                    "",
                ),
                (
                    "Requested outcome",
                    request.get("desired_outcome"),
                    "summary-orange",
                ),
                (
                    request.get(
                        "impact_type",
                        "Revenue influenced",
                    ),
                    format_impact(request),
                    "summary-green",
                ),
                (
                    "Primary business outcome",
                    request.get("business_outcome"),
                    "summary-purple",
                ),
                (
                    "Supporting evidence",
                    request.get("evidence") or "No evidence documented.",
                    "summary-orange",
                ),
            ]

            for label, value, css_class in items:
                render_html(
                    f"""
                    <div class="summary-card {css_class}">
                        <div class="summary-label">{clean(label)}</div>
                        <div class="summary-value">{clean(value)}</div>
                    </div>
                    """
                )

    with right:
        with st.container(border=True):
            render_section_banner(
                2,
                "Stakeholder alignment",
                "How to present the request to the selected audience.",
                "purple",
            )

            render_html(
                f"""
                <div class="stakeholder-panel">
                    <div class="stakeholder-title">
                        Primary stakeholder
                    </div>

                    <div class="stakeholder-role">
                        {clean(request.get("stakeholder_role"))}
                    </div>

                    <div class="stakeholder-text">
                        {clean(request.get("stakeholder_team"))}
                    </div>
                </div>
                """
            )

            guidance_items = [
                (
                    "Primary consideration",
                    guidance["priority"],
                    "summary-purple",
                ),
                (
                    "Possible concern",
                    guidance["concern"],
                    "summary-coral",
                ),
                (
                    "Recommended framing",
                    guidance["framing"],
                    "summary-green",
                ),
                (
                    "Support needed",
                    request.get("support_type"),
                    "summary-orange",
                ),
                (
                    "Specific ask",
                    request.get("stakeholder_ask"),
                    "summary-green",
                ),
            ]

            for label, value, css_class in guidance_items:
                render_html(
                    f"""
                    <div class="summary-card {css_class}">
                        <div class="summary-label">{clean(label)}</div>
                        <div class="summary-value">{clean(value)}</div>
                    </div>
                    """
                )

    action_column, _ = st.columns([1.2, 3])

    with action_column:
        if st.button(
            "Generate Meeting Brief",
            type="primary",
            use_container_width=True,
        ):
            navigate("Meeting Brief")


def render_meeting_brief() -> None:
    render_page_heading(
        "Meeting preparation",
        "Meeting brief",
        (
            "Use this summary to prepare for the cross-functional "
            "stakeholder conversation."
        ),
    )

    request = render_request_selector("brief_request")

    if not request:
        return

    guidance = get_stakeholder_guidance(request)

    account = request.get(
        "account",
        request.get(
            "customer",
            "a dealer, partner, or member group",
        ),
    )

    opening = (
        f"We are evaluating {request.get('request_type', 'a request')} "
        f"for {account}."
    )

    business_case = (
        f"The request supports the outcome "
        f"'{request.get('business_outcome', 'business value')}' and has an "
        f"estimated impact of {format_impact(request)}."
    )

    with st.container(border=True):
        render_section_banner(
            1,
            request.get("title", "Meeting brief"),
            (
                f"Prepared for {request.get('stakeholder_role')} within "
                f"{request.get('stakeholder_team')}."
            ),
            "purple",
        )

        brief_items = [
            (
                "Opening",
                opening,
                "",
            ),
            (
                "Dealer, member, or operational problem",
                request.get("problem"),
                "",
            ),
            (
                "Requested outcome",
                request.get("desired_outcome"),
                "summary-orange",
            ),
            (
                "Business impact",
                business_case,
                "summary-green",
            ),
            (
                "Supporting evidence",
                request.get("evidence") or "No evidence documented.",
                "summary-orange",
            ),
            (
                "Possible stakeholder concern",
                guidance["concern"],
                "summary-coral",
            ),
            (
                "Recommended framing",
                guidance["framing"],
                "summary-purple",
            ),
            (
                "Specific ask",
                request.get("stakeholder_ask"),
                "summary-green",
            ),
        ]

        for label, value, css_class in brief_items:
            render_html(
                f"""
                <div class="summary-card {css_class}">
                    <div class="summary-label">{clean(label)}</div>
                    <div class="summary-value">{clean(value)}</div>
                </div>
                """
            )

    st.subheader("Questions to consider")

    for number, question in enumerate(
        guidance["questions"],
        start=1,
    ):
        render_html(
            f"""
            <div class="summary-card">
                <div class="summary-label">Question {number}</div>
                <div class="summary-value">{clean(question)}</div>
            </div>
            """
        )

    render_html(
        """
        <div class="summary-card summary-green">
            <div class="summary-label">Recommended next step</div>

            <div class="summary-value">
                Confirm the owner, agreed action, required review, and target
                follow-up date before the meeting ends.
            </div>
        </div>
        """
    )


def main() -> None:
    apply_styles()
    initialize_state()
    render_header()

    page = st.session_state.page

    if page == "Dashboard":
        render_dashboard()
    elif page == "New Request":
        render_new_request()
    elif page == "Request Detail":
        render_request_detail()
    elif page == "Meeting Brief":
        render_meeting_brief()


if __name__ == "__main__":
    main()
