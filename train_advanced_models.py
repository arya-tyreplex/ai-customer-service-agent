"""
Advanced ML Model Training - Highest Accuracy
Train all models with hyperparameter tuning and advanced techniques
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("  TyrePlex ML Training - Advanced Mode")
print("  Training all models with highest accuracy")
print("="*80)

# Create directories
Path('models').mkdir(exist_ok=True)
Path('data/processed').mkdir(parents=True, exist_ok=True)

# Load data
print("\n[1/7] Loading vehicle data...")
df = pd.read_csv('vehicle_tyre_mapping.csv', low_memory=False)
print(f"✅ Loaded {len(df):,} records")
print(f"✅ Columns: {len(df.columns)}")

# Data cleaning
print("\n[2/7] Cleaning data...")
initial_count = len(df)

# Remove rows with missing critical data
df = df.dropna(subset=[
    'Vehicle Make', 'Vehicle Model', 'Vehicle Variant',
    'Front Tyre Brand', 'Front Tyre Price'
])

# Fill missing prices with median
df['Front Tyre Price'] = df['Front Tyre Price'].fillna(df['Front Tyre Price'].median())
df['Rear Tyre Price'] = df['Rear Tyre Price'].fillna(df['Rear Tyre Price'].median())

# Remove invalid prices (0 or negative)
df = df[df['Front Tyre Price'] > 0]

# Remove duplicates
df = df.drop_duplicates(subset=['Vehicle Make', 'Vehicle Model', 'Vehicle Variant', 'Front Tyre Brand'])

cleaned_count = len(df)
print(f"✅ Cleaned: {initial_count:,} → {cleaned_count:,} records ({cleaned_count/initial_count*100:.1f}% retained)")

# Feature engineering
print("\n[3/7] Engineering features...")

# Create combined features
df['vehicle_full'] = df['Vehicle Make'] + ' ' + df['Vehicle Model'] + ' ' + df['Vehicle Variant']
df['tyre_size_front'] = df['Front Tyre Width'].astype(str) + '/' + df['Front Tyre Aspect Ratio'].astype(str) + 'R' + df['Front Rim Size'].astype(str)
df['price_range'] = pd.cut(df['Front Tyre Price'], bins=[0, 3000, 5000, 8000, 15000, 100000], labels=['budget', 'economy', 'mid', 'premium', 'luxury'])

# Encode categorical variables
print("\n[4/7] Encoding categorical variables...")
encoders = {}

categorical_cols = [
    'Vehicle Make', 'Vehicle Model', 'Vehicle Variant',
    'Front Tyre Brand', 'Front Tyre Type', 'Fuel Type', 'Vehicle Type'
]

for col in categorical_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

# Save encoders
with open('data/processed/encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)
print(f"✅ Encoded {len(encoders)} categorical columns")

# Prepare datasets
print("\n[5/7] Preparing datasets...")

# Dataset 1: Brand Recommendation
brand_features = [
    'Vehicle Make_encoded', 'Vehicle Model_encoded', 'Vehicle Variant_encoded',
    'Front Tyre Width', 'Front Tyre Aspect Ratio', 'Front Rim Size',
    'Vehicle Price', 'Fuel Type_encoded', 'Vehicle Type_encoded'
]
brand_features = [f for f in brand_features if f in df.columns]

X_brand = df[brand_features].fillna(0)
y_brand = df['Front Tyre Brand_encoded']

# Dataset 2: Price Prediction
price_features = [
    'Vehicle Make_encoded', 'Vehicle Model_encoded', 'Vehicle Variant_encoded',
    'Front Tyre Brand_encoded', 'Front Tyre Width', 'Front Tyre Aspect Ratio',
    'Front Rim Size', 'Front Tyre Type_encoded', 'Vehicle Price'
]
price_features = [f for f in price_features if f in df.columns]

X_price = df[price_features].fillna(0)
y_price = df['Front Tyre Price']

# Dataset 3: Size Prediction
size_features = [
    'Vehicle Make_encoded', 'Vehicle Model_encoded', 'Vehicle Variant_encoded',
    'Vehicle Price', 'Fuel Type_encoded', 'Vehicle Type_encoded'
]
size_features = [f for f in size_features if f in df.columns]

X_size = df[size_features].fillna(0)
y_size = df['tyre_size_front']

# Encode tyre size
le_size = LabelEncoder()
y_size_encoded = le_size.fit_transform(y_size.astype(str))
encoders['tyre_size'] = le_size

# Dataset 4: Intent Classification (synthetic for demo)
intents = ['buy_tyres', 'price_inquiry', 'size_inquiry', 'brand_inquiry', 'booking']
np.random.seed(42)
df['intent'] = np.random.choice(intents, size=len(df))
le_intent = LabelEncoder()
y_intent = le_intent.fit_transform(df['intent'])
encoders['intent'] = le_intent

# Use simple features for intent
X_intent = df[['Vehicle Make_encoded', 'Front Tyre Brand_encoded']].fillna(0)

print(f"✅ Brand dataset: {X_brand.shape}")
print(f"✅ Price dataset: {X_price.shape}")
print(f"✅ Size dataset: {X_size.shape}")
print(f"✅ Intent dataset: {X_intent.shape}")

# Save processed datasets
with open('data/processed/brand_dataset.pkl', 'wb') as f:
    pickle.dump((X_brand, y_brand), f)
with open('data/processed/price_dataset.pkl', 'wb') as f:
    pickle.dump((X_price, y_price), f)
with open('data/processed/size_dataset.pkl', 'wb') as f:
    pickle.dump((X_size, y_size_encoded), f)
with open('data/processed/intent_dataset.pkl', 'wb') as f:
    pickle.dump((X_intent, y_intent), f)

# Scale features for price prediction
scaler = StandardScaler()
X_price_scaled = scaler.fit_transform(X_price)

scalers = {'price': scaler}
with open('data/processed/scalers.pkl', 'wb') as f:
    pickle.dump(scalers, f)

print("\n[6/7] Training models with hyperparameter tuning...")
print("⏳ This may take 10-30 minutes for highest accuracy...\n")

metrics = {}

# Model 1: Brand Recommender (Random Forest with tuning)
print("📊 Training Brand Recommender...")
X_train, X_test, y_train, y_test = train_test_split(X_brand, y_brand, test_size=0.2, random_state=42)

# Hyperparameter tuning
param_grid_brand = {
    'n_estimators': [200, 300],
    'max_depth': [20, 30, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

rf_brand = RandomForestClassifier(random_state=42, n_jobs=-1)
grid_brand = GridSearchCV(rf_brand, param_grid_brand, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
grid_brand.fit(X_train, y_train)

brand_model = grid_brand.best_estimator_
y_pred = brand_model.predict(X_test)

metrics['brand_recommender'] = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
    'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
    'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
    'best_params': grid_brand.best_params_,
    'cv_score': grid_brand.best_score_
}

with open('models/brand_recommender.pkl', 'wb') as f:
    pickle.dump(brand_model, f)

print(f"✅ Brand Recommender: {metrics['brand_recommender']['accuracy']*100:.2f}% accuracy")
print(f"   Best params: {grid_brand.best_params_}")

# Model 2: Price Predictor (Gradient Boosting with tuning)
print("\n📊 Training Price Predictor...")
X_train, X_test, y_train, y_test = train_test_split(X_price_scaled, y_price, test_size=0.2, random_state=42)

param_grid_price = {
    'n_estimators': [200, 300],
    'learning_rate': [0.05, 0.1],
    'max_depth': [5, 7],
    'min_samples_split': [2, 5]
}

gb_price = GradientBoostingRegressor(random_state=42)
grid_price = GridSearchCV(gb_price, param_grid_price, cv=3, scoring='r2', n_jobs=-1, verbose=1)
grid_price.fit(X_train, y_train)

price_model = grid_price.best_estimator_
y_pred = price_model.predict(X_test)

metrics['price_predictor'] = {
    'mae': mean_absolute_error(y_test, y_pred),
    'r2_score': r2_score(y_test, y_pred),
    'mean_price': float(y_test.mean()),
    'best_params': grid_price.best_params_,
    'cv_score': grid_price.best_score_
}

with open('models/price_predictor.pkl', 'wb') as f:
    pickle.dump(price_model, f)

print(f"✅ Price Predictor: R² = {metrics['price_predictor']['r2_score']:.4f}, MAE = ₹{metrics['price_predictor']['mae']:.2f}")
print(f"   Best params: {grid_price.best_params_}")

# Model 3: Size Predictor (Random Forest with tuning)
print("\n📊 Training Size Predictor...")
X_train, X_test, y_train, y_test = train_test_split(X_size, y_size_encoded, test_size=0.2, random_state=42)

param_grid_size = {
    'n_estimators': [200, 300],
    'max_depth': [15, 20, None],
    'min_samples_split': [2, 5]
}

rf_size = RandomForestClassifier(random_state=42, n_jobs=-1)
grid_size = GridSearchCV(rf_size, param_grid_size, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
grid_size.fit(X_train, y_train)

size_model = grid_size.best_estimator_
y_pred = size_model.predict(X_test)

metrics['size_predictor'] = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
    'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
    'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
    'best_params': grid_size.best_params_,
    'cv_score': grid_size.best_score_
}

with open('models/size_predictor.pkl', 'wb') as f:
    pickle.dump(size_model, f)

print(f"✅ Size Predictor: {metrics['size_predictor']['accuracy']*100:.2f}% accuracy")
print(f"   Best params: {grid_size.best_params_}")

# Model 4: Intent Classifier (Gradient Boosting with tuning)
print("\n📊 Training Intent Classifier...")
X_train, X_test, y_train, y_test = train_test_split(X_intent, y_intent, test_size=0.2, random_state=42)

param_grid_intent = {
    'n_estimators': [100, 200],
    'learning_rate': [0.1, 0.2],
    'max_depth': [3, 5]
}

gb_intent = GradientBoostingClassifier(random_state=42)
grid_intent = GridSearchCV(gb_intent, param_grid_intent, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
grid_intent.fit(X_train, y_train)

intent_model = grid_intent.best_estimator_
y_pred = intent_model.predict(X_test)

metrics['intent_classifier'] = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
    'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
    'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
    'best_params': grid_intent.best_params_,
    'cv_score': grid_intent.best_score_
}

with open('models/intent_classifier.pkl', 'wb') as f:
    pickle.dump(intent_model, f)

print(f"✅ Intent Classifier: {metrics['intent_classifier']['accuracy']*100:.2f}% accuracy")
print(f"   Best params: {grid_intent.best_params_}")

# Save metrics
print("\n[7/7] Saving metrics and metadata...")
metrics['training_date'] = datetime.now().isoformat()
metrics['total_records'] = len(df)
metrics['features'] = {
    'brand': brand_features,
    'price': price_features,
    'size': size_features,
    'intent': list(X_intent.columns)
}

with open('models/model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2, default=str)

print("\n" + "="*80)
print("  Training Complete!")
print("="*80)

print("\n📊 Final Model Performance:")
print(f"\n1. Brand Recommender:")
print(f"   Accuracy:  {metrics['brand_recommender']['accuracy']*100:.2f}%")
print(f"   Precision: {metrics['brand_recommender']['precision']*100:.2f}%")
print(f"   Recall:    {metrics['brand_recommender']['recall']*100:.2f}%")
print(f"   F1-Score:  {metrics['brand_recommender']['f1_score']*100:.2f}%")

print(f"\n2. Price Predictor:")
print(f"   R² Score:  {metrics['price_predictor']['r2_score']:.4f}")
print(f"   MAE:       ₹{metrics['price_predictor']['mae']:.2f}")
print(f"   Avg Price: ₹{metrics['price_predictor']['mean_price']:.2f}")

print(f"\n3. Size Predictor:")
print(f"   Accuracy:  {metrics['size_predictor']['accuracy']*100:.2f}%")
print(f"   Precision: {metrics['size_predictor']['precision']*100:.2f}%")
print(f"   Recall:    {metrics['size_predictor']['recall']*100:.2f}%")
print(f"   F1-Score:  {metrics['size_predictor']['f1_score']*100:.2f}%")

print(f"\n4. Intent Classifier:")
print(f"   Accuracy:  {metrics['intent_classifier']['accuracy']*100:.2f}%")
print(f"   Precision: {metrics['intent_classifier']['precision']*100:.2f}%")
print(f"   Recall:    {metrics['intent_classifier']['recall']*100:.2f}%")
print(f"   F1-Score:  {metrics['intent_classifier']['f1_score']*100:.2f}%")

print("\n✅ All models saved to 'models/' directory")
print("✅ Processed data saved to 'data/processed/' directory")
print("✅ Metrics saved to 'models/model_metrics.json'")

print("\n💡 Next steps:")
print("   1. Test models: python test_complete_system.py")
print("   2. Run voice agent: python voice_demo_aws.py")
print("   3. Check metrics: cat models/model_metrics.json")

print("\n" + "="*80)
