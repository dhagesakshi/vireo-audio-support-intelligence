from pathlib import Path
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_DIR = Path(__file__).resolve().parents[1] / "outputs"
MODEL_PATH = MODEL_DIR / "ticket_category_model.joblib"

def build_model():
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.98,
            sublinear_tf=True
        )),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ])

def train_model(df: pd.DataFrame):
    model = build_model()
    text = df["customer_message"].fillna("").astype(str)
    model.fit(text, df["category"])
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model

def predict_with_confidence(model, texts):
    probabilities = model.predict_proba(texts)
    labels = model.classes_
    idx = probabilities.argmax(axis=1)
    return (
        labels[idx],
        probabilities.max(axis=1)
    )
