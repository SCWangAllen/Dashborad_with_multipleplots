import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html, dash, State
import pandas as pd
from dash import dash_table
import os as os
import numpy as np
# import pdpipe as pdp

# import plotly.express as px
# import plotly.graph_objs as go
# import plotly.io as pio
# import plotly.figure_factory as ff  # 畫heatmap的時候用到的
import PlotsGen as pg
import DataProcess as dp
import data_process_for_house as dh

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

df_train = pd.read_csv("/train.csv")
df_train = dp.Data.reduce_mem_usage(df_train)
df_test = pd.read_csv("/test.csv")

# 上面是給初始資料看得


# missbar = pg.BarAndDes(data=miss_data, barcid='miss', title="MissValue Condition").gen_barcontainer(columnx='index',
#                                                                                                     columny='Missing '
#                                                                                                             'Ratio',
#                                                                                                     fig_id='missbar')
missbar = pg.BarAndDes(data=dh.miss_data).gen_updata_bar(columnx='index', columny='Missing Ratio', title="NA Condition")

# Heatmap
PCorrHeatmap = pg.HeatMap(data=df_train, heatid='heat1')

dataclass = dp.DataTables(data=df_train)
datainfo = dataclass.gen_tabled_info(title='Data Info')
datapreview = dataclass.gen_preview_table(title="Data Preview", left=0)
# topbar = pg.TopNavbar(otherpage=['1', '2', '3'], href=['bar1', "line1", 'heatmap1'])
PScatter = pg.ScatterPlots(data=df_train, scaid='sca1')
PDis = pg.Displot(data=df_train, disid='dis1')

# BOX before skew 處理
numericcols = dh.whole_data_bskew.dtypes[dh.whole_data_bskew.dtypes != "object"].index
PBox = pg.BoxCharts(data=dh.whole_data_bskew[numericcols], boxcid='box1', title="before dealing with skewness")
PBox2 = pg.BoxCharts(data=dh.whole_data_askew[numericcols], boxcid='box2', title='After dealing with skewness')

bleow_nav = dbc.Container([
    dbc.Row([
        html.Hr(),
        html.H2("Data Analysis", className="lead", style={'text-align': 'center', 'font-weight': 'bold'}),
        html.Hr(),
    ])
], style={'min-height': '0px'})
app.layout = html.Div(
    [
        sidebar, dcc.Location(id='link', ),
        bleow_nav,
        datapreview,
        datainfo,
        PScatter.gen_scacon(fig_id='scafig', x=df_train.columns[0], y=df_train.columns[-1]),
        PDis.gen_dis_con(fig_id='disfig', hist_data=[df_train.columns[-1]], group_labels=df_train.columns[-1]),
        dbc.Container([html.Hr(), dcc.Graph(figure=missbar)]),
        PCorrHeatmap.gen_heatmap_con(title="Correlation Heatmap", id_='heatfig'),
        PBox.gen_boxcontainer(fig_id='boxfig', columnx=dh.whole_data_bskew[numericcols].columns[0],
                              columny=dh.whole_data_bskew[numericcols].columns[1]),
        PBox2.gen_boxcontainer(fig_id='boxfig2', columnx=dh.whole_data_askew[numericcols].columns[0],
                               columny=dh.whole_data_askew[numericcols].columns[1]),
    ]
)


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
        # print(PLine.datas.columns)
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
    Output('disfig', 'figure'),
    Input('dis1_state', 'n_clicks'),
    State('dis1_hist_data', 'value'),
    # State('sca1_x_range_max', 'value'),
    # State('sca1_x_range_min', 'value'),
    State('dis1_width', 'value'),
    State('dis1_height', 'value'),
    State('dis1_logp', 'value'),
    State('dis1_normal', 'value'),
    State('dis1_int', 'value'),
    State('dis1_bin', 'value'),
    prevent_initial_call=True
)
def updata_dis(state, hist_data, width, height, logp, normal, ints, dis1_bin):
    print(normal)
    print(state)
    print(hist_data)
    if ints is not None:
        ints = int(ints)
    else:
        ints = 1000
    if dis1_bin is not None:
        dis1_bin = float(dis1_bin)
    else:
        dis1_bin = 1
    print(type(dis1_bin))
    if width is not None and height is not None:
        return PDis.gen_dis_plot(datacols=hist_data, width=int(width), height=int(height), logp=logp,
                                 reducerange=ints, bin_size=dis1_bin)
    else:
        return PDis.gen_dis_plot(datacols=hist_data, logp=logp, reducerange=ints, bin_size=dis1_bin)


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
    fig = PBox.gen_box(columnx=boxx, columny=boxy, color=color, boxmode=boxmode)
    print(color, type(color))
    print(boxmode, type(boxmode))
    return fig


@app.callback(
    Output('boxfig2', 'figure'),
    Input('box2_state', 'n_clicks'),
    State('box2_x', 'value'),
    State('box2_y', 'value'),
    State('box2_color', 'value'),
    State('box2_boxmode', 'value'),
    prevent_initial_call=True
)
def update_box(state, boxx, boxy, color, boxmode: str = "overlay"):
    print(state)
    boxmode = boxmode
    fig = PBox.gen_box(columnx=boxx, columny=boxy, color=color, boxmode=boxmode)
    print(color, type(color))
    print(boxmode, type(boxmode))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=3041)
