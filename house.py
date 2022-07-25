# import dataclasses
# import pathlib
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html, dash, State
import pandas as pd
from dash import dash_table
import os as os
import numpy as np
# import pdpipe as pdp
import io  # 自動檢查資料需要之模組
# import plotly.express as px
# import plotly.graph_objs as go
# import plotly.io as pio
# import plotly.figure_factory as ff  # 畫heatmap的時候用到的
import PlotsGen as pg

SIDEBAR_STYLE = {
    "position": "fixed",
    # "bottom": 0,
    "right": 0,
    'left': 0,
    "padding": "2rem 1rem",
}

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    suppress_callback_exceptions=True
)
server = app.server
app.title = 'House Price EDA'


class DataTables:
    TITLE: str = 'Default'
    LEFT: int = 4
    RIGHT: int = 8

    def __init__(self,
                 data: pd.DataFrame,
                 left=LEFT, ):
        self.data = data
        self.left = left
        self.right = 12 - left

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
    def _get_data_column_data_table(anydf: pd.DataFrame):
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
    def _datable_with_style(data, columns):
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

    def _get_datades_table(self):
        return self._datable_with_style(columns=self._get_data_column_data_table(self._get_data_description()),
                                        data=self._get_data_description().to_dict('records'))

    def gen_tabled_info(self,
                        title: str = TITLE,
                        left: int = LEFT):
        left = left

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
                          left: int = LEFT):
        head = head
        title = title
        left = left
        table = self._datable_with_style(data=self.data.head(head).to_dict('records'),
                                         columns=self._get_data_column_data_table(self.data))
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Markdown(), width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}), table], width=(12 - left))
            ])
        ])

    #
    def gen_description_table(self,
                              title: str = TITLE,
                              left: int = LEFT,
                              round_: int = 5):
        left = left
        title = title
        round_ = round_
        table = self._datable_with_style(
            data=self.data.describe().round(round_).reset_index().to_dict('records'),
            columns=self._get_data_column_data_table(self.data.describe().reset_index()))
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(dcc.Markdown(), width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}), table], width=(12 - left))
            ])
        ])


#
# sidebar = dbc.Navbar([
#     dbc.Container(
#         [
#             dbc.Row([
#
#                 dbc.Col(dbc.NavLink('Home', href='/', active='exact'), width=10),
#                 dbc.Col(dbc.NavLink('Preview', href='/preview', active='exact'), width=1),
#                 dbc.Col(dbc.NavLink('DataClean', href='/dataclean', active='exact'), width=1)]),
#         ], id='mainnavbar'),
# ])
sidebar = html.Div(
    [
        html.H4("Data Review"),
        html.Hr(),
        dbc.Button("選擇資料集", id="select_state", n_clicks=0),
        dbc.Nav(
            [
                # dbc.NavLink("主資料", href="#alldata", external_link=True),  # external_link能讓她強制轉到我想要的頁面
                dbc.NavLink("Bar Chart", href="#barfig", external_link=True),
                dbc.NavLink("Line Chart", href="#linefig", external_link=True),
                dbc.NavLink("Box Chart", href="#boxfig", external_link=True),
                dbc.NavLink("Scatter Plot", href="#scafig", external_link=True),
                dbc.NavLink("Heatmap", href="#heatfig", external_link=True),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id='side_bar'
)
bleow_nav = dbc.Container([
    dbc.Row([
        html.Hr(),
        html.H2("Data Analysis", className="lead", style={'text-align': 'center', 'font-weight': 'bold'}),
        html.Hr(),
    ])
])
df_train = pd.read_csv("E:\\new_Desktop\\python\\Dashborad_with_multipleplots\\train.csv")
df_test = pd.read_csv("E:\\new_Desktop\\python\\Dashborad_with_multipleplots\\test.csv")
topbar = pg.TopNavbar(otherpage=['1', '2', '3'], href=['bar1', "line1", 'heatmap1'])

PBarchart = pg.BarAndDes(data=df_train, barcid='bar1', columnx=df_train.columns[0], columny=df_train.columns[1])
PLine = pg.LineAndDes(data=df_train, linecid='line1', columnx=df_train.columns[0], columny=df_train.columns[1])
PBox = pg.BoxCharts(data=df_train, boxcid='box1', columnx=df_train.columns[0], columny=df_train.columns[1])
PCorrHeatmap = pg.HeatMap(data=df_train, heatid='heat1')
PScatter = pg.ScatterPlots(data=df_train, scaid='sca1')
dataclass = DataTables(data=df_train)
datainfo = dataclass.gen_tabled_info()
datapreview = dataclass.gen_preview_table(title="Preview", left=0)
datades = dataclass.gen_description_table(title="Description")

app.layout = html.Div(
    [
        sidebar,
        dcc.Location(id='link'),
        # topbar.gen_topbar(),
        bleow_nav,
        datapreview,
        datainfo,
        datades,
        PBarchart.gen_barcontainer(fig_id='barfig'),
        PLine.gen_linecontainter(fig_id='linefig'),
        PBox.gen_boxcontainer(fig_id='boxfig'),
        PScatter.gen_scacon(fig_id='scafig', x=df_train.columns[0], y=df_train.columns[-1]),
        PCorrHeatmap.gen_heatmap(title="Correlation Heatmap", id_='heatfig')])


# barchart callback
@app.callback(
    Output('barfig', 'figure'),
    # Output('bar1_content', "children"),
    Input('bar1_state', 'n_clicks'),
    State('bar1_x', 'value'),
    State('bar1_y', 'value'),
    State('bar1_color', 'value'),
    # State('bar1_text', 'value'),
    State('bar1_barmode', 'value'),
    prevent_initial_call=True
)
def update_bar(state, barx, bary, color,
               barmode: str = 'overlay'):
    print(state)
    barmode = barmode
    fig = PBarchart.gen_updata_bar(columnx=barx, columny=bary, color=color, )
    fig.update_layout(barmode=barmode)
    # fig.update_layout(color=color)
    print(color, type(color))
    return fig


# linechart callback
@app.callback(
    Output('linefig', 'figure'),
    Input('line1_state', 'n_clicks'),
    State('line1_x', 'value'),
    State('line1_y', 'value'),
    State('line1_color', 'value'),
    State('line1_text', 'value'),
    # Input('line1_x', 'value'),
    # Input('line1_y', 'value'),
    prevent_initial_call=True
)
def update_line(State, linex, liney, color, text):
    fig = PLine.gen_updata_line(columnx=linex, columny=liney, color=color, text=text)
    # fig.update_layout(yaxis=dict)
    print(color, type(color))
    print(text, type(text))
    return fig


@app.callback(
    Output('line1_xy_range_word', 'children'),
    Input('line1_x', 'value'),
    Input('line1_y', 'value'),
    prevent_initial_call=True
)
def show_maxin(x, y):
    while x is not None and y is not None:
        x_max = PLine.data[x].max()
        x_min = PLine.data[x].min()
        y_max = PLine.data[y].max()
        y_min = PLine.data[y].min()
        table_body = dbc.Table(html.Tbody([html.Tr(f'x_max={x_max}'),
                                           html.Tr(f'x_min={x_min}'),
                                           html.Tr(f'y_max={y_max}'),
                                           html.Tr(f'y_min={y_min}')]))
        # print(x)
        # print(y)
        # print(PLine.data.columns)
        # print(x_max, y_max)
        return table_body


@app.callback(
    Output('boxfig', 'figure'),
    Input('box1_state', 'n_clicks'),
    State('box1_x', 'value'),
    State('box1_y', 'value'),
    State('box1_color', 'value'),
    State('box1_boxmode', 'value'),
    prevent_initial_call=True
)
def update_box(state, boxx, boxy, color, boxmode: str = "overlay"):
    print(state)
    boxmode = boxmode
    fig = PBox.gen_updata(columnx=boxx, columny=boxy, color=color, boxmode=boxmode)
    print(color, type(color))
    print(boxmode, type(boxmode))
    return fig


@app.callback(
    Output('sca1_xy_range_word', 'children'),
    Input('sca1_x', 'value'),
    Input('sca1_y', 'value'),
    prevent_initial_call=True
)
def show_maxin(x, y):
    while x is not None and y is not None:
        x_max = PScatter.data[x].max()
        x_min = PScatter.data[x].min()
        y_max = PScatter.data[y].max()
        y_min = PScatter.data[y].min()
        table_body = dbc.Table(html.Tbody([html.Tr(f'x_max={x_max}'),
                                           html.Tr(f'x_min={x_min}'),
                                           html.Tr(f'y_max={y_max}'),
                                           html.Tr(f'y_min={y_min}')]))
        # print(x)
        # print(y)
        # print(PLine.data.columns)
        # print(x_max, y_max)
        return table_body


@app.callback(
    Output('scafig', 'figure'),
    Input('sca1_state', 'n_clicks'),
    State('sca1_x', 'value'),
    State('sca1_y', 'value'),
    State('sca1_color', 'value'),
    State('sca1_width', 'value'),
    State('sca1_height', 'value'),
    State('sca1_x_range_max', 'value'),
    State('sca1_x_range_min', 'value'),
    State('sca1_y_range_max', 'value'),
    State('sca1_y_range_min', 'value'),
    # State('sca1_boxmode', 'value'),
    prevent_initial_call=True
)
def updata_sca(state, x, y, color, width, height, x_range_max, x_range_min, y_range_max, y_range_min, ):
    print(state)
    if x_range_max is not None and x_range_min is not None:
        x_range = [int(x_range_min), int(x_range_max)]
    else:
        x_range = None
    if y_range_min is not None and y_range_max is not None:
        y_range = [int(y_range_min), int(y_range_max)]
    else:
        y_range = None
    if width is not None and height is not None:
        return PScatter.gen_scatter(columny=y, columnx=x, color=color, width=int(width), height=int(height),
                                    x_range=x_range,
                                    y_range=y_range,
                                    tmeplate='nice')
    else:
        return PScatter.gen_scatter(columny=y, columnx=x, color=color,
                                    x_range=x_range,
                                    y_range=y_range,
                                    tmeplate='nice')


@app.callback(
    Output('heatfig', 'figure'),
    Output('heat1_var_list', 'children'),
    Input('heat1_state', 'n_clicks'),
    State('heat1_vars', 'value'),
    prevent_initial_call=True
    # State(),
    # State(),
)
def updata_heatmap(state, var):
    print(state)
    var_list = []
    for i in range(len(var)):
        var_list.append(html.Tr(f'{i + 1}. {var[i]}'))
    table_body = dbc.Table(html.Tbody(var_list))
    return PCorrHeatmap.gen_update(var=var), table_body


if __name__ == '__main__':
    app.run_server(debug=True, port=3040)
