import joblib
import pandas as pd
import os
from houseprices.preprocess import preprocess
# from preprocess import preprocess

airflow_home_folder = os.environ["AIRFLOW_HOME"]


def make_predictions(df: pd.DataFrame) -> int:
    preprocessed_df = preprocess(df, is_training=False)
    # print(preprocessed_df.head(1))
    model = joblib.load(airflow_home_folder + '/models/LGBM_model.joblib')
    result = model.predict(preprocessed_df)
    return result


if __name__ == '__main__':
    df_test = pd.read_csv('./dags/data/new_data/test_data.csv')
    columns = ["SalePrice", "OverallQual", "GrLivArea",
               "GarageArea", "TotalBsmtSF", "Street", "LotShape"]
    feature_columns = columns[1:]
    result = make_predictions(df_test[feature_columns])
    print(result)
