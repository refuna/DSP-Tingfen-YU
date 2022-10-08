from unittest import result
import joblib

from pathlib import Path
import sys
import pandas as pd 


from preprocess import preprocessing_pipe



def make_predictions(df: pd.DataFrame, model_path: Path) -> int:  
    preprocessed_df = preprocessing_pipe(df)
    model = joblib.load(model_path)
    result = model.predict(preprocessed_df)
    return result
 
if __name__ == '__main__':
    project_dir = Path.cwd()
    model_path = project_dir.parent/ 'models' / 'LGBM_model.joblib'
    df_test = pd.read_csv('../data/test.csv')
    result = make_predictions(df_test, model_path)
    print(result)