# SupportIQ - AI-Assisted Customer Support (Prototype)
**DEMO LINK**:https://supportiq-prototype-gmzpytga9cw8pbzfcmwicd.streamlit.app/

**AGENT LOGIN**
USER NAME :agent1
PASSWORD:agent123
**CUSTOMER LOGIN  DEMO**
USER NAME:customer1
PASSWORD:cust123


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
