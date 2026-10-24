"""Generate a small SYNTHETIC ticket dataset (no real customer data)."""
import random, pandas as pd
random.seed(42)
T = {
 "refund": ["I want a refund for my order {o}", "please refund me, I returned the item", "how do I get my money back for order {o}", "I would like to return this and get a refund", "refund request for {o} please"],
 "damaged_item": ["my order {o} arrived damaged", "the item is broken when it arrived", "package was crushed and the product is cracked", "I received a defective product, it does not work", "item arrived smashed, I need a replacement"],
 "delivery_delay": ["where is my order {o}, it is late", "my parcel has not arrived yet", "delivery is delayed, tracking has not updated", "it has been a week and nothing arrived", "when will my package be delivered"],
 "password_reset": ["I forgot my password", "cannot log in to my account, need to reset password", "reset link not working for my login", "how do I change my password", "locked out of my account"],
 "invoice": ["I need an invoice for order {o}", "where can I download my invoice", "please correct the tax number on my invoice", "billing name is wrong on my receipt", "send me the PDF invoice"],
 "cancel_order": ["please cancel my order {o}", "I want to cancel the order I just placed", "cancel my purchase before it ships", "ordered by mistake, how to cancel", "stop my order from being shipped"],
}
PRE = ["", "Hi, ", "Hello, ", "Hey team, ", "Good morning, "]
POST = ["", " Thanks.", " Please help!", " Thank you.", " Urgent."]
rows = []
for intent, tpls in T.items():
    for _ in range(60):
        t = random.choice(tpls).format(o=f"#{random.randint(1000,9999)}")
        rows.append((random.choice(PRE) + t + random.choice(POST), intent))
random.shuffle(rows)
pd.DataFrame(rows, columns=["text", "intent"]).to_csv("data/tickets.csv", index=False)
print(len(rows), "rows written to data/tickets.csv")
