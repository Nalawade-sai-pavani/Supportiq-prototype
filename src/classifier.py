"""Step 2: intent classifier (TF-IDF + Logistic Regression) with confidence score."""
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

MODEL_PATH = "models/intent_model.joblib"
PRIORITY = {"damaged_item": "HIGH", "refund": "HIGH", "delivery_delay": "MEDIUM",
            "invoice": "MEDIUM", "cancel_order": "MEDIUM", "password_reset": "LOW"}


def train(csv="data/tickets.csv", path=MODEL_PATH):
    df = pd.read_csv(csv)
    X_tr, X_te, y_tr, y_te = train_test_split(df.text, df.intent, test_size=0.2,
                                              random_state=42, stratify=df.intent)
    model = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
                      ("clf", LogisticRegression(max_iter=1000))])
    model.fit(X_tr, y_tr)
    print(classification_report(y_te, model.predict(X_te)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    return model


def load(path=MODEL_PATH):
    return joblib.load(path)


def predict(model, text):
    probs = model.predict_proba([text])[0]
    i = probs.argmax()
    return model.classes_[i], float(probs[i]), PRIORITY.get(model.classes_[i], "MEDIUM")


if __name__ == "__main__":
    train()