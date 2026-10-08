# ValueBridge

ValueBridge is a Streamlit application designed for the  to help bridge communication gaps between Sales, dealer-facing teams, Operations, and technical stakeholders.

The app guides users through defining the problem, measuring the business impact, selecting the right stakeholder, and preparing a meeting brief.

## Status

ValueBridge is currently an MVP and continues to be refined based on workflow and user feedback.

## What it does

- Captures dealer, member, payment, operational, and compliance requests
- Connects requests to business outcomes and measurable impact
- Provides stakeholder-specific guidance
- Creates a clear request summary and meeting brief
- Stores requests in Google Firestore, with a local fallback for development

## Built with

- Python
- Streamlit
- Google Cloud Firestore
- Google Cloud Run

## Run locally

```bash
cd ~/dev-projects/valuebridge
source venv/bin/activate
streamlit run app.py


app.py            Main Streamlit application
database.py       Firestore and local storage functions
requirements.txt  Python dependencies
Dockerfile        Cloud Run container setup
.dockerignore     Files excluded from the container
