# _*_ coding: UTF-8 _*_
# 注意資料集不要取中文名字
# from logging import PlaceHolder
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
        'colorway': ['#ec7424', '#a4abab'],
        # Keep adding others as needed below
        'hovermode': 'x unified'
    },
    # DATA
    data={
        # Each graph object must be in a tuple or list for each trace
        'bar': [go.Bar(texttemplate='%{value}',
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
app.title = 'credit_Analysis'

SIDEBAR_STYLE = {
    "position": "fixed",
    # "bottom": 0,
    "right": 0,
    'left': 0,
    "padding": "2rem 1rem",
}
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


class SideBar:
    SIDETITLE: str = "SideBar"
    SUBTITLES: list = []
    HREF: list = []
    ID: str = 'side_bar'

    def __init__(self,
                 title: str = SIDETITLE,
                 subtitles=None,
                 idname: str = ID,
                 href=None):
        if href is None:
            href = self.SUBTITLES
        if subtitles is None:
            self.subtitles = self.SUBTITLES
        self.title = title
        self.subtitles = subtitles
        self.idname = idname
        self.href = href

    def _gen_navlink_(self):
        navlinks = []
        for i in range(len(self.subtitles)):
            navlinks.append(dbc.NavLink(children=self.subtitles[i], href=f'#{self.href[i]}', external_link=True))
        return navlinks

    def gen_sidebar(self):
        gensidebar = html.Div([
            html.H4(self.title),
            html.Hr(),
            dbc.Nav(
                self._gen_navlink_()
                ,
                vertical=True,
                pills=True, )
        ], id=self.idname)
        return gensidebar


class TopNavbar:
    HOME: str = 'Home'
    OTHERPAGE = list = []
    ID: str = "top_bar"

    def __init__(self,
                 home: str = HOME,
                 otherpage=None,
                 href=None,
                 topid=ID):
        if otherpage is None:
            otherpage = self.OTHERPAGE
        self.otherpage = otherpage
        self.home = home
        if href is None:
            href = self.otherpage
        self.href = href
        self.topid = topid

    def _gen_navlink_col(self, lens):
        navlinks = [dbc.Col(dbc.NavLink(self.home, href='/', active='exact'), width=6)]
        for i in range(len(self.otherpage)):
            navlinks.append(dbc.Col(dbc.NavLink(children=self.otherpage[i], href=f'/{self.href[i]}',
                                                external_link=True), width=6 / lens))
        return navlinks

    def gen_topbar(self):
        gentopbar = dbc.Navbar([
            dbc.Container([
                dbc.Row(

                    self._gen_navlink_col(lens=len(self.otherpage))
                )
            ], id=self.topid)
        ])
        return gentopbar


class BarAndDes:
    DATA: object = []
    TITLE: str = 'Default'
    COLOR: list or str = []
    HOVER: list = []
    LABEL: dict = {}
    BARDMODE: str = ''
    FIGID: str = ''
    DETAIL: list = ['color', 'text']
    '''
    DATA 要是一個DataFrame
    '''

    def __init__(self,
                 data: pd.DataFrame,
                 title: str = TITLE,
                 columnx: str = '',
                 columny: str = '',
                 color=None,
                 label=None,
                 hover=None,
                 barmode=None,
                 figid=None):
        if label is None:
            label = self.LABEL
        if color is None:
            color = self.COLOR
        if hover is None:
            hover = self.HOVER
        self.data = data
        self.title = title
        self.columnx = columnx
        self.columny = columny
        self.color = color
        self.label = label
        self.hover = hover
        self.barmode = barmode
        self.figid = figid

    def _gen_barchart(self):
        fig = px.bar(self.data, x=self.columnx, y=self.columny, title=self.title, color=self.color, labels=self.label,
                     hover_data=self.HOVER, template='nice', barmode=self.barmode)
        return fig

    def _get_data_column_select(self, id_, ):
        columns = self.data.columns.to_list()
        labels = []
        for i in columns:
            x = {
                "label": i,
                "value": i,
            }
            labels.append(x)

        return dbc.Select(
            options=labels,
            id=f'{self.figid}_{id_}',
            placeholder=f'{columns[0]}'
        )

    def gen_barcontainer(self, bar_contents):
        bar = self._gen_barchart()
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.Div([
                    dbc.InputGroup(
                        [dbc.InputGroupText("X-axis", ),
                         self._get_data_column_select(id_='x', ),
                         dbc.InputGroupText("Y-axis", ),
                         self._get_data_column_select(id_='y', ),
                         ]
                    ),
                    ## TODO 可以寫成內建函式
                    dbc.InputGroup(
                        [dbc.InputGroupText("Color"),
                         dbc.Input(placeholder=''),
                         dbc.InputGroupText("Text"),
                         dbc.Input(placeholder='', ),
                         dbc.Button('作圖', id=f'{self.figid}_state', n_clicks=0)
                         ]
                    )

                    , bar_contents]), width=4),
                dbc.Col(dcc.Graph(figure=bar, id=self.figid), width=8)
            ])
        ])


class LineAndDes:
    DATA: object = []  # 資料
    TITLE: str = 'Default'  # 圖片標題
    COLOR: list or str = []  # 是否分組畫圖
    LABEL: dict = {}  # X軸和Y軸的名稱
    TEXT: str = ''  # 折線圖上的點顯示的資料
    FIGID: str = ''  # 裡面圖片的ID
    DETAIL: list = ['color', 'text']

    def __init__(self,
                 data: pd.DataFrame = None,
                 title: str = TITLE,
                 columnx: str = '',
                 columny: str = '',
                 label: dict = None,
                 hover: list = None,
                 color=None,
                 text=None,
                 figid=None):
        if label is None:
            label = self.LABEL
        self.data = data
        self.title = title
        self.columnx = columnx
        self.columny = columny
        self.label = label
        self.hover = hover
        self.color = color
        self.text = text
        self.figid = figid

    '''
    數值要求，y軸要是numeric data
            x軸可以是category也可以是numeric data
    '''

    def _gen_linecharts(self):
        fig = px.line(self.data, x=self.columnx, y=self.columny, title=self.title, labels=self.label,
                      hover_data=self.hover, color=self.color, text=self.text, template="nice")
        return fig

    def _get_data_column_select(self, id_, ):
        columns = self.data.columns.to_list()
        labels = []
        for i in columns:
            x = {
                "label": i,
                "value": i,
            }
            labels.append(x)

        return dbc.Select(
            options=labels,
            id=f'{self.figid}_{id_}',
            placeholder=f'{columns[0]}'
        )

    def _get_plot_detail_column(self, id_):
        columns = self.DETAIL
        labels = [{"label": i, "value": i} for i in columns]
        return dbc.Select(
            options=labels,
            id=f'{self.figid}_{id_}',
            placeholder=f'{columns[0]}'
        )

    def gen_linecontainter(self, line_contents):
        linec = self._gen_linecharts()
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.Div([
                    dbc.InputGroup(
                        [dbc.InputGroupText("X-axis", ),
                         self._get_data_column_select(id_='x', ),
                         dbc.InputGroupText("Y-axis", ),
                         self._get_data_column_select(id_='y', ),
                         ]
                    ),
                    ## TODO 可以寫成內建函式
                    dbc.InputGroup(
                        [dbc.InputGroupText("Color"),
                         dbc.Input(placeholder='', id=f'{self.figid}_color'),
                         dbc.InputGroupText("Text"),
                         dbc.Input(placeholder='', id=f'{self.figid}_text'),
                         dbc.Button('作圖', id=f'{self.figid}_state')
                         ]
                    )
                    , line_contents]), width=4),
                dbc.Col(dcc.Graph(figure=linec, id=self.figid), width=8)
            ])
        ])


data_bar = px.data.gapminder()
long_df = px.data.medals_long()
data_line = px.data.gapminder().query("country in ['Canada','Botswana']")
topbar = TopNavbar(otherpage=['1', '2', '3'])
PBar = BarAndDes(data=data_bar, columnx='year', columny='pop', color='country',
                 title='BarChart', barmode='group', figid='barfig')
bar_content = '12345544'
PLine = LineAndDes(data=data_line, columnx='lifeExp', columny='gdpPercap',
                   title="Life expectancy in Canada", text='year', color='country', figid='linefig')

line_content = '5678'

'''
id的規則，在建立物件的同時，要給定id=figid，裡面的select column的id格式為figid_y(或y)

'''
app.layout = html.Div(
    [dcc.Location(id='link'), topbar.gen_topbar(), bleow_nav,
     PBar.gen_barcontainer(bar_contents=bar_content),
     html.Hr(),
     PLine.gen_linecontainter(line_contents=line_content)])


@app.callback(
    Output('barfig', 'figure'),
    Input('barfig_state', 'n_clicks'),
    State('barfig_x', 'value'),
    State('barfig_y', 'value'),
)
def update_bar(State, barx, bary):
    fig = px.bar(data_bar, x=barx, y=bary)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=3001)
