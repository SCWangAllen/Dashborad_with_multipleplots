import dataclasses
import pathlib
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html, dash, State
import pandas as pd
from dash import dash_table
import os as os
import numpy as np
# import pdpipe as pdp
import io  # 自動檢查資料需要之模組
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.figure_factory as ff  # 畫heatmap的時候用到的
import PlotsGen as pg

SIDEBAR_STYLE = {
    "position": "fixed",
    # "bottom": 0,
    "right": 0,
    'left': 0,
    "padding": "2rem 1rem",
}
pio.templates["nice"] = go.layout.Template(
    layout={
        # Fonts
        # Note - 'family' must be a single string, NOT a list or dict!
        'title':
            {'font': {'family': 'HelveticaNeue-CondensedBold, Helvetica, Sans-serif',
                      'size': 30,
                      'color': '#333'}
             },
        'font': {'family': 'Helvetica Neue, Helvetica, Sans-serif',
                 'size': 16,
                 'color': '#333'},
        # Colorways
        # 'colorway': ['#ec7424', '#a4abab'],
        # Keep adding others as needed below
        'hovermode': 'x unified'
    },
    # DATA
    data={
        # Each graph object must be in a tuple or list for each trace
        'bar': [go.Bar(
            # texttemplate='%{value}',
            textposition='outside',
            textfont={'family': 'Helvetica Neue, Helvetica, Sans-serif',
                      'size': 20,
                      'color': '#FFFFFF'
                      })]
    }
)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    suppress_callback_exceptions=True
)
server = app.server
app.title = 'House Price EDA'


class DataTables:
    DATA: pd.DataFrame = []
    TITLE: str = 'Default'
    LEFT: int = 4
    RIGHT: int = 8

    def __init__(self,
                 data=DATA,
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


sidebar = dbc.Navbar([
    dbc.Container(
        [
            dbc.Row([

                dbc.Col(dbc.NavLink('Home', href='/', active='exact'), width=10),
                dbc.Col(dbc.NavLink('Preview', href='/preview', active='exact'), width=1),
                dbc.Col(dbc.NavLink('DataClean', href='/dataclean', active='exact'), width=1)]),
        ], id='mainnavbar'),
])
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
corrheatmap = pg.HeatMap(data=df_train, heatid='heat1')
dataclass = DataTables(data=df_train)
datainfo = dataclass.gen_tabled_info()
datapreview = dataclass.gen_preview_table(title="Preview", left=0)
datades = dataclass.gen_description_table(title="Description")

app.layout = html.Div(
    [dcc.Location(id='link'), topbar.gen_topbar(), bleow_nav,
     datapreview,
     datainfo,
     datades,
     PBarchart.gen_barcontainer(fig_id='barfig'),
     PLine.gen_linecontainter(fig_id='linefig'),
     PBox.gen_boxcontainer(fig_id='boxfig'),
     corrheatmap.gen_heatmap(title="Correlation Heatmap", id_='heatfig')])


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
def update_bar(State, barx, bary, color,
               barmode: str = 'overlay'):
    barmode = barmode
    fig = PBarchart.gen_updata_bar(columnx=barx, columny=bary, color=color)
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
    prevent_initial_call=True
)
def update_line(State, linex, liney, color, text):
    fig = PLine.gen_updata_line(columnx=linex, columny=liney, color=color, text=text)
    print(color, type(color))
    print(text, type(text))
    return fig


@app.callback(
    Output('boxfig', 'figure'),
    Input('box1_state', 'n_clicks'),
    State('box1_x', 'value'),
    State('box1_y', 'value'),
    State('box1_color', 'value'),
    State('box1_boxmode', 'value'),
    prevent_initial_call=True
)
def update_box(State, boxx, boxy, color, boxmode: str = "overlay"):
    boxmode = boxmode
    fig = PBox.gen_updata(columnx=boxx, columny=boxy, color=color, boxmode=boxmode)
    print(color, type(color))
    print(boxmode, type(boxmode))
    return fig


@app.callback(
    Output('heatfig', 'figure'),
    Output('heat1_var_list', 'children'),
    Input('heat1_state', 'n_clicks'),
    State('heat1_vars', 'value'),
    prevent_initial_call=True
    # State(),
    # State(),
)
def updata_heatmap(State, var):
    print(var)
    var_list = []
    for i in range(len(var)):
        var_list.append(html.Tr(f'{i+1}. {var[i]}'))
    table_body = dbc.Table(html.Tbody(var_list))
    return corrheatmap.gen_update(var=var), table_body


if __name__ == '__main__':
    app.run_server(debug=True, port=3040)
