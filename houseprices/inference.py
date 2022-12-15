import joblib
import pandas as pd

from houseprices.preprocess import preprocess


def make_predictions(df: pd.DataFrame) -> int:
    preprocessed_df = preprocess(df)
    # print(preprocessed_df.head(1))
    model = joblib.load('models/LGBM_model.joblib')
    result = model.predict(preprocessed_df)
    return result


if __name__ == '__main__':
    df_test = pd.read_csv('data/test.csv')
    columns = ["SalePrice", "OverallQual", "GrLivArea",
               "GarageArea", "TotalBsmtSF", "Street", "LotShape"]
    feature_columns = columns[1:]
    result = make_predictions(df_test[feature_columns])
    print(result)
