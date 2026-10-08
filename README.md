# Bima Saathi

Hinglish WhatsApp AI Assistant for Insurance, with Tool Calling, Action Verification, and an Evaluation and Analytics Layer.

## Features
- **Multilingual Support**: English, Hindi, and Hinglish with language detection.
- **Action Verifier Guardrail**: Strictly verifies LLM tool claims to prevent hallucinations.
- **Mock Services**: Includes a local mock CRM, Pricing, and Claims API.
- **LLM Orchestration**: Tool calling loop integrated with Groq/OpenAI.
- **Analytics Dashboard**: Streamlit application to visualize tool errors and the conversation funnel.

## Setup
1. Create a virtual environment: `python3 -m venv .venv`
2. Activate it: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Setup `.env` using `.env.example` as a template (make sure to add your Groq API key).

## Running the app
1. Start the mock services: `uvicorn mock_services.main:app --port 8100`
2. Run manual tests: `python test_manual.py`
3. Launch dashboard: `streamlit run dashboard/app.py`
