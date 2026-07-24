import streamlit as st


def apply_styles() -> None:
    """Apply the global ValueBridge interface styles."""

    st.html(
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
