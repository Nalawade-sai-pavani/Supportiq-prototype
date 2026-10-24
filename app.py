"""SupportIQ prototype with customer portal + agent console.
Run: streamlit run app.py"""
import csv, os, datetime, hmac
import streamlit as st
from src.pipeline import SupportIQ
from src import store

st.set_page_config(page_title="SupportIQ", layout="wide")

# ---------- accounts ----------
DEFAULT_AGENTS = {"agent1": "agent123", "admin": "admin123"}       # demo only
DEFAULT_CUSTOMERS = {"customer1": "cust123"}                        # demo only


def secret_table(name, default):
    try:
        return dict(st.secrets[name])
    except Exception:
        return default


AGENTS = secret_table("agents", DEFAULT_AGENTS)
BUILTIN_CUSTOMERS = secret_table("customers", DEFAULT_CUSTOMERS)


@st.cache_resource
def get_engine():
    return SupportIQ()


def login_page():
    st.title("SupportIQ")
    tab_c, tab_s, tab_a = st.tabs(["Customer login", "Customer sign up", "Agent login"])
    with tab_c:
        u = st.text_input("Username", key="cu")
        p = st.text_input("Password", type="password", key="cp")
        if st.button("Log in", key="cb"):
            if store.verify_customer(u, p, BUILTIN_CUSTOMERS):
                st.session_state.update(user=u.strip().lower(), role="customer")
                st.rerun()
            else:
                st.error("Invalid username or password")
        st.caption("Demo customer: customer1 / cust123")
    with tab_s:
        u = st.text_input("Choose a username", key="su")
        p = st.text_input("Choose a password (6+ characters)", type="password", key="sp")
        if st.button("Create account", key="sb"):
            ok, msg = store.register_customer(u, p)
            (st.success if ok else st.error)(msg)
    with tab_a:
        u = st.text_input("Agent username", key="au")
        p = st.text_input("Agent password", type="password", key="ap")
        if st.button("Agent log in", key="ab"):
            if u.strip() in AGENTS and hmac.compare_digest(str(AGENTS[u.strip()]), p):
                st.session_state.update(user=u.strip(), role="agent")
                st.rerun()
            else:
                st.error("Invalid agent credentials")
        st.caption("Demo agent: agent1 / agent123")


# ---------- customer portal ----------
STATUS_ICON = {"Open": "🟡 Received - waiting for an agent", "Escalated": "🟠 With a senior agent",
               "Replied": "🟢 Answered"}


def customer_view(user):
    st.title("Customer Support")
    st.write(f"Welcome, **{user}**. Tell us how we can help.")
    tab_new, tab_my = st.tabs(["New request", "My requests"])
    with tab_new:
        with st.form("new_request", clear_on_submit=True):
            msg = st.text_area("Describe your issue (please avoid sharing card numbers or passwords)",
                               height=140)
            sent = st.form_submit_button("Submit request")
        if sent:
            if not msg.strip():
                st.warning("Please type your message first.")
            else:
                res = get_engine().handle(msg)
                tid = store.add_ticket(user, msg, res)
                st.success(f"Request #{tid} received. An agent will reply here shortly.")
    with tab_my:
        mine = sorted(store.list_tickets(user), key=lambda t: t["id"], reverse=True)
        if not mine:
            st.info("You have no requests yet.")
        for t in mine:
            with st.expander(f"#{t['id']} - {STATUS_ICON.get(t['status'], t['status'])}"):
                st.write("**Your message:**", t["raw_text"])
                if t["reply"]:
                    st.write("**Reply:**")
                    st.success(t["reply"])
                else:
                    st.caption("No reply yet. Refresh this page later.")


# ---------- agent console ----------
def log_feedback(user, t, decision, final):
    os.makedirs("data", exist_ok=True)
    with open("data/feedback.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.datetime.now().isoformat(), user, t["id"],
                                t["masked_text"], t["intent"], decision, final])


def agent_view(user):
    st.title("SupportIQ - Agent Console")
    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    open_t = [t for t in store.list_tickets() if t["status"] in ("Open", "Escalated")]
    open_t.sort(key=lambda t: (order.get(t["priority"], 1), t["id"]))
    st.subheader(f"Queue: {len(open_t)} open")
    if not open_t:
        st.info("No open tickets. New customer requests will appear here.")
    else:
        labels = {f"#{t['id']} | {t['priority']} | {t['intent']} | {t['status']}": t for t in open_t}
        t = labels[st.selectbox("Select a ticket", list(labels))]
        left, right = st.columns([2, 1])
        with left:
            st.markdown("**Customer message (personal data masked)**")
            st.info(t["masked_text"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Intent", t["intent"])
            c2.metric("Confidence", f"{t['confidence']:.0%}")
            c3.metric("Priority", t["priority"])
            if t["draft"]:
                st.markdown("**AI-suggested reply (edit before sending)**")
            else:
                st.warning(t["reason"] or "No AI draft. Please write a reply.")
            final = st.text_area("Reply to customer", t["draft"] or "", height=200, key=f"r{t['id']}")
            b1, b2 = st.columns(2)
            if b1.button("Send reply", key=f"s{t['id']}"):
                if not final.strip():
                    st.error("Reply cannot be empty.")
                else:
                    decision = "approved" if final == t["draft"] else "edited"
                    log_feedback(user, t, decision, final)
                    store.update_ticket(t["id"], status="Replied", reply=final, agent=user,
                                        replied_at=datetime.datetime.now().isoformat(timespec="seconds"))
                    st.session_state["flash"] = f"Reply sent for #{t['id']} ({decision})."
                    st.rerun()
            if b2.button("Escalate", key=f"e{t['id']}"):
                log_feedback(user, t, "escalated", final)
                store.update_ticket(t["id"], status="Escalated")
                st.session_state["flash"] = f"#{t['id']} escalated."
                st.rerun()
        with right:
            st.markdown("**Sources**")
            for s in t["sources"] or ["none"]:
                st.write(s)
    done = [t for t in store.list_tickets() if t["status"] == "Replied"]
    with st.expander(f"Answered tickets ({len(done)})"):
        for t in sorted(done, key=lambda x: x["id"], reverse=True):
            st.write(f"#{t['id']} by {t['agent']}: {t['reply'][:120]}")


# ---------- router ----------
if st.session_state.get("role") is None:
    login_page()
    st.stop()

user, role = st.session_state["user"], st.session_state["role"]
st.sidebar.write(f"Logged in as **{user}** ({role})")
if st.sidebar.button("Log out"):
    st.session_state.clear()
    st.rerun()

if role == "customer":
    customer_view(user)
else:
    agent_view(user)