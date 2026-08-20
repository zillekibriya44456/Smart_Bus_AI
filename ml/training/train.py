import pandas as pd
import numpy as np
import os
import joblib
import json
import warnings

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("XGBoost not available, skipping XGBoost models.")

warnings.filterwarnings('ignore')

CLEAN_CSV = '/Users/zillekibriya/Desktop/SmartBusStop/data/cleaned/bus_stop_optimization_dataset_15000_cleaned.csv'
MODEL_DIR = '/Users/zillekibriya/Desktop/SmartBusStop/ml/models'

def calculate_suitability(df):
    """Phase 4 Engine to compute the ground truth for our surrogate models"""
    # Demand Score (Max expected 100)
    demand = (df['Passenger_Count'] / 100.0) * 100
    demand = np.clip(demand, 0, 100)
    
    # Road Score (Optimal width 12m)
    road = np.where(df['Road_Width'] >= 12, 100, (df['Road_Width'] / 12.0) * 100)
    
    # Accessibility
    access = 100 - ((df['Walking_Distance_m'] / 500.0) * 100)
    access = np.clip(access, 0, 100)
    
    # Traffic/Safety
    traffic_mapping = {'Low': 100, 'Moderate': 80, 'High': 60}
    safety = df['Traffic_Level'].map(traffic_mapping).fillna(80)
    
    # Spacing
    dist = df['Distance_to_Next_Stop_m']
    spacing = np.where((dist >= 500) & (dist <= 1000), 100,
                       np.where(dist < 500, (dist/500)*100, (1000/dist)*100))
    spacing = np.clip(spacing, 0, 100)
    
    # Weights
    w_demand, w_road, w_access, w_safety, w_spacing = 0.30, 0.15, 0.20, 0.25, 0.10
    
    score = (w_demand * demand) + (w_road * road) + (w_access * access) + \
            (w_safety * safety) + (w_spacing * spacing)
            
    # Hard constraints
    # Road width < 6m -> 0
    score = np.where(df['Road_Width'] < 6, 0, score)
    # Distance < 200m -> 0
    score = np.where(df['Distance_to_Next_Stop_m'] < 200, 0, score)
    
    df['Suitability_Score'] = score
    
    # Categories
    conditions = [
        (df['Suitability_Score'] >= 80),
        (df['Suitability_Score'] >= 65),
        (df['Suitability_Score'] >= 50),
        (df['Suitability_Score'] >= 35)
    ]
    choices = ['Highly Suitable', 'Suitable', 'Moderately Suitable', 'Needs Improvement']
    df['Suitability_Category'] = np.select(conditions, choices, default='Not Suitable')
    
    return df

def train_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    df = pd.read_csv(CLEAN_CSV)
    df = calculate_suitability(df)
    
    features = ['Passenger_Count', 'Boarding', 'Alighting', 'Road_Width', 
                'Walking_Distance_m', 'Distance_to_Next_Stop_m', 'Traffic_Level',
                'Bus_Frequency', 'Waiting_Time_min', 'Occupancy_pct']
                
    num_features = ['Passenger_Count', 'Boarding', 'Alighting', 'Road_Width', 
                    'Walking_Distance_m', 'Distance_to_Next_Stop_m', 
                    'Bus_Frequency', 'Waiting_Time_min', 'Occupancy_pct']
    cat_features = ['Traffic_Level']
    
    X = df[features]
    y_reg = df['Suitability_Score']
    y_clf = df['Suitability_Category']
    
    X_train, X_test, y_train_reg, y_test_reg, y_train_clf, y_test_clf = train_test_split(
        X, y_reg, y_clf, test_size=0.2, random_state=42)
        
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ])
        
    # Regression Models
    reg_models = {
        'RandomForest': RandomForestRegressor(n_estimators=50, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=50, random_state=42)
    }
    
    if XGB_AVAILABLE:
        reg_models['XGBoost'] = xgb.XGBRegressor(n_estimators=50, random_state=42)
    
    reg_results = {}
    best_reg_name = None
    best_reg_score = -float('inf')
    best_reg_model = None
    
    for name, model in reg_models.items():
        print(f"Training {name} (Regression)...")
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipeline.fit(X_train, y_train_reg)
        preds = pipeline.predict(X_test)
        
        r2 = r2_score(y_test_reg, preds)
        reg_results[name] = {
            'MAE': float(mean_absolute_error(y_test_reg, preds)),
            'RMSE': float(np.sqrt(mean_squared_error(y_test_reg, preds))),
            'R2': float(r2)
        }
        if r2 > best_reg_score:
            best_reg_score = r2
            best_reg_name = name
            best_reg_model = pipeline

    joblib.dump(best_reg_model, os.path.join(MODEL_DIR, 'best_reg_model.pkl'))
    
    # Extract Feature Importance from best model
    cat_encoder = best_reg_model.named_steps['preprocessor'].named_transformers_['cat']
    cat_names = cat_encoder.get_feature_names_out(cat_features).tolist()
    feature_names = num_features + cat_names
    
    importance = None
    if hasattr(best_reg_model.named_steps['model'], 'feature_importances_'):
        importance = best_reg_model.named_steps['model'].feature_importances_.tolist()
        
    feature_imp_dict = dict(zip(feature_names, importance)) if importance else {}
    
    # Classification Models
    clf_models = {
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
        'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=50, random_state=42)
    }
    
    if XGB_AVAILABLE:
        clf_models['XGBoost'] = xgb.XGBClassifier(n_estimators=50, random_state=42, use_label_encoder=False, eval_metric='mlogloss')
    
    y_train_clf_enc, labels = pd.factorize(y_train_clf)
    y_test_clf_enc = pd.Series(y_test_clf).map({l: i for i, l in enumerate(labels)}).values
    
    clf_results = {}
    best_clf_name = None
    best_clf_score = -float('inf')
    best_clf_model = None
    
    for name, model in clf_models.items():
        print(f"Training {name} (Classification)...")
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipeline.fit(X_train, y_train_clf_enc)
        preds = pipeline.predict(X_test)
        
        acc = accuracy_score(y_test_clf_enc, preds)
        clf_results[name] = {
            'Accuracy': float(acc),
            'Precision': float(precision_score(y_test_clf_enc, preds, average='weighted', zero_division=0)),
            'Recall': float(recall_score(y_test_clf_enc, preds, average='weighted', zero_division=0)),
            'F1': float(f1_score(y_test_clf_enc, preds, average='weighted', zero_division=0))
        }
        if acc > best_clf_score:
            best_clf_score = acc
            best_clf_name = name
            best_clf_model = pipeline
            
    joblib.dump(best_clf_model, os.path.join(MODEL_DIR, 'best_clf_model.pkl'))
    joblib.dump(list(labels), os.path.join(MODEL_DIR, 'clf_labels.pkl'))
    
    results = {
        'Regression': reg_results,
        'Best_Regression': best_reg_name,
        'Classification': clf_results,
        'Best_Classification': best_clf_name,
        'Feature_Importance': feature_imp_dict
    }
    
    with open('/Users/zillekibriya/Desktop/SmartBusStop/scratch/model_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    train_models()
