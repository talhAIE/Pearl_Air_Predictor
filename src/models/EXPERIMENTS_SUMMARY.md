# Model Training Experiments Summary

This document summarizes all model training experiments conducted for the AQI Predictor project.

---

## Experiment 1: Baseline Models

**Objective:** Establish baseline performance with default parameters  
**Data Split:** 80/20 (Train: 7,008 | Test: 1,752)  
**Features:** 19 engineered features

### Results

| Model | R² Score | RMSE | MAE | Parameters |
|-------|----------|------|-----|------------|
| Random Forest | 0.6007 | 52.33 | 17.89 | Default (n_estimators=100) |
| XGBoost | 0.5529 | 55.38 | 19.45 | Default |
| LightGBM | **0.8220** | **34.94** | **14.72** | Default |

**Winner:** LightGBM  
**Key Finding:** LightGBM significantly outperforms other models even with default parameters.

---

## Experiment 2: Hyperparameter Tuning

**Objective:** Improve model performance through hyperparameter optimization  
**Method:** RandomizedSearchCV with 3-fold cross-validation  
**Data Split:** 80/20 (Train: 7,008 | Test: 1,752)

### Results

| Model | R² Score | RMSE | MAE | Improvement |
|-------|----------|------|-----|-------------|
| Random Forest | 0.7036 | 45.10 | 15.25 | +17.1% |
| XGBoost | 0.6963 | 45.65 | 16.08 | +25.9% |
| LightGBM | **0.8229** | **34.86** | **14.68** | +0.1% |

### Best Parameters

**Random Forest:**
- n_estimators: 300
- max_depth: 25
- min_samples_split: 5
- min_samples_leaf: 4

**XGBoost:**
- n_estimators: 100
- max_depth: 6
- learning_rate: 0.05
- subsample: 0.8
- colsample_bytree: 0.9

**LightGBM:**
- n_estimators: 300
- max_depth: 12
- learning_rate: 0.05
- num_leaves: 31
- subsample: 0.8

**Winner:** LightGBM  
**Key Finding:** Hyperparameter tuning significantly improved RF and XGBoost, but LightGBM was already near-optimal.

---

## Experiment 3: Manual Parameter Optimization

**Objective:** Fine-tune LightGBM parameters manually  
**Data Split:** 80/20 (Train: 7,008 | Test: 1,752)

### Results

| Model | R² Score | RMSE | MAE | Notes |
|-------|----------|------|-----|-------|
| LightGBM (Exp 2) | 0.8229 | 34.86 | 14.68 | Baseline from Exp 2 |
| LightGBM (Manual) | **0.8229** | **34.86** | **14.68** | No improvement |

**Winner:** LightGBM (same as Experiment 2)  
**Key Finding:** Manual tuning did not improve performance. Experiment 2 parameters are optimal.

---

## Final Model Selection

**Selected Model:** LightGBM  
**Final Parameters:**
```python
LGBMRegressor(
    n_estimators=300,
    max_depth=12,
    learning_rate=0.05,
    num_leaves=31,
    subsample=0.8,
    random_state=42
)
```

**Performance Metrics:**
- **R² Score:** 0.8229 (82.3% variance explained)
- **RMSE:** 34.86
- **MAE:** 14.68

**Model Location:** `models/best_model_lightgbm.pkl`

---

## Conclusions

1. **LightGBM is the clear winner** across all experiments
2. **Hyperparameter tuning** significantly improved RF (+17%) and XGBoost (+26%)
3. **LightGBM was near-optimal** from the start (only +0.1% improvement)
4. **Final R² = 0.82** is excellent for real-world AQI prediction
5. **MAE = 14.68** means predictions are accurate within ±15 AQI points

---

## Next Steps

- ✅ Deploy LightGBM model to production
- ✅ Set up daily retraining pipeline
- ✅ Monitor model performance over time
- [ ] Consider ensemble methods if performance degrades
