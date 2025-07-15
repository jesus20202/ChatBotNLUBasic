from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib
import os
from .training_data import TrainingDataset

class MLIntentClassifier:

    spanish_stopwords = [
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus", "ellas", "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías", "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "esos", "esas", "estoy", "estás", "está", "estamos", "estáis", "están", "esté", "estés", "estemos", "estéis", "estén", "estaré", "estarás", "estará", "estaremos", "estaréis", "estarán", "estaría", "estarías", "estaríamos", "estaríais", "estarían", "estaba", "estabas", "estábamos", "estabais", "estaban", "estuve", "estuviste", "estuvo", "estuvimos", "estuvisteis", "estuvieron", "estuviera", "estuvieras", "estuviéramos", "estuvierais", "estuvieran", "estuviese", "estuvieses", "estuviésemos", "estuvieseis", "estuviesen", "estando", "estado", "estada", "estados", "estadas", "estad"
    ]

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words=MLIntentClassifier.spanish_stopwords,
            lowercase=True,
            strip_accents='unicode'
        )
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            ),
            'logistic': LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced'
            ),
            'svm': SVC(
                probability=True,
                random_state=42,
                class_weight='balanced'
            )
        }
        self.best_model = None
        self.model_name = None
        self.is_trained = False
        self.model_path = "nlu/trained_model.pkl"
        self.vectorizer_path = "nlu/vectorizer.pkl"

    def train_and_evaluate(self):
        dataset = TrainingDataset()
        texts, labels = dataset.get_training_data()
        X = self.vectorizer.fit_transform(texts)
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        results = {}
        for name, model in self.models.items():
            cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='f1_macro')
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            report = classification_report(y_test, y_pred, output_dict=True)
            results[name] = {
                'model': model,
                'cv_score': cv_scores.mean(),
                'test_accuracy': report['accuracy'],
                'f1_macro': report['macro avg']['f1-score']
            }
        best_name = max(results.keys(), key=lambda x: results[x]['f1_macro'])
        self.best_model = results[best_name]['model']
        self.model_name = best_name
        self.is_trained = True
        self.save_model()
        return results

    def save_model(self):
        if self.is_trained:
            joblib.dump(self.best_model, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)

    def load_model(self):
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            self.best_model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.is_trained = True
            return True
        return False

    def classify(self, text: str) -> tuple[str, float]:
        if not self.is_trained:
            return 'unknown', 0.0
        X = self.vectorizer.transform([text])
        prediction = self.best_model.predict(X)[0]
        probabilities = self.best_model.predict_proba(X)[0]
        confidence = max(probabilities)
        return prediction, confidence

    def get_model_info(self) -> dict:
        if not self.is_trained:
            return {'status': 'not_trained'}
        return {
            'status': 'trained',
            'model_type': self.model_name,
            'features': self.vectorizer.get_feature_names_out()[:10].tolist(),
            'vocab_size': len(self.vectorizer.vocabulary_)
        }