"""
ML Model Trainer for TyrePlex System
Trains multiple models for different tasks
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Any
from loguru import logger

# ML models
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, RandomForestRegressor
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)
import joblib


class ModelTrainer:
    """
    Trains ML models for TyrePlex system.
    
    Models:
    1. Brand Recommender (Random Forest Classifier)
    2. Price Predictor (Gradient Boosting Regressor)
    3. Tyre Size Predictor (Random Forest Classifier)
    4. Intent Classifier (Multinomial Naive Bayes)
    """
    
    def __init__(self, data_dir: str = 'data/processed'):
        self.data_dir = data_dir
        self.models = {}
        self.metrics = {}
        self.encoders = None
        self.scalers = None
        
    def load_datasets(self):
        """Load all preprocessed datasets."""
        logger.info(f"Loading datasets from {self.data_dir}/...")
        
        # Load encoders and scalers
        self.encoders = pickle.load(open(f'{self.data_dir}/encoders.pkl', 'rb'))
        self.scalers = pickle.load(open(f'{self.data_dir}/scalers.pkl', 'rb'))
        logger.success("✅ Loaded encoders and scalers")
        
        # Load datasets
        self.brand_data = pickle.load(open(f'{self.data_dir}/brand_dataset.pkl', 'rb'))
        self.price_data = pickle.load(open(f'{self.data_dir}/price_dataset.pkl', 'rb'))
        self.size_data = pickle.load(open(f'{self.data_dir}/size_dataset.pkl', 'rb'))
        self.intent_data = pickle.load(open(f'{self.data_dir}/intent_dataset.pkl', 'rb'))
        
        logger.success("✅ Loaded all datasets")
    
    def train_brand_recommender(self) -> Dict:
        """
        Train brand recommendation model.
        Uses Random Forest Classifier for multi-class classification.
        """
        logger.info("\n" + "=" * 70)
        logger.info("Training Brand Recommender Model")
        logger.info("=" * 70)
        
        X_train, X_test, y_train, y_test = self.brand_data
        
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Test samples: {len(X_test)}")
        logger.info(f"Number of brands: {len(np.unique(y_train))}")
        
        # Train model
        logger.info("\n🔄 Training Random Forest Classifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        
        model.fit(X_train, y_train)
        logger.success("✅ Model trained")
        
        # Evaluate
        logger.info("\n📊 Evaluating model...")
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        metrics = {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'num_classes': len(np.unique(y_train))
        }
        
        logger.success(f"✅ Accuracy: {accuracy*100:.2f}%")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\n🔝 Top 5 Important Features:")
        for idx, row in feature_importance.head().iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        self.models['brand_recommender'] = model
        self.metrics['brand_recommender'] = metrics
        
        return metrics
    
    def train_price_predictor(self) -> Dict:
        """
        Train price prediction model.
        Uses Gradient Boosting Regressor for regression.
        """
        logger.info("\n" + "=" * 70)
        logger.info("Training Price Predictor Model")
        logger.info("=" * 70)
        
        X_train, X_test, y_train, y_test = self.price_data
        
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Test samples: {len(X_test)}")
        logger.info(f"Price range: ₹{y_train.min():.0f} - ₹{y_train.max():.0f}")
        
        # Train model
        logger.info("\n🔄 Training Gradient Boosting Regressor...")
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=10,
            learning_rate=0.1,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            verbose=0
        )
        
        model.fit(X_train, y_train)
        logger.success("✅ Model trained")
        
        # Evaluate
        logger.info("\n📊 Evaluating model...")
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        logger.success(f"✅ Mean Absolute Error: ₹{mae:.2f}")
        logger.success(f"✅ RMSE: ₹{rmse:.2f}")
        logger.success(f"✅ R² Score: {r2:.4f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\n🔝 Top 5 Important Features:")
        for idx, row in feature_importance.head().iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        self.models['price_predictor'] = model
        self.metrics['price_predictor'] = metrics
        
        return metrics
    
    def train_size_predictor(self) -> Dict:
        """
        Train tyre size prediction model.
        Uses Random Forest Classifier for multi-class classification.
        """
        logger.info("\n" + "=" * 70)
        logger.info("Training Tyre Size Predictor Model")
        logger.info("=" * 70)
        
        X_train, X_test, y_train, y_test = self.size_data
        
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Test samples: {len(X_test)}")
        logger.info(f"Number of sizes: {len(np.unique(y_train))}")
        
        # Train model
        logger.info("\n🔄 Training Random Forest Classifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=25,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        
        model.fit(X_train, y_train)
        logger.success("✅ Model trained")
        
        # Evaluate
        logger.info("\n📊 Evaluating model...")
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        metrics = {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'num_classes': len(np.unique(y_train))
        }
        
        logger.success(f"✅ Accuracy: {accuracy*100:.2f}%")
        
        self.models['size_predictor'] = model
        self.metrics['size_predictor'] = metrics
        
        return metrics
    
    def train_intent_classifier(self) -> Dict:
        """
        Train customer intent classification model.
        Uses Multinomial Naive Bayes for text classification.
        """
        logger.info("\n" + "=" * 70)
        logger.info("Training Intent Classifier Model")
        logger.info("=" * 70)
        
        X_train, X_test, y_train, y_test = self.intent_data
        
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Test samples: {len(X_test)}")
        logger.info(f"Number of intents: {len(np.unique(y_train))}")
        
        # Train model
        logger.info("\n🔄 Training Multinomial Naive Bayes...")
        model = MultinomialNB(alpha=1.0)
        
        model.fit(X_train, y_train)
        logger.success("✅ Model trained")
        
        # Evaluate
        logger.info("\n📊 Evaluating model...")
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        metrics = {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'num_classes': len(np.unique(y_train))
        }
        
        logger.success(f"✅ Accuracy: {accuracy*100:.2f}%")
        
        # Show intent labels
        intent_labels = self.encoders['intent'].classes_
        logger.info("\n🎯 Intent Classes:")
        for i, intent in enumerate(intent_labels):
            logger.info(f"  {i+1}. {intent}")
        
        self.models['intent_classifier'] = model
        self.metrics['intent_classifier'] = metrics
        
        return metrics
    
    def train_all_models(self):
        """Train all models."""
        logger.info("\n" + "=" * 70)
        logger.info("Training All Models")
        logger.info("=" * 70)
        
        # Load datasets
        self.load_datasets()
        
        # Train each model
        self.train_brand_recommender()
        self.train_price_predictor()
        self.train_size_predictor()
        self.train_intent_classifier()
        
        logger.success("\n✅ All models trained successfully!")
    
    def save_models(self, output_dir: str = 'models'):
        """Save all trained models."""
        Path(output_dir).mkdir(exist_ok=True)
        
        logger.info(f"\n💾 Saving models to {output_dir}/...")
        
        for model_name, model in self.models.items():
            joblib.dump(model, f'{output_dir}/{model_name}.pkl')
            logger.success(f"✅ Saved {model_name}")
        
        # Save metrics
        import json
        with open(f'{output_dir}/model_metrics.json', 'w') as f:
            # Convert numpy types to Python types
            metrics_json = {}
            for model_name, metrics in self.metrics.items():
                metrics_json[model_name] = {
                    k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                    for k, v in metrics.items()
                }
            json.dump(metrics_json, f, indent=2)
        
        logger.success(f"✅ Saved model metrics")
        
        logger.success(f"\n✅ All models saved to {output_dir}/")
    
    def get_model_summary(self) -> Dict:
        """Get summary of all models."""
        return {
            'models_trained': list(self.models.keys()),
            'metrics': self.metrics,
            'total_models': len(self.models)
        }


# CLI usage
if __name__ == "__main__":
    import sys
    
    logger.info("=" * 70)
    logger.info("TyrePlex Model Trainer")
    logger.info("=" * 70)
    
    # Initialize trainer
    trainer = ModelTrainer('data/processed')
    
    # Train all models
    trainer.train_all_models()
    
    # Save models
    trainer.save_models('models')
    
    # Print summary
    summary = trainer.get_model_summary()
    logger.info("\n" + "=" * 70)
    logger.info("Training Summary")
    logger.info("=" * 70)
    logger.info(f"\n✅ Trained {summary['total_models']} models:")
    for model_name in summary['models_trained']:
        logger.info(f"  - {model_name}")
    
    logger.info("\n📊 Model Performance:")
    for model_name, metrics in summary['metrics'].items():
        logger.info(f"\n  {model_name}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                if 'accuracy' in metric:
                    logger.info(f"    {metric}: {value*100:.2f}%")
                else:
                    logger.info(f"    {metric}: {value:.2f}")
            else:
                logger.info(f"    {metric}: {value}")
    
    logger.success("\n✅ Model training complete!")
    logger.info("\nNext step: python src/ml_system/ml_inference.py")
