# Machine Learning Model Report

## 1. Overview
This report summarizes the training and evaluation of machine learning models for the Smart Bus Stop Suitability system. The models act as surrogate decision-support systems to approximate the deterministic Phase 4 Suitability Engine.

## 2. Models Evaluated
### Regression Models (Predicting Suitability Score: 0-100)
- Random Forest Regressor
- Gradient Boosting Regressor

*Note: XGBoost was skipped as it is not installed in the current environment.*

### Classification Models (Predicting Suitability Category)
- Logistic Regression
- Random Forest Classifier
- Gradient Boosting Classifier

## 3. Preprocessing & Data Splits
- **Train/Test Split**: 80% Training, 20% Testing (15,000 total samples -> 12,000 Train, 3,000 Test).
- **Numeric Features**: Standard Scaler applied (`Passenger_Count`, `Boarding`, `Alighting`, `Road_Width`, `Walking_Distance_m`, `Distance_to_Next_Stop_m`, `Bus_Frequency`, `Waiting_Time_min`, `Occupancy_pct`).
- **Categorical Features**: One-Hot Encoding applied (`Traffic_Level`).

## 4. Evaluation Metrics

### Regression Results
| Model | MAE | RMSE | R2 Score |
|---|---|---|---|
| **Random Forest (Best)** | **0.52** | **0.78** | **0.99** |
| Gradient Boosting | 0.90 | 1.17 | 0.98 |

### Classification Results
| Model | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Random Forest (Best)** | **0.938** | **0.938** | **0.938** | **0.936** |
| Logistic Regression | 0.937 | 0.937 | 0.937 | 0.937 |
| Gradient Boosting | 0.922 | 0.923 | 0.922 | 0.919 |

## 5. Feature Importance (Random Forest Regressor)
The surrogate model successfully captured the logic of the deterministic engine:
1. **Passenger_Count**: 36.8%
2. **Walking_Distance_m**: 35.8%
3. **Traffic_Level (High/Low/Med)**: ~21.3% (combined)
4. **Distance_to_Next_Stop_m**: 3.5%
5. **Road_Width**: 1.8%

*Variables not included in the Suitability Formula (e.g., Boarding, Alighting, Bus Frequency) had near 0% importance, proving the model learned the actual suitability rule without capturing noise.*

## 6. Target Circularity & Leakage Analysis
**Important Context**: The dataset features (`Passenger_Count`, `Walking_Distance_m`, etc.) were used to mathematically generate the `Suitability_Score` ground-truth target using the engine rules defined in Phase 4. We then trained an ML model on these exact same features to predict the score. 

This is structurally a form of **circularity/leakage** because the target is perfectly determined by the inputs. The exceptionally high R2 score (0.99) is a direct consequence of this. 

**Conclusion**: The ML model here acts purely as a **Surrogate Model** mapping the rule-based logic. It should be used as a fast, generalizable approximation layer rather than an independent AI discovering hidden ground-truth patterns.

## 7. Artifacts Saved
- `ml/models/best_reg_model.pkl`: The Random Forest Regressor pipeline.
- `ml/models/best_clf_model.pkl`: The Random Forest Classifier pipeline.
- `ml/models/clf_labels.pkl`: The label mappings for categories.
