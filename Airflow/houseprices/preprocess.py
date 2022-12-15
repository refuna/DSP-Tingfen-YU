from pathlib import Path
# from re import M
# from tkinter import E
import pandas as pd
import joblib
import sklearn.preprocessing as sp
import os

airflow_home_folder = os.environ["AIRFLOW_HOME"]

def impute_missing_data(df: pd.DataFrame, is_traning: bool) -> pd.DataFrame:
    list_cols = list(df.columns)
    for col in list_cols:
        if df[col].dtypes == 'number':
            df[col].fillna(0, inplace=True)
        elif df[col].dtypes == 'object':
            df[col].fillna("None", inplace=True)
    return df


def preprocess_continuous_features(df: pd.DataFrame, is_training: bool) -> pd.DataFrame:
    continuous_columns = df.select_dtypes(include='number').columns.tolist()
    continuous_columns = [
        col for col in continuous_columns if col != 'SalePrice']
    sc_path = airflow_home_folder + '/models/sc.joblib'


    if is_training:
        sc = sp.StandardScaler()
        sc.fit(df[continuous_columns])
        joblib.dump(sc, sc_path)
    else:
        if os.path.exists(sc_path):
            sc = joblib.load(sc_path)
        else:
            raise ValueError(
                'scaler not found, \
                please run training before inference')

    scaled_features_df = pd.DataFrame(sc.transform(
        df[continuous_columns]), columns=continuous_columns)
    # df[continuous_columns] = df_scaled

    return scaled_features_df


def preprocess_categorical_features(df: pd.DataFrame, is_training: bool) -> sp.OneHotEncoder:
    one_hot_encoder_path = airflow_home_folder +'/models/OneHotEncoder.joblib'
    categorical_columns = df.select_dtypes(include="object").columns.tolist()
    categorical_df = df[categorical_columns]

    if is_training:
        one_hot_encoder = sp.OneHotEncoder(
            handle_unknown='ignore', sparse_output=True)
        one_hot_encoder.fit(categorical_df)
        joblib.dump(one_hot_encoder, one_hot_encoder_path)
    else:
        if os.path.exists(one_hot_encoder_path):
            one_hot_encoder = joblib.load(one_hot_encoder_path)
        else:
            raise ValueError(
                'one hot encoder not found, \
                please run training before inference')

    categorical_features_sparse = one_hot_encoder.transform(
        categorical_df).toarray()
    categorical_columns = one_hot_encoder.get_feature_names_out()
    categorical_features_df = pd.DataFrame(
        data=categorical_features_sparse,
        columns=categorical_columns, index=categorical_df.index)

    return categorical_features_df


def preprocess(dataframe: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
    df = impute_missing_data(dataframe, is_training)
    continuous_features_df = preprocess_continuous_features(df, is_training)
    categorical_features_df = preprocess_categorical_features(df, is_training)
    return categorical_features_df.join(continuous_features_df)


if __name__ == '__main__':
    df_test = pd.read_csv('./dags/data/new_data/test_data.csv')
    columns = ["SalePrice", "OverallQual", "GrLivArea",
               "GarageArea", "TotalBsmtSF", "Street", "LotShape"]
    feature_columns = columns[1:]
    result = preprocess(df_test[feature_columns], is_training=True)
    print(result.head())


# def df_OneHotEncoder(df: pd.DataFrame,
#                      onehotencoder: sp.OneHotEncoder, is_training: bool) -> pd.DataFrame:
#     cols_ohe = df.select_dtypes(include="object").columns.tolist()
#     df_ohe = df[cols_ohe]
#     encoded_ohe_data = onehotencoder.transform(df_ohe).toarray()
#     encoded_columns = onehotencoder.get_feature_names_out()
#     encoded_ohe_data = pd.DataFrame(
#         data=encoded_ohe_data, columns=encoded_columns, index=df_ohe.index)
#     # encoded_ohe_df = df.copy().drop(cols_ohe, axis=1).join(encoded_ohe_data)
#     return encoded_ohe_data


# def preprocessing_pipe(df: pd.DataFrame) -> pd.DataFrame:
#     # df1 = impute_outlier(df)
#     df2 = impute_missing_data(df)
#     df3 = preprocess_continuous_features(df2)
#     ohe = get_OneHotEncoder(df3)
#     df4 = df_OneHotEncoder(df3, ohe)
#     return df4


# def impute_outlier(df: pd.DataFrame) -> pd.DataFrame:
#     df.drop(['Id', 'PoolQC', 'MiscFeature', 'Alley',
#              'Fence', 'FireplaceQu'], axis=1, inplace=True)
#     df['LotFrontage'] = df.groupby('Neighborhood')['LotFrontage'].transform(
#         lambda x: x.fillna(x.median()))
#     return df


# def categorical_dist(df: pd.DataFrame) -> list:
#     categorical_columns = df.select_dtypes(include="object").columns
#     cols_ordinal = ['BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond',
#                     'ExterQual', 'ExterCond', 'HeatingQC',
#                     'KitchenQual', 'BsmtFinType1', 'BsmtFinType2',
#                     'Functional', 'BsmtExposure', 'GarageFinish',
#                     'LandSlope', 'PavedDrive', 'Street', 'CentralAir']
#     df_ohe = df[categorical_columns].drop((i for i in cols_ordinal), axis=1)
#     cols_ohe = list(df_ohe.columns)
#     return cols_ordinal, cols_ohe


# def get_LabelEncoder(df: pd.DataFrame, models: Path):
#     label_encoder_path = models / 'label_encoder.joblib'
#     cols_ordinal, cols_ohe = categorical_dist(df)
#     if label_encoder_path.exists():
#         encoders = joblib.load(label_encoder_path)
#     else:
#         encoders = {}
#         for col in cols_ordinal:
#             le = sp.LabelEncoder().fit(df[col])
#             encoders[col] = le
#         joblib.dump(encoders, label_encoder_path)
#     return encoders

# def df_LabelEncoder(df: pd.DataFrame,
#                     encoders: sp.LabelEncoder) -> pd.DataFrame:
#     cols_ordinal, cols_ohe = categorical_dist(df)
#     for col in cols_ordinal:
#         le = encoders.get(col)
#         df[col] = le.transform(df[col])
#     return df
