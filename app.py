import html
import logging
from typing import Any

import streamlit as st

from components.styles import apply_styles
from database import (
    DatabaseError,
    list_requests,
    test_connection,
)
from pages.business_case import render_business_case


st.set_page_config(
    page_title="ValueBridge",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logging.basicConfig(level=logging.INFO)


STAKEHOLDER_ROLES = {
    "Dealer Sales": {
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


EXAMPLE_REQUESTS = [
    {
        "title": "Reduce F&I enrollment friction",
        "problem": (
            "F&I managers report that enrollment takes too long during "
            "a time-sensitive vehicle sale."
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
            "Dealer-facing teams lack a consistent view of enrollment activity, "
            "program utilization, and declining participation."
        ),
        "outcome": (
            "Help account teams identify performance gaps and dealers that "
            "may need training, outreach, or support."
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
            "inside the existing CRM workflow."
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


def initialize_state() -> None:
    defaults = {
        "page": "Dashboard",
        "selected_request_index": 0,
        "requests_loaded": False,
        "requests": [],
        "database_connected": False,
        "database_message": "Beta v1.0",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.requests_loaded:
        refresh_requests()


def refresh_requests() -> None:
    try:
        st.session_state.requests = list_requests()

        connected, _ = test_connection()

        st.session_state.database_connected = connected
        st.session_state.database_message = "Beta v1.0"

    except DatabaseError:
        st.session_state.requests = []
        st.session_state.database_connected = False
        st.session_state.database_message = "Beta v1.0"

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
                    Sales business case and cross-functional alignment workspace
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
        "Business Case",
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


def render_request_selector(key: str) -> dict[str, Any] | None:
    requests = st.session_state.requests

    if not requests:
        st.info("Build and save a business case first.")
        return None

    options = [
        (
            f"{request.get('title', 'Untitled')} — "
            f"{request.get('stakeholder_role', 'Unmapped')}"
        )
        for request in requests
    ]

    selected_index = st.selectbox(
        "Select business case",
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

    default_guidance = STAKEHOLDER_ROLES["Product"]

    guidance = STAKEHOLDER_ROLES.get(team, default_guidance).copy()

    if request.get("stakeholder_rationale"):
        guidance["priority"] = request["stakeholder_rationale"]

    if request.get("recommended_framing"):
        guidance["framing"] = request["recommended_framing"]

    return guidance


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
        or 0
    )

    if impact_type == "Revenue influenced":
        return f"${impact_value:,.0f}"

    return f"{impact_value:,} {impact_type.lower()}"


def render_guidance_sections() -> None:
    with st.expander("How ValueBridge works", expanded=False):
        st.markdown(
            """
            **1. Describe the sales situation**  
            Explain the customer request, commercial priority, obstacle, and
            what is needed to move the opportunity forward.

            **2. Run the AI analysis**  
            ValueBridge drafts the customer need, business problem, commercial
            impact, risk of inaction, stakeholder recommendation, and internal ask.

            **3. Review the business case**  
            Confirm the language, correct any assumptions, and add missing evidence.

            **4. Prepare the conversation**  
            Save the case and use the meeting brief to guide the cross-functional
            discussion.
            """
        )

        render_html(
            """
            <div class="how-to-callout">
                AI-generated content is a working draft. The salesperson remains
                responsible for confirming the facts, commercial impact, and
                requested action.
            </div>
            """
        )

    with st.expander("Why ValueBridge matters", expanded=False):
        st.markdown(
            """
            **Translates sales insight into business language**  
            Helps Sales explain customer demand in terms that Product,
            Engineering, Operations, Compliance, and Leadership can evaluate.

            **Builds a stronger internal case**  
            Connects the customer need to revenue, retention, adoption,
            operational impact, competitive risk, and urgency.

            **Improves stakeholder alignment**  
            Recommends the team most capable of advancing the request and
            explains why their participation matters.

            **Creates a specific ask**  
            Moves beyond describing the problem by identifying the decision,
            review, action, or commitment Sales needs.
            """
        )

        render_html(
            """
            <div class="value-callout">
                ValueBridge helps Sales convert field intelligence into
                decision-ready business cases for cross-functional action.
            </div>
            """
        )


def render_example_requests() -> None:
    st.subheader("What a strong business case looks like")

    render_html(
        """
        <div class="section-intro">
            Strong cases clearly connect the customer need, commercial impact,
            internal stakeholder, and requested action.
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
                    <div class="example-label">Internal ask</div>
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
                Describe the opportunity, apply commercial context, and use
                AI-assisted analysis to prepare a stronger cross-functional case.
            </p>
        </section>
        """
    )

    render_guidance_sections()

    requests = st.session_state.requests

    total_impact = sum(
        int(
            request.get(
                "impact_value",
                request.get(
                    "revenue",
                    request.get("revenue_impact", 0),
                ),
            )
            or 0
        )
        for request in requests
        if request.get(
            "impact_type",
            "Revenue influenced",
        )
        == "Revenue influenced"
    )

    high_priority = sum(
        request.get("urgency")
        in {
            "High",
            "Dealer escalation",
            "Revenue risk",
            "Member-impacting issue",
            "Compliance deadline",
        }
        for request in requests
    )

    stakeholder_teams = {
        (
            request.get("stakeholder_team")
            or request.get("recommended_stakeholder")
        )
        for request in requests
        if (
            request.get("stakeholder_team")
            or request.get("recommended_stakeholder")
        )
    }

    st.subheader("Workspace overview")

    columns = st.columns(4)

    metrics = [
        (
            "Business Cases",
            len(requests),
            "Saved sales priorities",
            "",
        ),
        (
            "High Priority",
            high_priority,
            "Requires timely engagement",
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
            "Estimated commercial value",
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

    st.subheader("Recent business cases")

    if not requests:
        with st.container(border=True):
            render_html(
                """
                <div class="empty-state">
                    <div class="empty-state-title">
                        No business cases have been created yet.
                    </div>

                    <div class="empty-state-text">
                        Describe a real sales situation and let ValueBridge build
                        the first decision-ready case.
                    </div>
                </div>
                """
            )

            if st.button(
                "Build First Case",
                type="primary",
                use_container_width=True,
                key="build_first_case",
            ):
                navigate("Business Case")

        return

    for index, request in enumerate(requests):
        request_id = (
            request.get("id")
            or request.get("request_id")
            or index
        )

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

        raw_impact_value = request.get(
            "impact_value",
            request.get(
                "revenue",
                request.get("revenue_impact", 0),
            ),
        )

        try:
            impact_value = float(raw_impact_value or 0)
        except (TypeError, ValueError):
            impact_value = 0

        if impact_type == "Revenue influenced":
            impact_text = (
                f"${impact_value:,.0f} revenue influenced"
                if impact_value > 0
                else "Revenue not yet confirmed"
            )
        else:
            impact_text = (
                f"{impact_value:,.0f} {str(impact_type).lower()}"
            )

        account_name = (
            request.get("account")
            or request.get("account_name")
            or request.get("customer")
            or "No account assigned"
        )

        case_title = (
            request.get("title")
            or (
                f"{account_name} Business Case"
                if account_name != "No account assigned"
                else "Untitled business case"
            )
        )

        stakeholder = (
            request.get("stakeholder_team")
            or request.get("recommended_stakeholder")
            or "Unmapped"
        )

        deal_stage = request.get(
            "deal_stage",
            "Stage not provided",
        )

        with st.container(border=True):
            render_html(
                f"""
                <div class="request-card-content">
                    <div class="request-pills">
                        <span class="pill pill-purple">
                            {clean(stakeholder)}
                        </span>

                        <span class="pill {urgency_class}">
                            {clean(urgency)}
                        </span>
                    </div>

                    <div class="request-title">
                        {clean(case_title)}
                    </div>

                    <div class="request-meta">
                        {clean(account_name)}
                        · {clean(deal_stage)}
                        · {clean(impact_text)}
                    </div>
                </div>
                """
            )

            if st.button(
                "Open business case",
                key=f"open_{request_id}",
                use_container_width=True,
            ):
                st.session_state.selected_request_index = index
                navigate("Request Detail")

def render_request_detail() -> None:
    render_page_heading(
        "Business case analysis",
        "Business case detail",
        (
            "Review the customer need, commercial rationale, risk of inaction, "
            "and recommended influence strategy."
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
                "Opportunity and business case",
                (
                    "The customer need, business problem, desired outcome, "
                    "and commercial impact."
                ),
                "blue",
            )

            items = [
                (
                    "Business case",
                    request.get("title"),
                    "",
                ),
                (
                    "Account or opportunity",
                    request.get(
                        "account",
                        request.get("customer"),
                    ),
                    "",
                ),
                (
                    "Deal stage",
                    request.get(
                        "deal_stage",
                        "Not provided",
                    ),
                    "summary-purple",
                ),
                (
                    "Customer need",
                    request.get(
                        "customer_need",
                        "Not documented",
                    ),
                    "",
                ),
                (
                    "Business problem",
                    request.get("problem"),
                    "",
                ),
                (
                    "Outcome required",
                    request.get("desired_outcome"),
                    "summary-orange",
                ),
                (
                    "Commercial impact",
                    request.get(
                        "commercial_impact",
                        format_impact(request),
                    ),
                    "summary-green",
                ),
                (
                    "Risk of inaction",
                    request.get(
                        "risk_of_inaction",
                        "Not documented",
                    ),
                    "summary-coral",
                ),
                (
                    "Evidence",
                    request.get("evidence")
                    or "No evidence documented.",
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
                "Influence strategy",
                (
                    "The recommended stakeholder, positioning, and "
                    "specific internal ask."
                ),
                "purple",
            )

            render_html(
                f"""
                <div class="stakeholder-panel">
                    <div class="stakeholder-title">
                        Recommended stakeholder
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
                    "Why this stakeholder should engage",
                    request.get(
                        "stakeholder_rationale",
                        guidance["priority"],
                    ),
                    "summary-purple",
                ),
                (
                    "Possible concern",
                    guidance["concern"],
                    "summary-coral",
                ),
                (
                    "Recommended framing",
                    request.get(
                        "recommended_framing",
                        guidance["framing"],
                    ),
                    "summary-green",
                ),
                (
                    "Support needed",
                    request.get("support_type"),
                    "summary-orange",
                ),
                (
                    "Internal ask",
                    request.get("stakeholder_ask"),
                    "summary-green",
                ),
                (
                    "Executive summary",
                    request.get(
                        "executive_summary",
                        "Not documented",
                    ),
                    "summary-purple",
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

    missing_information = request.get(
        "missing_information",
        [],
    )

    if missing_information:
        with st.expander(
            "Information that would strengthen the case",
            expanded=False,
        ):
            for item in missing_information:
                st.markdown(f"- {item}")

    action_column, _ = st.columns([1.4, 3])

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
        "Stakeholder meeting brief",
        (
            "Use this summary to present the business case and secure "
            "a clear decision, action, or next step."
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
            "the customer or opportunity",
        ),
    )

    opening = request.get("executive_summary")

    if not opening:
        opening = (
            f"We are evaluating a sales priority for {account}. "
            f"The opportunity requires support from "
            f"{request.get('stakeholder_team', 'a cross-functional team')} "
            f"to move forward."
        )

    business_case = request.get("commercial_impact")

    if not business_case:
        business_case = (
            f"The request has an estimated impact of "
            f"{format_impact(request)}."
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
                "Executive opening",
                opening,
                "",
            ),
            (
                "Customer need",
                request.get(
                    "customer_need",
                    "Not documented",
                ),
                "",
            ),
            (
                "Business problem",
                request.get("problem"),
                "",
            ),
            (
                "Outcome required",
                request.get("desired_outcome"),
                "summary-orange",
            ),
            (
                "Commercial impact",
                business_case,
                "summary-green",
            ),
            (
                "Risk of inaction",
                request.get(
                    "risk_of_inaction",
                    "Not documented",
                ),
                "summary-coral",
            ),
            (
                "Evidence",
                request.get("evidence")
                or "No evidence documented.",
                "summary-orange",
            ),
            (
                "Why this stakeholder should engage",
                request.get(
                    "stakeholder_rationale",
                    guidance["priority"],
                ),
                "summary-purple",
            ),
            (
                "Recommended framing",
                request.get(
                    "recommended_framing",
                    guidance["framing"],
                ),
                "summary-purple",
            ),
            (
                "Internal ask",
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

    st.subheader("Questions to prepare for")

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
            <div class="summary-label">Meeting objective</div>

            <div class="summary-value">
                Confirm the decision, accountable owner, required follow-up,
                and target completion date before the meeting ends.
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

    elif page == "Business Case":
        render_business_case(
            refresh_requests=refresh_requests,
            navigate=navigate,
        )

    elif page == "Request Detail":
        render_request_detail()

    elif page == "Meeting Brief":
        render_meeting_brief()


if __name__ == "__main__":
    main()
