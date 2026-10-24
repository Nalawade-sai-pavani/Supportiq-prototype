"""Step 5: agent console prototype. Run: streamlit run app.py"""
import csv, os, datetime
import streamlit as st
from src.pipeline import SupportIQ

st.set_page_config(page_title="SupportIQ", layout="wide")

@st.cache_resource
def get_engine():
    return SupportIQ()

engine = get_engine()
st.title("SupportIQ - Agent Console (Prototype)")

SAMPLES = ["My order #4821 arrived damaged, my email is jane@example.com",
           "Where is my parcel? It is 5 days late",
           "I forgot my password and cannot log in",
           "Can you recommend a good laptop?"]
sample = st.selectbox("Load a sample ticket (optional)", [""] + SAMPLES)
msg = st.text_area("Customer message", value=sample, height=110)

if st.button("Analyse ticket") and msg.strip():
    st.session_state["res"] = engine.handle(msg)

res = st.session_state.get("res")
if res:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Masked message")
        st.info(res["masked_text"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Intent", res["intent"])
        c2.metric("Confidence", f"{res['confidence']:.0%}")
        c3.metric("Priority", res["priority"])
        if res["action"] == "SUGGEST_REPLY":
            st.subheader("AI-suggested reply (editable)")
            final = st.text_area("Reply", res["reply"], height=200, key="reply")
            b1, b2, b3 = st.columns(3)
            def log(decision):
                os.makedirs("data", exist_ok=True)
                with open("data/feedback.csv", "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([datetime.datetime.now().isoformat(), res["masked_text"],
                                            res["intent"], decision, final])
            if b1.button("Approve & send"): log("approved"); st.success("Sent and logged.")
            if b2.button("Edit saved"): log("edited"); st.success("Edit logged as feedback.")
            if b3.button("Escalate"): log("escalated"); st.warning("Escalated to senior agent.")
        else:
            st.error("Escalated to human agent: " + res.get("reason", ""))
    with right:
        st.subheader("Sources")
        for pid in res["sources"] or ["none"]:
            st.write(pid)
