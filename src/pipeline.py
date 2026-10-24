"""Orchestrator: redact -> classify -> confidence gate -> retrieve -> draft -> guardrail."""
import os
from . import classifier
from .redact import redact
from .retriever import Retriever
from .drafter import draft

THRESHOLD = 0.45  # tune during testing

class SupportIQ:
    def __init__(self):
        if not os.path.exists(classifier.MODEL_PATH):
            classifier.train()
        self.model = classifier.load()
        self.retriever = Retriever()

    def handle(self, raw_text: str) -> dict:
        text = redact(raw_text)
        intent, conf, priority = classifier.predict(self.model, text)
        result = {"masked_text": text, "intent": intent, "confidence": conf,
                  "priority": priority, "action": "ESCALATE", "reply": None, "sources": []}
        if conf < THRESHOLD:
            result["reason"] = "Low confidence: routed to human agent"
            return result
        passages = self.retriever.search(text)
        reply = draft(intent, passages)
        if reply is None:
            result["reason"] = "No supporting policy found: routed to human agent"
            return result
        result.update(action="SUGGEST_REPLY", reply=reply, sources=[p["id"] for p in passages])
        return result
