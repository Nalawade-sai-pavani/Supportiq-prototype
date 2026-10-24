# SupportIQ - AI-Assisted Customer Support (Prototype)

Pipeline: PII redaction -> intent/priority classifier -> confidence gate -> policy retrieval -> grounded reply with citations -> human review.

## Run
    python -m venv .venv
    .venv\Scripts\activate          (Windows)   |   source .venv/bin/activate  (Mac/Linux)
    pip install -r requirements.txt
    python make_data.py             # synthetic dataset
    python -m src.classifier        # train model
    pytest -q                       # tests
    streamlit run app.py            # agent console

Data is synthetic. No real customer information is used.
