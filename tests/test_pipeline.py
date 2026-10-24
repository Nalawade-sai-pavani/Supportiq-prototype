from src.redact import redact
from src.pipeline import SupportIQ

def test_redaction():
    out = redact("mail me at jane@example.com about order #4821, phone +91 98765 43210")
    assert "jane@example.com" not in out and "#4821" not in out and "98765" not in out

def test_damaged_item_gets_cited_reply():
    r = SupportIQ().handle("my order #1234 arrived damaged and broken")
    assert r["intent"] == "damaged_item" and r["action"] == "SUGGEST_REPLY"
    assert "KB1" in r["sources"]

def test_off_topic_escalates():
    r = SupportIQ().handle("what is the weather like on mars")
    assert r["action"] == "ESCALATE"
