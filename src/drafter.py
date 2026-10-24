"""Step 4: draft a grounded reply using ONLY retrieved passages, with citations.
Template-based so the prototype runs offline; swap draft() for an LLM call later."""
OPENERS = {
    "damaged_item": "I'm sorry your item arrived damaged.",
    "refund": "Thanks for contacting us about your refund.",
    "delivery_delay": "I'm sorry your order is taking longer than expected.",
    "password_reset": "Happy to help you get back into your account.",
    "invoice": "Thanks for your invoice request.",
    "cancel_order": "Thanks for letting us know you'd like to cancel.",
}

def draft(intent, passages):
    if not passages:
        return None  # nothing to ground on -> refuse and escalate
    body = passages[0]["text"]
    cites = ", ".join(f"[{p['id']}] {p['title']}" for p in passages)
    return f"{OPENERS.get(intent, 'Thanks for reaching out.')} {body}\n\nSources: {cites}"
