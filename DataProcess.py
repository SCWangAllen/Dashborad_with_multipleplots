import dash_bootstrap_components
import numpy as np
import pandas as pd
# import plotly.express as px
from dash import dash_table
import io  # 自動檢查資料需要之模組
import dash_bootstrap_components as dbc
from dash import dcc, html
import PlotsGen


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

    def __init__(self, data: pd.DataFrame):
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

    def group_by_vc(self, columns: list, othcol, ):
        df = (self.data.
              groupby(columns)[othcol].
              value_counts().
              to_frame().
              rename(columns={othcol: f'{othcol}_count'}))
        return df


class DataTables(PlotsGen.Settings):
    TITLE: str = 'Default'
    TFOPTIONS = [{"label": "True", 'value': True},
                 {'label': "False", 'value': False}]

    def __init__(self, data: pd.DataFrame = None, left: int = None):

        super().__init__()
        if left is None:
            self.left = self.LEFT
        self.data = data
        self.right = 12 - self.left

    # pd.description的reformat再輸出
    def _get_data_description(self):
        buffer = io.StringIO()
        self.data.info(buf=buffer)
        lines = buffer.getvalue().splitlines()
        details = (pd.DataFrame([x.split() for x in lines[5:-2]], columns=lines[3].split())
                   .drop('Count', axis=1)
                   .rename(columns={'Non-Null': 'Non-Null Count'})
                   .rename(columns={'#': 'number'}))
        unique_value = []
        for i in self.data.columns:
            unique_value.append(len(self.data[i].unique()))
        details['unique'] = unique_value
        return details

    # 將任何DF的column調成datatable的column的輸出結構
    @staticmethod
    def get_data_column_data_table(anydf: pd.DataFrame):
        column = anydf.columns.to_list()
        labels = []
        for i in column:
            x = {
                "name": i,
                "id": i
            }
            labels.append(x)
        return labels

    # 將任何DF轉成我想要的dataframe樣子，樣式可以在class固定變數調整裡面調整

    @staticmethod
    def datable_with_style(data, columns):
        table_header_style = {
            'background-color': 'rgb(210, 210, 210)',
            'font-weight': 'bold',
            'font-size': '12px',
            'text-align': 'left',
        }
        table_data_style = {
            'font-size': '12px',
            'text-align': 'left',
            'whiteSpace': 'none',
            'height': 'auto',
            'lineHeight': '15px',
            'width': "50px"
        }
        table_cell_style = {
            "padding": "5px",
            "height": "auto",
            "minWidth": "100px",
            "width": "1o0px",
            "maxWidth": "100px",  # all three widths are needed
            "whiteSpace": "normal",  #
        }
        table_style = {"overflow": "hidden",
                       "padding": "15px", }
        return dash_table.DataTable(
            columns=columns,
            data=data,
            # style_table={'margin-top': '100px'},
            style_header=table_header_style,
            style_data=table_data_style,
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'background-color': '#cfd8dc'}],
            sort_action="native",
            sort_mode="single",  # 排序模式
            style_table=table_style,
            style_cell=table_cell_style,
            page_size=11,
            # fixed_columns={'headers': True, 'data': 2},
            fixed_rows={'headers': True, 'data': 0}
        )

    # 產生groupby後的dataframe
    def group_by_vc(self, columns: list, othcol=None, ):

        df = (self.data.
              groupby(columns)[othcol].
              value_counts().
              to_frame().
              rename(columns={othcol: f'{othcol}_count'}).
              reset_index())

        return df

    def group_by_value(self, columns, univals=None):
        while univals is None:
            df = (self.data.
                  groupby(columns).
                  get_group(self.data[columns].unique[0]))
        else:
            df = (self.data.
                  groupby(columns).
                  get_group(univals))
        return df

    def _get_datades_table(self):
        return self.datable_with_style(data=self._get_data_description().to_dict('records'),
                                       columns=self.get_data_column_data_table(self._get_data_description()))

    def gen_tabled_info(self,
                        title: str = TITLE,
                        left: int = None):
        if left is None:
            left = self.LEFT
        table = self._get_datades_table()
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(dcc.Markdown('''  ''', style={'font-family': '標楷體', 'padding': '15px', 'font-size': '20px'}),
                        width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}), table], width=(12 - left))
            ])
        ])

    def gen_preview_table(self,
                          title: str = TITLE,
                          head: int = 500,
                          left: int = None):

        if left is None:
            left = self.LEFT
        table = self.datable_with_style(data=self.data.head(head).to_dict('records'),
                                        columns=self.get_data_column_data_table(self.data))
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Markdown(), width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}), table], width=(12 - left))
            ])
        ])

    #
    def gen_description_table(self,
                              title: str = TITLE,
                              left: int = None,
                              round_: int = 5):
        if left is None:
            left = self.LEFT
        # left = left
        # title = title
        # round_ = round_
        table = self.datable_with_style(data=self.data.describe().round(round_).reset_index().to_dict('records'),
                                        columns=self.get_data_column_data_table(self.data.describe().reset_index()))
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(dcc.Markdown(), width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}), table], width=(12 - left))
            ])
        ])

    def gen_groupby_table(self,
                          title: str = TITLE,
                          left: int = None,
                          id_: str = None,
                          cols: list = None,
                          othcols: str = None,
                          ):
        if left is None:
            left = self.LEFT
        gdata = self.group_by_vc(columns=cols, othcol=othcols)
        table = self.datable_with_style(data=gdata.to_dict('records'), columns=self.get_data_column_data_table(gdata))

        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.H4('Settings', style={'text-align': 'center'}),
                    dcc.Dropdown(options=[
                        {'label': 'by value', "value": 'by value'},
                        {'label': 'by_col', "value": 'by_col'},
                    ],
                        placeholder='Group by col or values'
                    ),
                    html.Div([
                        dbc.InputGroup(
                            [dbc.InputGroupText("GroupBy", id='groupby_text'),
                             dbc.Select(options=self.get_select(self.data),
                                        id=f'{id_}_x',
                                        placeholder="Choose col"),
                             dbc.InputGroupText("v or c", id='groupby_vorc'),
                             dbc.Select(options=self.get_select(gdata),
                                        id=f'{id_}_y',
                                        placeholder="Choose col"),
                             ]
                        ),
                        dbc.InputGroup(
                            [dbc.InputGroupText("Filter", id='group_filter'),
                             dbc.Select(options=self.TFOPTIONS,
                                        id=f'{id_}_value', ),
                             # dbc.InputGroupText("Aggregate", ),
                             # dbc.Select(options=self.TFOPTIONS, id=f'{id_}_aggr', ),
                             ]
                        ),
                        # dbc.InputGroup([
                        #     dbc.InputGroupText("count"),
                        #     dbc.Input(id=f'{id_}_count', )
                        # ]),
                        html.Div([
                            self.gen_data_dropdown(data=gdata, top_id=id_,
                                                   id_='filter', multi=True, placeholder="Fliter")
                        ]),
                        html.Div([
                            dbc.InputGroupText("Function"),
                            dcc.Dropdown(options=[
                                {'label': 'Aggregate', "value": 'Aggregate'},
                                {'label': 'fun2', "value": 'fun2'},
                                {'label': 'fun3', "value": 'fun3'},
                            ], multi=False, id=f'{id_}_lambda')
                        ])
                    ])
                ], width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}), table, ],
                        width=(12 - left), id=f'{id_}_gr_vc')
            ])
        ], id=id_)
