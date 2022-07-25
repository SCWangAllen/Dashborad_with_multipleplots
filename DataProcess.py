import numpy as np
import pandas as pd
import plotly.express as px


class MyDataset:
    def __init__(self,
                 data,
                 label,
                 transform=None):
        self.data = data
        self.label = label
        self.transform = transform

    def __getitem__(self, index):
        return self.data[index], self.label[index]

    def __len__(self):
        return len(self.data)


class Data:
    """
    對data的處理相關函數
    """
    def __init__(self, data):
        self.data = data

    @staticmethod
    def reduce_mem_usage(df: pd.DataFrame):
        """對所有的columns跑一次，並針對每個欄位的資料型態做減少記憶體的使用量\n
           檢查所有不是object的column的最大最小值，去設定該欄位的資料型態，以減少資料使用量。
           numpy.iinfo(type),numpy.finfo(type)\n
           檢查type裡面的limits type(ex:np.int8...)
        """
        origin_mem = df.memory_usage().sum() / 1024 ** 2
        # 轉成MB
        print('Memory usage of dataframe is {:.2f} MB'.format(origin_mem))
        for col in df.columns:
            col_type = df[col].dtype
            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)
                else:
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
            else:
                df[col] = df[col].astype('category')
            end_mem = df.memory_usage().sum() / 1024 ** 2
            print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
            print('Decreased by {:.1f}%'.format(100 * (origin_mem - end_mem) / origin_mem))

            return df
