from sklearn.model_selection import  KFold
from sklearn.metrics import mean_squared_log_error
from lightgbm import LGBMRegressor
from pathlib import Path
import numpy as np
import pandas as pd
import joblib



import sys
# project_dir = Path.cwd()
# model_dir = project_dir/ 'models'
# model_path = models /'LGBM_model.joblib'
# sys.path.append(str(project_dir))

from  preprocess import preprocessing_pipe



def split_data(df: pd.DataFrame) -> pd.DataFrame:     
    x, y = df.iloc[:, :-1], df["SalePrice"]
    kf = KFold(n_splits=5, random_state=50, shuffle=True)
    for train_index, test_index in kf.split(x, y):
        train_x, test_x = x.iloc[train_index], x.iloc[test_index]
        train_y, test_y = y.iloc[train_index], y.iloc[test_index]
    return train_x, test_x, train_y, test_y


def compute_rmsle(test_y: np.ndarray, pred_test_y: np.ndarray, precision: int = 2) -> float:
    rmsle = np.sqrt(mean_squared_log_error(test_y, pred_test_y))
    return round(rmsle, precision)



def build_model(df: pd.DataFrame, model_path: Path) -> int:
    score = {}
    preprocessed_df = preprocessing_pipe(df)
    model = LGBMRegressor(num_leaves=4, n_estimators=615,learning_rate=0.1,loss='exponential')
    train_x, test_x, train_y, test_y = split_data(preprocessed_df)
    model.fit(train_x, train_y)
    pred_test_y = model.predict(test_x)
    joblib.dump(model, model_path) 
    score['rmse'] = compute_rmsle(test_y, pred_test_y, 2)
    return score

if __name__ == '__main__':
    project_dir = Path.cwd().parent
    model_path = project_dir/ 'models'/'LGBM_model.joblib'
    df = pd.read_csv('../data/train.csv')
    score = build_model(df, model_path)
    print(score) 