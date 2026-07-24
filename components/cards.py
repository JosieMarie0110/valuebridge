"""
Reusable Streamlit card wrappers.
"""

from __future__ import annotations

import html

import streamlit as st


def card_open(
    title: str,
    subtitle: str = "",
    *,
    css_class: str = "",
) -> None:
    """Open a styled content card."""

    safe_title = html.escape(str(title or ""))
    safe_subtitle = html.escape(str(subtitle or ""))
    extra_class = f" {css_class.strip()}" if css_class.strip() else ""

    subtitle_html = ""

    if safe_subtitle:
        subtitle_html = (
            f'<div class="app-card-subtitle">{safe_subtitle}</div>'
        )

    st.markdown(
        f"""
        <div class="app-card{extra_class}">
            <div class="app-card-header">
                <div class="app-card-title">{safe_title}</div>
                {subtitle_html}
            </div>
            <div class="app-card-body">
        """,
        unsafe_allow_html=True,
    )


def card_close() -> None:
    """Close a styled content card."""

    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(
    title: str,
    subtitle: str = "",
) -> None:
    """Render a page section heading."""

    safe_title = html.escape(str(title or ""))
    safe_subtitle = html.escape(str(subtitle or ""))

    subtitle_html = ""

    if safe_subtitle:
        subtitle_html = (
            f'<div class="section-subtitle">{safe_subtitle}</div>'
        )

    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">{safe_title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_card(
    label: str,
    value: str,
    description: str = "",
) -> None:
    """Render a compact dashboard status card."""

    safe_label = html.escape(str(label or ""))
    safe_value = html.escape(str(value or ""))
    safe_description = html.escape(str(description or ""))

    description_html = ""

    if safe_description:
        description_html = (
            f'<div class="status-card-description">'
            f"{safe_description}"
            f"</div>"
        )

    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-card-label">{safe_label}</div>
            <div class="status-card-value">{safe_value}</div>
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def notice_box(
    message: str,
    *,
    kind: str = "info",
) -> None:
    """Render a custom notice box."""

    allowed_kinds = {
        "info",
        "success",
        "warning",
        "error",
    }

    selected_kind = (
        kind if kind in allowed_kinds else "info"
    )

    safe_message = html.escape(str(message or ""))

    st.markdown(
        f"""
        <div class="notice-box notice-{selected_kind}">
            {safe_message}
        </div>
        """,
        unsafe_allow_html=True,
    )
