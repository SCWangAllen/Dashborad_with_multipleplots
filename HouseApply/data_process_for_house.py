import numpy as np
import pandas as pd
from scipy.stats import norm, skew
df_train_after = pd.read_csv("/train.csv")
df_train_after.drop("Id", axis=1, inplace=True)
df_test_after = pd.read_csv("/test.csv")
df_test_after.drop("Id", axis=1, inplace=True)
df_train_after = df_train_after.drop(
    df_train_after[(df_train_after['GrLivArea'] > 4000) & (df_train_after['SalePrice'] < 300000)].index)
# 去除了兩個資料點而已
nsoftrain = df_train_after.shape[0]
nsoftest = df_test_after.shape[0]
# 對y取log 沒有對y取log的話，跑出來的rmse會相當大
df_train_after["SalePrice"] = np.log1p(df_train_after["SalePrice"])
y_train = df_train_after.SalePrice.values
whole_data = pd.concat((df_train_after, df_test_after)).reset_index(drop=True)
whole_data.drop(['SalePrice'], axis=1, inplace=True)

# NA圖形以及數據處理
whole_data_na = (whole_data.isnull().sum() / len(whole_data)) * 100
whole_data_na = whole_data_na.drop(whole_data_na[whole_data_na == 0].index).sort_values(ascending=False)
miss_data = pd.DataFrame({'Missing Ratio': whole_data_na})
miss_data = miss_data.reset_index()  # 轉成dataFrame才能被我的class使用

# 處理NA值
for col in ('GarageType', 'GarageFinish', 'GarageQual', 'GarageCond'):
    whole_data[col] = whole_data[col].fillna('None')
for col in ('GarageYrBlt', 'GarageArea', 'GarageCars'):
    whole_data[col] = whole_data[col].fillna(0)
for col in ('BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2'):
    whole_data[col] = whole_data[col].fillna('None')
for col in ('BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF', 'TotalBsmtSF', 'BsmtFullBath', 'BsmtHalfBath'):
    whole_data[col] = whole_data[col].fillna(0)
whole_data['MiscFeature'] = whole_data['MiscFeature'].fillna("None")
whole_data['Alley'] = whole_data['Alley'].fillna("None")
whole_data["FireplaceQu"] = whole_data["FireplaceQu"].fillna("None")
whole_data["Fence"] = whole_data["Fence"].fillna("None")
whole_data["PoolQC"] = whole_data["PoolQC"].fillna("None")
whole_data["LotFrontage"] = whole_data.groupby("Neighborhood")["LotFrontage"].transform(
    lambda x: x.fillna(x.median()))

whole_data["MasVnrType"] = whole_data["MasVnrType"].fillna("None")
whole_data["MasVnrArea"] = whole_data["MasVnrArea"].fillna(0)

whole_data['MSZoning'] = whole_data['MSZoning'].fillna(whole_data['MSZoning'].mode()[0])
whole_data = whole_data.drop(['Utilities'], axis=1)

whole_data["Functional"] = whole_data["Functional"].fillna("Typ")

whole_data['Electrical'] = whole_data['Electrical'].fillna(whole_data['Electrical'].mode()[0])
whole_data['KitchenQual'] = whole_data['KitchenQual'].fillna(whole_data['KitchenQual'].mode()[0])
whole_data['Exterior1st'] = whole_data['Exterior1st'].fillna(whole_data['Exterior1st'].mode()[0])
whole_data['Exterior2nd'] = whole_data['Exterior2nd'].fillna(whole_data['Exterior2nd'].mode()[0])
whole_data['SaleType'] = whole_data['SaleType'].fillna(whole_data['SaleType'].mode()[0])
whole_data['MSSubClass'] = whole_data['MSSubClass'].fillna("None")

# Feature generation
# 年度以及月份應該是類別資料，而不是數值
whole_data['YrSold'] = whole_data['YrSold'].astype(str)
whole_data['MoSold'] = whole_data['MoSold'].astype(str)

# MSSubClass在資料敘述中，是代表銷售種類，只是這邊用數值呈現
whole_data['MSSubClass'] = whole_data['MSSubClass'].apply(str)

# 房子的大致狀況，在資料敘述中，為類別變數。
whole_data['OverallCond'] = whole_data['OverallCond'].astype(str)

# labelEncoding
from sklearn.preprocessing import LabelEncoder

cols = ('FireplaceQu', 'BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond',
        'ExterQual', 'ExterCond', 'HeatingQC', 'PoolQC', 'KitchenQual', 'BsmtFinType1',
        'BsmtFinType2', 'Functional', 'Fence', 'BsmtExposure', 'GarageFinish', 'LandSlope',
        'LotShape', 'PavedDrive', 'Street', 'Alley', 'CentralAir', 'MSSubClass', 'OverallCond',
        'YrSold', 'MoSold')
# process columns, apply LabelEncoder to categorical features
for c in cols:
    lbl = LabelEncoder()
    lbl.fit(list(whole_data[c].values))
    whole_data[c] = lbl.transform(list(whole_data[c].values))

whole_data['TotalSF'] = whole_data['TotalBsmtSF'] + whole_data['1stFlrSF'] + whole_data['2ndFlrSF']
# 儲存還沒處理skew資料，要畫和鬚圖
whole_data_bskew = whole_data

# 處理skewness
numeric = whole_data.dtypes[whole_data.dtypes != "object"].index

skewed_feats = whole_data[numeric].apply(lambda x: skew(x)).sort_values(ascending=False)
print("\nSkew in numerical features: \n")
skewness = pd.DataFrame({'Skew': skewed_feats})
skewness = skewness[abs(skewness) > 0.75]

from scipy.special import boxcox1p

skewed_features = skewness.index
lam = 0.15
for feat in skewed_features:
    # all_data[feat] += 1
    whole_data[feat] = boxcox1p(whole_data[feat], lam)

whole_data_askew = whole_data
