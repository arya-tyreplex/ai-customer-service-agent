"""
Fast ML Model Training - Good Accuracy
Train all models quickly with optimized parameters
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("  TyrePlex ML Training - Fast Mode")
print("  Training all models with good accuracy (5-10 minutes)")
print("="*80)

# Create directories
Path('models').mkdir(exist_ok=True)
Path('data/processed').mkdir(parents=True, exist_ok=True)

# Load data
print("\n[1/6] Loading vehicle data...")
df = pd.read_csv('vehicle_tyre_mapping.csv', low_memory=False)
print(f"✅ Loaded {len(df):,} records")

# Data cleaning
print("\n[2/6] Cleaning data...")
initial_count = len(df)

df = df.dropna(subset=['Vehicle Make', 'Vehicle Model', 'Vehicle Variant', 'Front Tyre Brand', 'Front Tyre Price'])
df['Front Tyre Price'] = df['Front Tyre Price'].fillna(df['Front Tyre Price'].median())
df['Rear Tyre Price'] = df['Rear Tyre Price'].fillna(df['Rear Tyre Price'].median())
df = df[df['Front Tyre Price'] > 0]
df = df.drop_duplicates(subset=['Vehicle Make', 'Vehicle Model', 'Vehicle Variant', 'Front Tyre Brand'])

print(f"✅ Cleaned: {initial_count:,} → {len(df):,} records")

# Feature engineering
print("\n[3/6] Engineering features...")
df['tyre_size_front'] = df['Front Tyre Width'].astype(str) + '/' + df['Front Tyre Aspect Ratio'].astype(str) + 'R' + df['Front Rim Size'].astype(str)

# Encode categorical variables
print("\n[4/6] Encoding categorical variables...")
encoders = {}

categorical_cols = ['Vehicle Make', 'Vehicle Model', 'Vehicle Variant', 'Front Tyre Brand', 'Front Tyre Type', 'Fuel Type', 'Vehicle Type']

for col in categorical_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

# Encode tyre size
le_size = LabelEncoder()
df['tyre_size_encoded'] = le_size.fit_transform(df['tyre_size_front'].astype(str))
encoders['tyre_size'] = le_size

# Intent (synthetic)
intents = ['buy_tyres', 'price_inquiry', 'size_inquiry', 'brand_inquiry', 'booking']
np.random.seed(42)
df['intent'] = np.random.choice(intents, size=len(df))
le_intent = LabelEncoder()
df['intent_encoded'] = le_intent.fit_transform(df['intent'])
encoders['intent'] = le_intent

with open('data/processed/encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)

print(f"✅ Encoded {len(encoders)} categorical columns")

# Prepare datasets
print("\n[5/6] Training models...")
metrics = {}

# Model 1: Brand Recommender
print("\n📊 Training Brand Recommender...")
brand_features = ['Vehicle Make_encoded', 'Vehicle Model_encoded', 'Vehicle Variant_encoded', 'Front Tyre Width', 'Front Tyre Aspect Ratio', 'Front Rim Size']
brand_features = [f for f in brand_features if f in df.columns]

X_brand = df[brand_features].fillna(0)
y_brand = df['Front Tyre Brand_encoded']

X_train, X_test, y_train, y_test = train_test_split(X_brand, y_brand, test_size=0.2, random_state=42)

brand_model = RandomForestClassifier(n_estimators=200, max_depth=25, random_state=42, n_jobs=-1)
brand_model.fit(X_train, y_train)
y_pred = brand_model.predict(X_test)

metrics['brand_recommender'] = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
    'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
    'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0)
}

with open('models/brand_recommender.pkl', 'wb') as f:
    pickle.dump(brand_model, f)
with open('data/processed/brand_dataset.pkl', 'wb') as f:
    pickle.dump((X_brand, y_brand), f)

print(f"✅ Brand Recommender: {metrics['brand_recommender']['accuracy']*100:.2f}% accuracy")

# Model 2: Price Predictor
print("\n📊 Training Price Predictor...")
price_features = ['Vehicle Make_encoded', 'Vehicle Model_encoded', 'Vehicle Variant_encoded', 'Front Tyre Brand_encoded', 'Front Tyre Width', 'Front Tyre Aspect Ratio', 'Front Rim Size']
price_features = [f for f in price_features if f in df.columns]

X_price = df[price_features].fillna(0)
y_price = df['Front Tyre Price']

scaler = StandardScaler()
X_price_scaled = scaler.fit_transform(X_price)

X_train, X_test, y_train, y_test = train_test_split(X_price_scaled, y_price, test_size=0.2, random_state=42)

price_model = RandomForestRegressor(n_estimators=200, max_depth=25, random_state=42, n_jobs=-1)
price_model.fit(X_train, y_train)
y_pred = price_model.predict(X_test)

metrics['price_predictor'] = {
    'mae': mean_absolute_error(y_test, y_pred),
    'r2_score': r2_score(y_test, y_pred),
    'mean_price': float(y_test.mean())
}

with open('models/price_predictor.pkl', 'wb') as f:
    pickle.dump(price_model, f)
with open('data/processed/price_dataset.pkl', 'wb') as f:
    pickle.dump((X_price, y_price), f)
with open('data/processed/scalers.pkl', 'wb') as f:
    pickle.dump({'price': scaler}, f)

print(f"✅ Price Predictor: R² = {metrics['price_predictor']['r2_score']:.4f}, MAE = ₹{metrics['price_predictor']['mae']:.2f}")

# Model 3: Size Predictor
print("\n📊 Training Size Predictor...")
size_features = ['Vehicle Make_encoded', 'Vehicle Model_encoded', 'Vehicle Variant_encoded']
size_features = [f for f in size_features if f in df.columns]

X_size = df[size_features].fillna(0)
y_size = df['tyre_size_encoded']

X_train, X_test, y_train, y_test = train_test_split(X_size, y_size, test_size=0.2, random_state=42)

size_model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
size_model.fit(X_train, y_train)
y_pred = size_model.predict(X_test)

metrics['size_predictor'] = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
    'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
    'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0)
}

with open('models/size_predictor.pkl', 'wb') as f:
    pickle.dump(size_model, f)
with open('data/processed/size_dataset.pkl', 'wb') as f:
    pickle.dump((X_size, y_size), f)

print(f"✅ Size Predictor: {metrics['size_predictor']['accuracy']*100:.2f}% accuracy")

# Model 4: Intent Classifier
print("\n📊 Training Intent Classifier...")
X_intent = df[['Vehicle Make_encoded', 'Front Tyre Brand_encoded']].fillna(0)
y_intent = df['intent_encoded']

X_train, X_test, y_train, y_test = train_test_split(X_intent, y_intent, test_size=0.2, random_state=42)

intent_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
intent_model.fit(X_train, y_train)
y_pred = intent_model.predict(X_test)

metrics['intent_classifier'] = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
    'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
    'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0)
}

with open('models/intent_classifier.pkl', 'wb') as f:
    pickle.dump(intent_model, f)
with open('data/processed/intent_dataset.pkl', 'wb') as f:
    pickle.dump((X_intent, y_intent), f)

print(f"✅ Intent Classifier: {metrics['intent_classifier']['accuracy']*100:.2f}% accuracy")

# Save metrics
print("\n[6/6] Saving metrics...")
metrics['training_date'] = datetime.now().isoformat()
metrics['total_records'] = len(df)
metrics['training_mode'] = 'fast'

with open('models/model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2, default=str)

print("\n" + "="*80)
print("  Training Complete!")
print("="*80)

print("\n📊 Final Model Performance:")
print(f"\n1. Brand Recommender:  {metrics['brand_recommender']['accuracy']*100:.2f}% accuracy")
print(f"2. Price Predictor:    R² = {metrics['price_predictor']['r2_score']:.4f}, MAE = ₹{metrics['price_predictor']['mae']:.2f}")
print(f"3. Size Predictor:     {metrics['size_predictor']['accuracy']*100:.2f}% accuracy")
print(f"4. Intent Classifier:  {metrics['intent_classifier']['accuracy']*100:.2f}% accuracy")

print("\n✅ All models saved to 'models/' directory")
print("\n💡 Next: python test_complete_system.py")
print("="*80)
