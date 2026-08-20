import joblib
import pandas as pd
import os

MODEL_DIR = '/Users/zillekibriya/Desktop/SmartBusStop/ml/models'

def load_models():
    reg_model = joblib.load(os.path.join(MODEL_DIR, 'best_reg_model.pkl'))
    clf_model = joblib.load(os.path.join(MODEL_DIR, 'best_clf_model.pkl'))
    labels = joblib.load(os.path.join(MODEL_DIR, 'clf_labels.pkl'))
    return reg_model, clf_model, labels

def predict(input_data):
    """
    input_data should be a dict or dataframe with the expected features.
    """
    df = pd.DataFrame([input_data])
    reg_model, clf_model, labels = load_models()
    
    score = reg_model.predict(df)[0]
    cat_idx = clf_model.predict(df)[0]
    category = labels[cat_idx]
    
    return {
        'Predicted_Score': score,
        'Predicted_Category': category
    }

if __name__ == '__main__':
    sample = {
        'Passenger_Count': 85,
        'Boarding': 40,
        'Alighting': 45,
        'Road_Width': 12,
        'Walking_Distance_m': 300,
        'Distance_to_Next_Stop_m': 600,
        'Traffic_Level': 'Moderate',
        'Bus_Frequency': 10,
        'Waiting_Time_min': 5,
        'Occupancy_pct': 70
    }
    print("Inference Test:")
    print(predict(sample))
