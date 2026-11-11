"""
Career Classifier - Logistic Regression based career category prediction
Refactored as a proper class with lazy loading support.
"""
import json
import joblib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from ai.text_preprocessing import preprocess_text

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"
MODEL_VERSION = "1.0.0"

# Technical acronyms to preserve during preprocessing
TECHNICAL_ACRONYMS = {
    "ai", "ml", "dl", "nlp", "cv", "ci", "cd", "cicd", "api", "rest", "graphql",
    "sql", "nosql", "aws", "gcp", "azure", "k8s", "kubernetes", "docker",
    "html", "css", "js", "ts", "jsx", "tsx", "vue", "react", "angular",
    "node", "express", "django", "flask", "fastapi", "spring", "hibernate",
    "jwt", "oauth", "oauth2", "ssl", "tls", "http", "https", "websocket",
    "grpc", "protobuf", "json", "xml", "yaml", "toml", "ini", "csv",
    "etl", "elt", "bi", "etl", "olap", "oltp", "crud", "orm", "mvc",
    "mvp", "mvvm", "tdd", "bdd", "ddd", "microservices", "serverless",
    "devops", "secops", "mlops", "dataops", "gitops", "ci/cd", "sre"
}


class CareerClassifier:
    """
    Career category classifier using TF-IDF + Logistic Regression.

    Provides lazy loading, confidence thresholds, and metadata tracking.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        vectorizer_path: Optional[Path] = None,
        confidence_threshold: float = 0.6,
        max_features: int = 2000,
        ngram_range: tuple = (1, 2),
        random_state: int = 42
    ):
        self.model_path = model_path or (MODELS_DIR / "career_classifier.joblib")
        self.vectorizer_path = vectorizer_path or (MODELS_DIR / "tfidf_vectorizer.joblib")
        self.confidence_threshold = confidence_threshold
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.random_state = random_state

        self._model: Optional[LogisticRegression] = None
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._metadata: Dict[str, Any] = {}
        self._is_loaded = False

    @property
    def model(self) -> LogisticRegression:
        """Lazy load model on first access."""
        if not self._is_loaded:
            self.load()
        return self._model

    @property
    def vectorizer(self) -> TfidfVectorizer:
        """Lazy load vectorizer on first access."""
        if not self._is_loaded:
            self.load()
        return self._vectorizer

    @property
    def is_fitted(self) -> bool:
        """Check if model is fitted."""
        return self._is_loaded and self._model is not None and hasattr(self._model, "classes_")

    @property
    def classes(self) -> List[str]:
        """Get list of career categories."""
        if self.is_fitted:
            return list(self._model.classes_)
        return []

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get model metadata."""
        return self._metadata.copy()

    def load(self) -> bool:
        """
        Load model and vectorizer from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.model_path.exists() and self.vectorizer_path.exists():
                self._model = joblib.load(self.model_path)
                self._vectorizer = joblib.load(self.vectorizer_path)

                # Load metadata if exists
                metadata_path = self.model_path.with_suffix(".json")
                if metadata_path.exists():
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        self._metadata = json.load(f)

                self._is_loaded = True
                logger.info(f"CareerClassifier loaded from {self.model_path}")
                return True
            else:
                logger.warning(f"Model files not found: {self.model_path}, {self.vectorizer_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to load CareerClassifier: {e}")
            self._is_loaded = False
            return False

    def save(self, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save model and vectorizer to disk.

        Args:
            metadata: Additional metadata to save

        Returns:
            True if saved successfully
        """
        try:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)

            joblib.dump(self._model, self.model_path)
            joblib.dump(self._vectorizer, self.vectorizer_path)

            # Save metadata
            meta = {
                "version": MODEL_VERSION,
                "saved_at": datetime.utcnow().isoformat(),
                "model_type": "LogisticRegression",
                "vectorizer_type": "TfidfVectorizer",
                "max_features": self.max_features,
                "ngram_range": self.ngram_range,
                "random_state": self.random_state,
                "confidence_threshold": self.confidence_threshold,
                "classes": self.classes,
            }
            if metadata:
                meta.update(metadata)

            metadata_path = self.model_path.with_suffix(".json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)

            self._metadata = meta
            logger.info(f"CareerClassifier saved to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save CareerClassifier: {e}")
            return False

    def train(
        self,
        data_path: str,
        text_column: str = "Cleaned Text",
        label_column: str = "Career Category",
        test_size: float = 0.2,
        eval_metrics: bool = True
    ) -> Dict[str, float]:
        """
        Train the career classifier.

        Args:
            data_path: Path to CSV training data
            text_column: Column name for text features
            label_column: Column name for labels
            test_size: Fraction for test split
            eval_metrics: Whether to compute and return metrics

        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Loading training data from {data_path}")
        df = pd.read_csv(data_path)

        X_text = df[text_column].astype(str)
        y = df[label_column]

        # Train/test split
        X_train_text, X_test_text, y_train, y_test = train_test_split(
            X_text, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y
        )

        # TF-IDF Vectorizer
        self._vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range
        )

        X_train = self._vectorizer.fit_transform(X_train_text)
        X_test = self._vectorizer.transform(X_test_text)

        # Logistic Regression
        self._model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=self.random_state
        )

        logger.info("Training LogisticRegression model...")
        self._model.fit(X_train, y_train)

        self._is_loaded = True

        metrics = {}
        if eval_metrics:
            y_pred = self._model.predict(X_test)

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision_weighted": precision_score(y_test, y_pred, average="weighted", zero_division=0),
                "recall_weighted": recall_score(y_test, y_pred, average="weighted", zero_division=0),
                "f1_weighted": f1_score(y_test, y_pred, average="weighted", zero_division=0),
                "train_samples": len(X_train_text),
                "test_samples": len(X_test_text),
                "num_classes": len(self._model.classes_),
                "num_features": len(self._vectorizer.get_feature_names_out()),
            }

            logger.info(f"Training complete. Accuracy: {metrics['accuracy']:.4f}")
            logger.info(f"Classes: {list(self._model.classes_)}")

        return metrics

    def predict(self, text: str) -> Optional[str]:
        """
        Predict career category from text.

        Args:
            text: Input text (CV, job description, etc.)

        Returns:
            Predicted career category or None if confidence < threshold
        """
        if not self.is_fitted:
            logger.warning("Model not fitted, cannot predict")
            return None

        try:
            cleaned = preprocess_text(text)
            vector = self._vectorizer.transform([cleaned])

            # Get prediction probabilities
            probas = self._model.predict_proba(vector)[0]
            max_proba = probas.max()

            # Check confidence threshold
            if max_proba < self.confidence_threshold:
                logger.debug(f"Prediction confidence {max_proba:.3f} below threshold {self.confidence_threshold}")
                return None

            predicted_idx = probas.argmax()
            return self._model.classes_[predicted_idx]

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None

    def predict_proba(self, text: str) -> Optional[Dict[str, float]]:
        """
        Get prediction probabilities for all classes.

        Args:
            text: Input text

        Returns:
            Dictionary mapping class -> probability, or None if error
        """
        if not self.is_fitted:
            return None

        try:
            cleaned = preprocess_text(text)
            vector = self._vectorizer.transform([cleaned])
            probas = self._model.predict_proba(vector)[0]

            return {
                cls: float(prob)
                for cls, prob in zip(self._model.classes_, probas)
            }
        except Exception as e:
            logger.error(f"predict_proba failed: {e}")
            return None

    def predict_top_k(self, text: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Get top-k predictions with probabilities.

        Args:
            text: Input text
            k: Number of top predictions

        Returns:
            List of {"career": str, "probability": float} dicts
        """
        probas = self.predict_proba(text)
        if not probas:
            return []

        sorted_probas = sorted(probas.items(), key=lambda x: x[1], reverse=True)
        return [
            {"career": career, "probability": prob}
            for career, prob in sorted_probas[:k]
        ]

    def get_feature_importance(self, top_n: int = 20) -> Dict[str, List[Dict]]:
        """
        Get top features per class (for interpretability).

        Args:
            top_n: Number of top features per class

        Returns:
            Dictionary mapping class -> list of {"feature": str, "coef": float}
        """
        if not self.is_fitted or not hasattr(self._model, "coef_"):
            return {}

        feature_names = self._vectorizer.get_feature_names_out()
        importance = {}

        for i, cls in enumerate(self._model.classes_):
            coefs = self._model.coef_[i]
            top_indices = coefs.argsort()[-top_n:][::-1]
            importance[cls] = [
                {"feature": feature_names[idx], "coefficient": float(coefs[idx])}
                for idx in top_indices
            ]

        return importance


# Backward compatibility - module-level instance
_classifier_instance: Optional[CareerClassifier] = None


def get_classifier() -> CareerClassifier:
    """Get singleton CareerClassifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = CareerClassifier()
    return _classifier_instance


def predict_career(cv_text: str) -> Optional[str]:
    """Backward compatible predict function."""
    return get_classifier().predict(cv_text)


def predict_career_proba(cv_text: str) -> Optional[Dict[str, float]]:
    """Backward compatible predict_proba function."""
    return get_classifier().predict_proba(cv_text)


def predict_career_top_k(cv_text: str, k: int = 3) -> List[Dict[str, Any]]:
    """Backward compatible predict_top_k function."""
    return get_classifier().predict_top_k(cv_text, k)


# CLI for training
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    classifier = CareerClassifier()

    # Default data path
    data_path = "data/career_preprocessed.csv"
    if len(sys.argv) > 1:
        data_path = sys.argv[1]

    if not Path(data_path).exists():
        logger.error(f"Data file not found: {data_path}")
        sys.exit(1)

    metrics = classifier.train(data_path)

    # Print metrics
    print("\n===== TRAINING METRICS =====")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    # Save model
    classifier.save({
        "training_data": data_path,
        "metrics": metrics
    })

    print("\nModel saved successfully!")