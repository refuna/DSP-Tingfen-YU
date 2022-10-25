import pandas as pd
import numpy as np

df = pd.read_csv('./data/test.csv')
df.head()
columns = ["OverallQual", "GrLivArea", "GarageArea", "TotalBsmtSF"]
df[columns].head()

# 6        896       730.0        882.0