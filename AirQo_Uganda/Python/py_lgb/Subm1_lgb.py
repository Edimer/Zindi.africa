# Importando bibliotecas
import pandas as pd
import lightgbm as lgb
import numpy as np
from sklearn.model_selection import train_test_split

# Datos train
nombres_train = pd.read_csv('../my_data/nombres_train.csv', header=None, sep=',')

df_train = pd.read_csv('../my_data/df_ancha_train.csv', names = nombres_train[1:][0],
                       header=None, sep=',', encoding = "latin",)[1:]
df_train.head(10)

# Datos test
nombres_test = pd.read_csv('../my_data/nombres_test.csv', header=None, sep=',')
df_test = pd.read_csv('../my_data/df_ancha_test.csv', names = nombres_test[1:][0],
                       header=None, sep=',', encoding = "latin",)[1:]
df_test.head(10) 

# Coerción a numérico
cols = df_train.columns.drop(["ID"])
df_train[cols] = df_train[cols].apply(pd.to_numeric, errors='coerce')

colsT = df_test.columns.drop(["ID"])
df_test[colsT] = df_test[colsT].apply(pd.to_numeric, errors='coerce')

# Split data
df_train2, df_test2 = train_test_split(df_train, test_size = 0.2, random_state = 123)

# Datos para entrenamiento del modelo
y_train = df_train2["target"]
y_test = df_test2["target"]
X_train = df_train2.drop(["ID", "target"], axis=1)
X_test = df_test2.drop(["ID", "target"], axis=1)

# Dataset lgb, igual que para XGBoost
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

# Parámetros del modelo
params = {
    'boosting_type': 'gbdt',
    'objective': 'regression',
    'metric': {'rmse'},
    'num_leaves': 350,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.9,
    'bagging_freq': 5,
    'verbose': 0,
    'max_depth': -1,
    'max_bin': 125
}

# Cross Validation
print('Starting training...')
gbm_cv = lgb.cv(params,
                lgb_train,
                num_boost_round=10000,
                early_stopping_rounds=20,
                nfold=10,
                stratified=False,
                seed=123,
                categorical_feature=["location"])
best_round = len(gbm_cv['rmse-mean'])

# Modelo con best_iterations
gbm = lgb.train(params,
                lgb_train,
                num_boost_round=best_round,
                valid_sets=lgb_eval,
                early_stopping_rounds=20,
                categorical_feature=["location"])

# Predicciones Test (submission)
print('Starting predict...')
predichos = gbm.predict(data=df_test.drop(["ID"], axis = 1))
predichos

# Exportando predicciones
mi_array = {'ID': df_test['ID'],
            'target': predichos}
          
s1_lgb = pd.DataFrame(data = mi_array)
s1_lgb.to_csv('submissions/s1_lgb.csv', index = False, header=True)

