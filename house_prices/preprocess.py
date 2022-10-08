from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import sklearn.preprocessing as sp

project_dir = Path.cwd()
# encoder_dir = project_dir/'encoders'
model_dir = project_dir.parent/ 'models'


def impute_outlier(df: pd.DataFrame) -> pd.DataFrame:
    df.drop(['Id', 'PoolQC', 'MiscFeature', 'Alley', 'Fence', 'FireplaceQu'], axis= 1, inplace=True)
    # df.drop(df[(df['GrLivArea']>4000) & (df['SalePrice']<300000)].index, inplace=True)
    # df.drop(df[df['TotalBsmtSF']> 5000].index, inplace=True)
    df['LotFrontage'] = df.groupby('Neighborhood')['LotFrontage'].transform(lambda x: x.fillna(x.median()))
    return df



def impute_missing_data(df: pd.DataFrame) -> pd.DataFrame:
    list_cols = list(df.columns)
    for col in list_cols:
        if df[col].dtypes == 'number':
            df[col].fillna(0, inplace=True)
        elif df[col].dtypes == 'object':
            df[col].fillna("None", inplace=True)
    return df




def categorical_dist(df: pd.DataFrame) -> list:
    categorical_columns = df.select_dtypes(include="object").columns
    cols_ordinal = ['BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond', 'ExterQual','ExterCond', 
                    'HeatingQC', 'KitchenQual', 'BsmtFinType1', 'BsmtFinType2','Functional', 'BsmtExposure', 
                    'GarageFinish', 'LandSlope','PavedDrive', 'Street', 'CentralAir'] 
    df_ohe = df[categorical_columns].drop((i for i in cols_ordinal), axis=1)
    cols_ohe = list(df_ohe.columns) 
    return cols_ordinal, cols_ohe
    

def get_OneHotEncoder(df: pd.DataFrame, models: Path) -> sp.OneHotEncoder:
    one_hot_encoder_path = models / 'one_hot_encoder.joblib'
    cols_ohe = df.select_dtypes(include="object").columns.tolist()
    if one_hot_encoder_path.exists():
        one_hot_encoder = joblib.load(one_hot_encoder_path)
    else:
        df_ohe = df[cols_ohe]
        one_hot_encoder = sp.OneHotEncoder(handle_unknown='ignore', sparse=True)
        one_hot_encoder.fit(df_ohe)
        joblib.dump(one_hot_encoder, one_hot_encoder_path)
    return one_hot_encoder

def df_OneHotEncoder(df: pd.DataFrame, onehotencoder: sp.OneHotEncoder )-> pd.DataFrame:
    cols_ohe = df.select_dtypes(include="object").columns.tolist()
    df_ohe = df[cols_ohe]
    encoded_ohe_data = onehotencoder.transform(df_ohe).toarray()
    encoded_columns = onehotencoder.get_feature_names_out()
    encoded_ohe_data = pd.DataFrame(data=encoded_ohe_data, columns=encoded_columns, index=df_ohe.index)
    encoded_ohe_df = df.copy().drop(cols_ohe, axis=1).join(encoded_ohe_data)
    return encoded_ohe_df

def get_LabelEncoder(df: pd.DataFrame, models: Path):
    label_encoder_path = models / 'label_encoder.joblib'
    cols_ordinal, cols_ohe = categorical_dist(df)
    if label_encoder_path.exists():
        encoders = joblib.load(label_encoder_path)
    else:
        encoders = {}   
        for col in cols_ordinal:
            le = sp.LabelEncoder().fit(df[col])
            encoders[col] = le
        joblib.dump(encoders, label_encoder_path)
    return encoders
    

def df_LabelEncoder(df: pd.DataFrame, encoders: sp.LabelEncoder) -> pd.DataFrame:    
    cols_ordinal, cols_ohe = categorical_dist(df)
    for col in cols_ordinal:
        le = encoders.get(col)
        df[col] = le.transform(df[col])
    return df


def scaled_data(df: pd.DataFrame) -> pd.DataFrame:
    continuous_columns = df.select_dtypes(include='number').columns.tolist()
    sc = sp.StandardScaler()
    if 'SalePrice' in df.columns:
        scaled_clos = df[continuous_columns].drop(['SalePrice'], axis=1).columns.tolist()
        df_scaled = pd.DataFrame(sc.fit_transform(df[scaled_clos]), columns = scaled_clos)
        df[scaled_clos] = df_scaled
    else:
        df_scaled = pd.DataFrame(sc.fit_transform(df[continuous_columns]), columns = continuous_columns)
        df[continuous_columns] = df_scaled  
    return df
        
        
def preprocessing_pipe(df: pd.DataFrame) -> pd.DataFrame:
    df1 = impute_outlier(df)
    df2 = impute_missing_data(df1)  
    df3 = scaled_data(df2)
    ohe = get_OneHotEncoder(df3, model_dir)
    df4 = df_OneHotEncoder(df3, ohe)
    return df4


df = pd.read_csv('../data/train.csv')
df_pre = preprocessing_pipe(df)
print(df_pre.head())