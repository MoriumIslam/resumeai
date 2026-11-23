import joblib
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

model = joblib.load("model/resume_classifier.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")
label_encoder = joblib.load("model/label_encoder.pkl")

def predict_category(text):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)
    return label_encoder.inverse_transform(pred)[0], vec