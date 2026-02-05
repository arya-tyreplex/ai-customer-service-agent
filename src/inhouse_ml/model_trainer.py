"""
ML Model Trainer for TyrePlex.
Trains models for tyre recommendations without using LLMs.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pathlib import Path
from typing import Dict, Tuple


class TyrePlexMLTrainer:
    """Train ML models for tyre recommendations."""
    
    def __init__(self, data_processor):
        """
        Initialize trainer.
        
        Args:
            data_processor: TyrePlexDataProcessor instance
        """
        self.processor = data_processor
        self.models = {}
        self.encoders = {}
        
    def train_brand_recommender(self) -> Dict:
        """
        Train model to recommend tyre brand based on vehicle.
        
        Returns:
            Dictionary with model and metrics
        """
        print("\n🤖 Training Tyre Brand Recommender...")
        
        df = self.processor.df
        
        # Encode categorical variables
        self.encoders['make'] = LabelEncoder()
        self.encoders['model'] = LabelEncoder()
        self.encoders['type'] = LabelEncoder()
        self.encoders['fuel'] = LabelEncoder()
        
        df['make_enc'] = self.encoders['make'].fit_transform(df['Vehicle Make'])
        df['model_enc'] = self.encoders['model'].fit_transform(df['Vehicle Model'])
        df['type_enc'] = self.encoders['type'].fit_transform(df['Vehicle Type'])
        df['fuel_enc'] = self.encoders['fuel'].fit_transform(df['Fuel Type'])
        
        # Features
        X = df[[
            'make_enc',
            'model_enc',
            'type_enc',
            'fuel_enc',
            'Front Tyre Price'
        ]]
        
        # Target
        y = df['Front Tyre Brand']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Brand Recommender Accuracy: {accuracy:.2%}")
        
        # Feature importance
        feature_names = ['Make', 'Model', 'Type', 'Fuel', 'Price']
        importances = model.feature_importances_
        
        print("\n📊 Feature Importance:")
        for name, importance in zip(feature_names, importances):
            print(f"  {name}: {importance:.3f}")
        
        self.models['brand_recommender'] = model
        
        return {
            'model': model,
            'accuracy': accuracy,
            'feature_importance': dict(zip(feature_names, importances))
        }
    
    def train_price_predictor(self) -> Dict:
        """
        Train model to predict tyre price.
        
        Returns:
            Dictionary with model and metrics
        """
        print("\n🤖 Training Price Predictor...")
        
        df = self.processor.df
        
        # Features (using already encoded data)
        X = df[[
            'make_enc',
            'model_enc',
            'type_enc',
            'fuel_enc'
        ]]
        
        # Target
        y = df['Front Tyre Price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mae = np.mean(np.abs(y_test - y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        print(f"✅ Price Predictor MAE: ₹{mae:.2f}")
        print(f"✅ Price Predictor MAPE: {mape:.2f}%")
        
        self.models['price_predictor'] = model
        
        return {
            'model': model,
            'mae': mae,
            'mape': mape
        }
    
    def train_intent_classifier(self, training_data: list = None) -> Dict:
        """
        Train intent classifier for customer queries.
        
        Args:
            training_data: List of (text, intent) tuples
            
        Returns:
            Dictionary with model and metrics
        """
        print("\n🤖 Training Intent Classifier...")
        
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        
        # Default training data if none provided
        if training_data is None:
            training_data = [
                # Vehicle inquiry
                ("I have a Maruti Swift", "vehicle_inquiry"),
                ("My car is Hyundai Creta", "vehicle_inquiry"),
                ("I own a Honda City", "vehicle_inquiry"),
                ("My vehicle is Toyota Fortuner", "vehicle_inquiry"),
                
                # Tyre recommendation
                ("Which tyre is best", "tyre_recommendation"),
                ("Recommend tyres for city driving", "tyre_recommendation"),
                ("I need new tyres", "tyre_recommendation"),
                ("Suggest good tyres", "tyre_recommendation"),
                
                # Price inquiry
                ("What's the price", "price_inquiry"),
                ("How much does it cost", "price_inquiry"),
                ("What's the rate", "price_inquiry"),
                ("Price of MRF tyres", "price_inquiry"),
                
                # Availability
                ("Is it available", "availability"),
                ("Do you have in stock", "availability"),
                ("When can I get delivery", "availability"),
                
                # Comparison
                ("Compare MRF and CEAT", "comparison"),
                ("Which is better MRF or Apollo", "comparison"),
                ("Difference between brands", "comparison"),
                
                # Lead capture
                ("My name is Rahul", "lead_capture"),
                ("My number is 9876543210", "lead_capture"),
                ("Call me at", "lead_capture"),
            ]
        
        texts, labels = zip(*training_data)
        
        # Vectorize
        vectorizer = TfidfVectorizer(max_features=100)
        X = vectorizer.fit_transform(texts)
        
        # Train
        model = MultinomialNB()
        model.fit(X, labels)
        
        # Evaluate
        y_pred = model.predict(X)
        accuracy = accuracy_score(labels, y_pred)
        
        print(f"✅ Intent Classifier Accuracy: {accuracy:.2%}")
        
        self.models['intent_classifier'] = model
        self.encoders['intent_vectorizer'] = vectorizer
        
        return {
            'model': model,
            'vectorizer': vectorizer,
            'accuracy': accuracy
        }
    
    def save_models(self, output_dir: str = 'models'):
        """Save all trained models."""
        Path(output_dir).mkdir(exist_ok=True)
        
        print(f"\n💾 Saving models to {output_dir}/...")
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f'{output_dir}/{name}.pkl')
            print(f"  ✅ Saved {name}")
        
        # Save encoders
        for name, encoder in self.encoders.items():
            joblib.dump(encoder, f'{output_dir}/encoder_{name}.pkl')
            print(f"  ✅ Saved encoder_{name}")
        
        print(f"\n✅ All models saved successfully!")
    
    def load_models(self, model_dir: str = 'models'):
        """Load trained models."""
        print(f"\n📂 Loading models from {model_dir}/...")
        
        model_files = {
            'brand_recommender': 'brand_recommender.pkl',
            'price_predictor': 'price_predictor.pkl',
            'intent_classifier': 'intent_classifier.pkl'
        }
        
        for name, filename in model_files.items():
            path = f'{model_dir}/{filename}'
            if Path(path).exists():
                self.models[name] = joblib.load(path)
                print(f"  ✅ Loaded {name}")
        
        # Load encoders
        encoder_files = [
            'encoder_make.pkl',
            'encoder_model.pkl',
            'encoder_type.pkl',
            'encoder_fuel.pkl',
            'encoder_intent_vectorizer.pkl'
        ]
        
        for filename in encoder_files:
            path = f'{model_dir}/{filename}'
            if Path(path).exists():
                name = filename.replace('encoder_', '').replace('.pkl', '')
                self.encoders[name] = joblib.load(path)
                print(f"  ✅ Loaded encoder_{name}")
    
    def predict_brand(self, make: str, model: str, vehicle_type: str, 
                     fuel_type: str, price_range: float) -> str:
        """
        Predict recommended tyre brand.
        
        Args:
            make: Vehicle make
            model: Vehicle model
            vehicle_type: Type of vehicle
            fuel_type: Fuel type
            price_range: Expected price range
            
        Returns:
            Recommended brand name
        """
        if 'brand_recommender' not in self.models:
            raise ValueError("Brand recommender not trained")
        
        # Encode inputs
        make_enc = self.encoders['make'].transform([make])[0]
        model_enc = self.encoders['model'].transform([model])[0]
        type_enc = self.encoders['type'].transform([vehicle_type])[0]
        fuel_enc = self.encoders['fuel'].transform([fuel_type])[0]
        
        # Predict
        X = [[make_enc, model_enc, type_enc, fuel_enc, price_range]]
        brand = self.models['brand_recommender'].predict(X)[0]
        
        return brand
    
    def predict_price(self, make: str, model: str, vehicle_type: str,
                     fuel_type: str) -> float:
        """
        Predict tyre price.
        
        Args:
            make: Vehicle make
            model: Vehicle model
            vehicle_type: Type of vehicle
            fuel_type: Fuel type
            
        Returns:
            Predicted price
        """
        if 'price_predictor' not in self.models:
            raise ValueError("Price predictor not trained")
        
        # Encode inputs
        make_enc = self.encoders['make'].transform([make])[0]
        model_enc = self.encoders['model'].transform([model])[0]
        type_enc = self.encoders['type'].transform([vehicle_type])[0]
        fuel_enc = self.encoders['fuel'].transform([fuel_type])[0]
        
        # Predict
        X = [[make_enc, model_enc, type_enc, fuel_enc]]
        price = self.models['price_predictor'].predict(X)[0]
        
        return price
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classify customer intent.
        
        Args:
            text: Customer message
            
        Returns:
            Tuple of (intent, confidence)
        """
        if 'intent_classifier' not in self.models:
            raise ValueError("Intent classifier not trained")
        
        # Vectorize
        X = self.encoders['intent_vectorizer'].transform([text])
        
        # Predict
        intent = self.models['intent_classifier'].predict(X)[0]
        confidence = self.models['intent_classifier'].predict_proba(X).max()
        
        return intent, confidence


# Example usage
if __name__ == "__main__":
    from data_processor import TyrePlexDataProcessor
    
    # Load data
    processor = TyrePlexDataProcessor('data/tyreplex_data.csv')
    processor.load_data()
    processor.create_vehicle_lookup()
    processor.create_tyre_database()
    
    # Train models
    trainer = TyrePlexMLTrainer(processor)
    
    # Train all models
    brand_results = trainer.train_brand_recommender()
    price_results = trainer.train_price_predictor()
    intent_results = trainer.train_intent_classifier()
    
    # Save models
    trainer.save_models()
    
    print("\n✅ All models trained and saved!")
    print("\n📊 Summary:")
    print(f"  Brand Recommender: {brand_results['accuracy']:.2%} accuracy")
    print(f"  Price Predictor: ₹{price_results['mae']:.2f} MAE")
    print(f"  Intent Classifier: {intent_results['accuracy']:.2%} accuracy")
