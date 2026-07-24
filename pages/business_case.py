from datetime import date
from io import BytesIO
from typing import Any, Callable, Optional

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from database import save_request
from services.ai_assistant import (
    analyze_business_case,
    generate_discovery_questions,
)


DEAL_STAGES = [
    "Discovery",
    "Solution Evaluation",
    "Business Case Development",
    "Proposal",
    "Negotiation",
    "Expansion",
    "Renewal",
    "Existing Customer Request",
    "Other",
]


OUTPUT_FIELDS = [
    (
        "executive_summary",
        "Executive Summary",
        "A concise overview of the opportunity and recommended direction.",
    ),
    (
        "customer_need",
        "Customer Need",
        "The need, business problem, and desired outcome.",
    ),
    (
        "business_impact",
        "Business Impact",
        "The commercial importance, operational effect, and risk of inaction.",
    ),
    (
        "recommended_stakeholder",
        "Recommended Stakeholder",
        "The primary internal stakeholder and why they are the right starting point.",
    ),
    (
        "recommended_approach",
        "Recommended Approach",
        "The recommended internal request, positioning, and next steps.",
    ),
    (
        "open_questions",
        "Open Questions",
        "Information, assumptions, or dependencies that still need confirmation.",
    ),
]


RefreshCallback = Optional[Callable[[], None]]


def _initialize_state() -> None:
    defaults = {
        "business_case_stage": "input",
        "business_case_generated": False,
        "business_case_saved": False,
        "business_case_id": None,
        "generated_case": {},
        "discovery_questions": [],
        "case_account_name": "",
        "case_deal_stage": DEAL_STAGES[0],
        "case_revenue_impact": 0.0,
        "case_decision_date": date.today(),
        "case_situation": "",
        "case_evidence": "",
        "business_case_pdf": None,
        "business_case_pdf_name": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _validate_input() -> list[str]:
    errors: list[str] = []

    account_name = str(
        st.session_state.get(
            "case_account_name",
            "",
        )
    ).strip()

    situation = str(
        st.session_state.get(
            "case_situation",
            "",
        )
    ).strip()

    if not account_name:
        errors.append(
            "Enter an account or opportunity name."
        )

    if not situation:
        errors.append(
            "Describe what is happening."
        )

    return errors


def _build_case_input() -> dict[str, Any]:
    decision_date = st.session_state.get(
        "case_decision_date",
        date.today(),
    )

    if hasattr(decision_date, "isoformat"):
        decision_date_value = decision_date.isoformat()
    else:
        decision_date_value = str(decision_date)

    return {
        "account_name": str(
            st.session_state.get(
                "case_account_name",
                "",
            )
        ).strip(),
        "deal_stage": st.session_state.get(
            "case_deal_stage",
            DEAL_STAGES[0],
        ),
        "revenue_impact": st.session_state.get(
            "case_revenue_impact",
            0.0,
        ),
        "decision_date": decision_date_value,
        "situation": str(
            st.session_state.get(
                "case_situation",
                "",
            )
        ).strip(),
        "evidence": str(
            st.session_state.get(
                "case_evidence",
                "",
            )
        ).strip(),
    }


def _review_information() -> None:
    errors = _validate_input()

    if errors:
        for error in errors:
            st.error(error)
        return

    case_input = _build_case_input()

    try:
        with st.spinner(
            "Reviewing the information and identifying important gaps..."
        ):
            questions = generate_discovery_questions(
                case_input
            )

    except Exception as exc:
        st.error(
            "ValueBridge could not review the information: "
            f"{exc}"
        )
        return

    st.session_state.discovery_questions = questions
    st.session_state.business_case_stage = (
        "discovery"
        if questions
        else "ready"
    )

    for question in questions:
        answer_key = (
            f"discovery_answer_{question['id']}"
        )

        if answer_key not in st.session_state:
            st.session_state[answer_key] = ""

    st.rerun()


def _build_discovery_answers() -> list[dict[str, str]]:
    answers: list[dict[str, str]] = []

    for question in st.session_state.get(
        "discovery_questions",
        [],
    ):
        question_id = question.get(
            "id",
            "",
        )

        answer = str(
            st.session_state.get(
                f"discovery_answer_{question_id}",
                "",
            )
        ).strip()

        answers.append(
            {
                "id": question_id,
                "question": question.get(
                    "question",
                    "",
                ),
                "answer": (
                    answer
                    if answer
                    else "Not yet confirmed"
                ),
            }
        )

    return answers


def _generate_case() -> None:
    errors = _validate_input()

    if errors:
        for error in errors:
            st.error(error)
        return

    case_input = _build_case_input()
    case_input["discovery_answers"] = (
        _build_discovery_answers()
    )

    try:
        with st.spinner(
            "Creating the business case..."
        ):
            generated_case = analyze_business_case(
                case_input
            )

    except Exception as exc:
        st.error(
            "ValueBridge could not generate the business case: "
            f"{exc}"
        )
        return

    if not isinstance(generated_case, dict):
        st.error(
            "ValueBridge returned an invalid business case."
        )
        return

    st.session_state.generated_case = generated_case
    st.session_state.business_case_generated = True
    st.session_state.business_case_saved = False
    st.session_state.business_case_id = None
    st.session_state.business_case_stage = "output"
    st.session_state.business_case_pdf = None
    st.session_state.business_case_pdf_name = None

    for field_name, _, _ in OUTPUT_FIELDS:
        value = generated_case.get(
            field_name,
            "",
        )

        if isinstance(value, list):
            value = "\n".join(
                f"- {item}"
                for item in value
            )

        st.session_state[
            f"edit_{field_name}"
        ] = str(value).strip()

    st.rerun()


def _get_edited_output() -> dict[str, str]:
    return {
        field_name: str(
            st.session_state.get(
                f"edit_{field_name}",
                "",
            )
        ).strip()
        for field_name, _, _ in OUTPUT_FIELDS
    }


def _validate_output(
    edited_output: dict[str, str],
) -> list[str]:
    required_sections = {
        "executive_summary": "Executive Summary",
        "customer_need": "Customer Need",
        "business_impact": "Business Impact",
        "recommended_stakeholder": (
            "Recommended Stakeholder"
        ),
        "recommended_approach": (
            "Recommended Approach"
        ),
    }

    errors: list[str] = []

    for field_name, label in required_sections.items():
        if not edited_output.get(
            field_name,
            "",
        ).strip():
            errors.append(
                f"{label} cannot be empty."
            )

    return errors


def _build_record(
    edited_output: dict[str, str],
) -> dict[str, Any]:
    case_input = _build_case_input()
    discovery_answers = (
        _build_discovery_answers()
    )

    return {
        "id": st.session_state.get(
            "business_case_id"
        ),
        "request_id": st.session_state.get(
            "business_case_id"
        ),
        **case_input,
        "discovery_questions": (
            st.session_state.get(
                "discovery_questions",
                [],
            )
        ),
        "discovery_answers": discovery_answers,
        "output": edited_output,
        "executive_summary": edited_output[
            "executive_summary"
        ],
        "customer_need": edited_output[
            "customer_need"
        ],
        "business_impact": edited_output[
            "business_impact"
        ],
        "recommended_stakeholder": edited_output[
            "recommended_stakeholder"
        ],
        "recommended_approach": edited_output[
            "recommended_approach"
        ],
        "open_questions": edited_output[
            "open_questions"
        ],
        "status": "Saved",
    }


def _save_case(
    refresh_requests: RefreshCallback = None,
) -> Optional[str]:
    edited_output = _get_edited_output()
    errors = _validate_output(
        edited_output
    )

    if errors:
        for error in errors:
            st.error(error)
        return None

    record = _build_record(
        edited_output
    )

    try:
        case_id = save_request(
            record
        )

    except Exception as exc:
        st.error(
            "ValueBridge could not save the business case: "
            f"{exc}"
        )
        return None

    st.session_state.business_case_id = case_id
    st.session_state.business_case_saved = True

    if callable(refresh_requests):
        try:
            refresh_requests()
        except Exception:
            pass

    return case_id


def _safe_pdf_text(
    value: Any,
) -> str:
    text = str(
        value or ""
    ).strip()

    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new,
        )

    return text.replace(
        "\n",
        "<br/>",
    )


def _create_pdf_filename() -> str:
    case_title = str(
        st.session_state.get(
            "case_account_name",
            "Business Case",
        )
    ).strip()

    safe_title = "".join(
        character
        if character.isalnum()
        or character in {"-", "_"}
        else "_"
        for character in case_title
    )

    safe_title = "_".join(
        part
        for part in safe_title.split("_")
        if part
    )

    return (
        f"{safe_title or 'Business_Case'}"
        "_ValueBridge_Briefing.pdf"
    )


def _create_pdf(
    edited_output: dict[str, str],
) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="ValueBridge Business Case Briefing",
        author="ValueBridge",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ValueBridgeTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor=colors.HexColor(
            "#17324D"
        ),
    )

    subtitle_style = ParagraphStyle(
        "ValueBridgeSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        spaceAfter=18,
        textColor=colors.HexColor(
            "#5B6770"
        ),
    )

    section_style = ParagraphStyle(
        "ValueBridgeSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor(
            "#17324D"
        ),
    )

    body_style = ParagraphStyle(
        "ValueBridgeBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        spaceAfter=8,
        textColor=colors.HexColor(
            "#202A33"
        ),
    )

    small_style = ParagraphStyle(
        "ValueBridgeSmall",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(
            "#5B6770"
        ),
    )

    case_title = st.session_state.get(
        "case_account_name",
        "Untitled Business Case",
    )

    revenue = st.session_state.get(
        "case_revenue_impact",
        0.0,
    )

    try:
        revenue_display = (
            f"${float(revenue):,.0f}"
            if float(revenue) > 0
            else "Not yet confirmed"
        )
    except (TypeError, ValueError):
        revenue_display = (
            "Not yet confirmed"
        )

    decision_date = st.session_state.get(
        "case_decision_date",
    )

    if hasattr(
        decision_date,
        "strftime",
    ):
        date_display = (
            decision_date.strftime(
                "%B %d, %Y"
            )
        )
    else:
        date_display = (
            "Not yet confirmed"
        )

    story = [
        Paragraph(
            "ValueBridge Business Case Briefing",
            title_style,
        ),
        Paragraph(
            _safe_pdf_text(
                case_title
            ),
            subtitle_style,
        ),
    ]

    metadata = [
        [
            Paragraph(
                "<b>Deal Stage</b>",
                small_style,
            ),
            Paragraph(
                "<b>Revenue Influenced</b>",
                small_style,
            ),
            Paragraph(
                "<b>Decision Date</b>",
                small_style,
            ),
        ],
        [
            Paragraph(
                _safe_pdf_text(
                    st.session_state.get(
                        "case_deal_stage",
                        "Not yet confirmed",
                    )
                ),
                body_style,
            ),
            Paragraph(
                _safe_pdf_text(
                    revenue_display
                ),
                body_style,
            ),
            Paragraph(
                _safe_pdf_text(
                    date_display
                ),
                body_style,
            ),
        ],
    ]

    metadata_table = Table(
        metadata,
        colWidths=[
            2.1 * inch,
            1.8 * inch,
            2.2 * inch,
        ],
        hAlign="CENTER",
    )

    metadata_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#EEF3F7"
                    ),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#C8D2DA"
                    ),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#D8E0E6"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.extend(
        [
            metadata_table,
            Spacer(
                1,
                14,
            ),
        ]
    )

    for (
        field_name,
        title,
        _,
    ) in OUTPUT_FIELDS:
        story.append(
            Paragraph(
                _safe_pdf_text(
                    title
                ),
                section_style,
            )
        )

        story.append(
            Paragraph(
                _safe_pdf_text(
                    edited_output.get(
                        field_name,
                        "",
                    )
                    or "Not yet confirmed."
                ),
                body_style,
            )
        )

    discovery_answers = (
        _build_discovery_answers()
    )

    situation = st.session_state.get(
        "case_situation",
        "",
    )

    evidence = st.session_state.get(
        "case_evidence",
        "",
    )

    if (
        situation
        or evidence
        or discovery_answers
    ):
        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "Source Information",
                title_style,
            )
        )

        if situation:
            story.append(
                Paragraph(
                    "Original Sales Situation",
                    section_style,
                )
            )

            story.append(
                Paragraph(
                    _safe_pdf_text(
                        situation
                    ),
                    body_style,
                )
            )

        if evidence:
            story.append(
                Paragraph(
                    "Evidence and Additional Context",
                    section_style,
                )
            )

            story.append(
                Paragraph(
                    _safe_pdf_text(
                        evidence
                    ),
                    body_style,
                )
            )

        if discovery_answers:
            story.append(
                Paragraph(
                    "Discovery Responses",
                    section_style,
                )
            )

            for item in discovery_answers:
                story.append(
                    Paragraph(
                        (
                            f"<b>{_safe_pdf_text(item['question'])}</b>"
                            f"<br/>{_safe_pdf_text(item['answer'])}"
                        ),
                        body_style,
                    )
                )

    document.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


def _save_and_create_pdf(
    refresh_requests: RefreshCallback = None,
) -> None:
    edited_output = _get_edited_output()
    errors = _validate_output(
        edited_output
    )

    if errors:
        for error in errors:
            st.error(error)
        return

    case_id = _save_case(
        refresh_requests
    )

    if not case_id:
        return

    try:
        pdf_bytes = _create_pdf(
            edited_output
        )

    except Exception as exc:
        st.error(
            "ValueBridge could not create the PDF briefing: "
            f"{exc}"
        )
        return

    st.session_state.business_case_pdf = (
        pdf_bytes
    )

    st.session_state.business_case_pdf_name = (
        _create_pdf_filename()
    )


def _render_progress() -> None:
    current_stage = st.session_state.get(
        "business_case_stage",
        "input",
    )

    active_step = {
        "input": 1,
        "discovery": 2,
        "ready": 2,
        "output": 3,
    }.get(
        current_stage,
        1,
    )

    if st.session_state.get(
        "business_case_saved",
        False,
    ):
        active_step = 4

    steps = [
        "Describe Situation",
        "Complete Discovery",
        "Review Business Case",
        "Save & Create PDF",
    ]

    columns = st.columns(
        4
    )

    for index, (
        label,
        column,
    ) in enumerate(
        zip(
            steps,
            columns,
        ),
        start=1,
    ):
        with column:
            if index <= active_step:
                st.markdown(
                    f"**{index}. {label}**"
                )
            else:
                st.caption(
                    f"{index}. {label}"
                )


def _render_input_form() -> None:
    with st.container(
        border=True
    ):
        st.subheader(
            "Describe the Sales Situation"
        )

        st.write(
            "Start with what you know. ValueBridge will review the "
            "information and ask only the questions needed to build a "
            "more complete business case."
        )

        row_one = st.columns(
            [1.4, 1]
        )

        with row_one[0]:
            st.text_input(
                "Account or opportunity",
                key="case_account_name",
                placeholder=(
                    "Example: Summit Automotive Group"
                ),
            )

        with row_one[1]:
            st.selectbox(
                "Deal stage",
                options=DEAL_STAGES,
                key="case_deal_stage",
            )

        row_two = st.columns(
            2
        )

        with row_two[0]:
            st.number_input(
                "Revenue influenced",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key="case_revenue_impact",
                help=(
                    "Leave this at zero when the amount has not yet been confirmed."
                ),
            )

        with row_two[1]:
            st.date_input(
                "Target decision or close date",
                key="case_decision_date",
            )

        st.text_area(
            "What is happening?",
            key="case_situation",
            height=180,
            placeholder=(
                "Describe the customer request, business challenge, "
                "deal obstacle, desired capability, or concern."
            ),
        )

        st.text_area(
            "What evidence or context do you already have?",
            key="case_evidence",
            height=130,
            placeholder=(
                "Add customer comments, metrics, deadlines, competitive "
                "pressure, current workarounds, or known constraints."
            ),
        )

        if st.button(
            "Review Information",
            type="primary",
            use_container_width=True,
        ):
            _review_information()


def _render_discovery() -> None:
    st.subheader(
        "Complete the Picture"
    )

    st.write(
        "Answer what you know. Questions may be left blank when the "
        "information has not yet been confirmed."
    )

    questions = st.session_state.get(
        "discovery_questions",
        [],
    )

    if not questions:
        with st.container(
            border=True
        ):
            st.success(
                "The information provided is sufficient to create the draft."
            )

    for number, question in enumerate(
        questions,
        start=1,
    ):
        question_id = question.get(
            "id",
            f"question_{number}",
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### {number}. {question.get('question', '')}"
            )

            reason = question.get(
                "reason",
                "",
            )

            if reason:
                st.caption(
                    reason
                )

            st.text_area(
                "Response",
                key=(
                    f"discovery_answer_{question_id}"
                ),
                placeholder=question.get(
                    "placeholder",
                    "Enter what is known, or leave blank if not yet confirmed.",
                ),
                height=110,
                label_visibility="collapsed",
            )

    if st.button(
        "Create Business Case",
        type="primary",
        use_container_width=True,
    ):
        _generate_case()


def _render_case_header() -> None:
    with st.container(
        border=True
    ):
        left, right = st.columns(
            [2, 1]
        )

        with left:
            st.caption(
                "BUSINESS CASE DRAFT"
            )

            st.subheader(
                st.session_state.get(
                    "case_account_name",
                    "Untitled Business Case",
                )
            )

            st.write(
                f"**Deal stage:** "
                f"{st.session_state.get('case_deal_stage', 'Not provided')}"
            )

        with right:
            revenue = st.session_state.get(
                "case_revenue_impact",
                0.0,
            )

            try:
                revenue_number = float(
                    revenue
                )

                revenue_display = (
                    f"${revenue_number:,.0f}"
                    if revenue_number > 0
                    else "Not confirmed"
                )

            except (
                TypeError,
                ValueError,
            ):
                revenue_display = (
                    "Not confirmed"
                )

            st.metric(
                "Revenue influenced",
                revenue_display,
            )

            decision_date = st.session_state.get(
                "case_decision_date",
            )

            if hasattr(
                decision_date,
                "strftime",
            ):
                date_display = (
                    decision_date.strftime(
                        "%B %d, %Y"
                    )
                )
            else:
                date_display = (
                    "Not confirmed"
                )

            st.write(
                f"**Decision date:** {date_display}"
            )


def _render_editable_section(
    field_name: str,
    title: str,
    description: str,
) -> None:
    with st.container(
        border=True
    ):
        st.markdown(
            f"### {title}"
        )

        st.caption(
            description
        )

        height = 170

        if field_name == "executive_summary":
            height = 150

        elif field_name in {
            "recommended_stakeholder",
            "open_questions",
        }:
            height = 140

        state_key = (
            f"edit_{field_name}"
        )

        if state_key not in st.session_state:
            generated_case = (
                st.session_state.get(
                    "generated_case",
                    {},
                )
            )

            st.session_state[state_key] = str(
                generated_case.get(
                    field_name,
                    "",
                )
            )

        st.text_area(
            title,
            key=state_key,
            height=height,
            label_visibility="collapsed",
        )


def _render_output(
    refresh_requests: RefreshCallback = None,
) -> None:
    _render_case_header()

    st.divider()

    st.subheader(
        "Review and Edit"
    )

    st.write(
        "Review the generated business case and revise any section "
        "before saving the final briefing."
    )

    for (
        field_name,
        title,
        description,
    ) in OUTPUT_FIELDS:
        _render_editable_section(
            field_name,
            title,
            description,
        )

    if st.button(
        "Save & Create PDF",
        type="primary",
        use_container_width=True,
    ):
        _save_and_create_pdf(
            refresh_requests
        )

    pdf_bytes = st.session_state.get(
        "business_case_pdf"
    )

    pdf_name = st.session_state.get(
        "business_case_pdf_name"
    )

    if pdf_bytes and pdf_name:
        st.success(
            "The business case was saved and the PDF briefing is ready."
        )

        st.download_button(
            label="Download PDF Briefing",
            data=pdf_bytes,
            file_name=pdf_name,
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )


def render_business_case(
    refresh_requests: RefreshCallback = None,
    **_: Any,
) -> None:
    _initialize_state()

    st.title(
        "Business Case"
    )

    st.caption(
        "Turn customer needs and commercial priorities into a formal, "
        "decision-ready internal business case."
    )

    _render_progress()

    st.divider()

    stage = st.session_state.get(
        "business_case_stage",
        "input",
    )

    if stage == "input":
        _render_input_form()
        return

    if stage in {
        "discovery",
        "ready",
    }:
        _render_discovery()
        return

    _render_output(
        refresh_requests
    )
