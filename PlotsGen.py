import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html, dash, State
import io  # 自動檢查資料需要之模組
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.figure_factory as ff
import pandas as pd


class HeatMap:
    DATA: pd.DataFrame = []
    TITLE: str = "Default"
    LEFT: int = 4

    def __init__(self,
                 data: pd.DataFrame = DATA,
                 ):
        self.data = data

    def _get_heatmap(self):
        corr = self.data.corr()
        fig = ff.create_annotated_heatmap(z=corr.to_numpy(),
                                          x=corr.columns.to_list(),  # 要求為list
                                          y=corr.columns.to_list(),
                                          colorscale=px.colors.diverging.RdBu,
                                          hoverinfo="none",  # Shows hoverinfo for null values
                                          showscale=True, ygap=1, xgap=1
                                          )
        fig.update_xaxes(side="bottom")
        fig.update_layout(
            title_text='Heatmap',
            title_x=0.5,
            width=1000,
            height=1000,
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_zeroline=False,
            yaxis_zeroline=False,
            yaxis_autorange='reversed',
            template='plotly_white'
        )
        # NaN values are not handled automatically and are displayed in the figure
        # So we need to get rid of the text manually
        for i in range(len(fig.layout.annotations)):
            if fig.layout.annotations[i].text == 'nan':
                fig.layout.annotations[i].text = ""
        return fig

    def gen_heatmap(self,
                    title=TITLE,
                    left=LEFT,
                    id_: str = None):
        title = title
        left = left
        id_ = id_
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(dcc.Markdown(), width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}),
                         dcc.Graph(figure=self._get_heatmap())], width=(12 - left))
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
            navlinks.append(dbc.Col(dbc.NavLink(children=self.otherpage[i], href=f'#{self.href[i]}',
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
    BARCONTAINERID: str = ''
    DETAIL: list = ['color', 'text']
    CONTENT: object = '橫軸為類別，Y軸為數值,' "\n" \
                      'color用的是另一個類別，他會自動分顏色，要使用group起來的話，要更改barmode'

    '''
    DATA 要是一個DataFrame
    '''

    def __init__(self,
                 data: pd.DataFrame,
                 title: str = TITLE,
                 columnx: str = '',
                 columny: str = '',
                 color: str = None,
                 label: str = None,
                 hover: str = None,
                 barmode: str = None,
                 barcid=None,
                 content=CONTENT):
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
        self.containerid = barcid
        self.content = content

    def _gen_barchart(self):
        fig = px.bar(self.data, x=self.columnx, y=self.columny, title=self.title, color=self.color,
                     labels=self.label,
                     hover_data=self.HOVER, barmode=self.barmode, template='nice')
        return fig

    '''
    下面是拿來生長放到select裡面的column,id_是每個select欄位的，方便我們做callback
    型式就是containerid_(id_)
    '''

    # 專門給select生產option  不產生html輸出
    @staticmethod
    def _get_select(datas):
        columns = datas.columns.to_list()
        labels = []
        for i in columns:
            x = {
                "label": f'{i}({datas[i].dtypes})',
                "value": i,
            }
            labels.append(x)
        return labels

    # 生產html輸出
    def _get_data_column_select(self, id_: str = None, ):
        id_ = id_
        # columns = self.data.columns.to_list()
        labels = self._get_select(self.data)
        return dbc.Select(
            options=labels,
            id=f'{self.containerid}_{id_}',
            placeholder=f'Choose Col'
        )

    def gen_barcontainer(self,
                         bar_contents: str = CONTENT,
                         fig_id: str = None):
        bar_contents = bar_contents
        bar = self._gen_barchart()
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(html.Div([
                    dbc.InputGroup(
                        [dbc.InputGroupText("X-axis", ),
                         self._get_data_column_select(id_='x', ),
                         dbc.InputGroupText("Y-axis", ),
                         self._get_data_column_select(id_='y', ),
                         ]
                    ),
                    html.Div(
                        [dcc.Dropdown(self._get_select(self.data), placeholder='Color',
                                      id=f'{self.containerid}_color', ),
                         ]
                    ),
                    # dbc.InputGroup(
                    #     [dbc.Input(placeholder='Text', id=f'{self.containerid}_text'), ]
                    # ),
                    html.Div(
                        [dcc.Dropdown(options=[{'label': "stack", "value": "stack"},
                                               {"label": "group", 'value': "group"},
                                               {'label': "overlay", 'value': 'overlay'},
                                               {'label': 'relative', 'value': 'relative'}],
                                      placeholder='barmode',
                                      id=f'{self.containerid}_barmode'),
                         ]
                    ),
                    dbc.Button('作圖', id=f'{self.containerid}_state', n_clicks=0)
                    , html.Div(bar_contents, id=f'{self.containerid}_content')]), width=4),
                dbc.Col(dcc.Graph(figure=bar, id=fig_id), width=8)
            ])
        ], id=self.containerid)

    def gen_updata_bar(self,
                       columnx: str = None,
                       columny: str = None,
                       title: str = None,
                       color: str = None,
                       barmode: str = None):
        data = self.data
        columnx = columnx
        columny = columny
        title = self.title
        color = color
        barmode = barmode
        fig = px.bar(data, x=columnx, y=columny, title=title, color=color,
                     labels=self.label,
                     hover_data=self.HOVER, barmode=barmode, template='nice')

        return fig


class LineAndDes:
    DATA: object = []  # 資料
    TITLE: str = 'Default'  # 圖片標題
    COLOR: list or str = []  # 是否分組畫圖
    LABEL: dict = {}  # X軸和Y軸的名稱
    TEXT: str = ''  # 折線圖上的點顯示的資料
    CONTAINERID: str = ''  # 裡面container的ID
    DETAIL: list = ['color', 'text']
    CONTENT: any = 'text為每個點上顯示的變數維和，color能根據不同變數做分組'

    def __init__(self,
                 data: pd.DataFrame = None,
                 title: str = TITLE,
                 columnx: str = '',
                 columny: str = '',
                 label: dict = None,
                 hover: list = None,
                 color=None,
                 text=None,
                 linecid=None, ):
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
        self.containerid = linecid

    '''
    數值要求，y軸要是numeric data
            x軸可以是category也可以是numeric data
    '''

    def _gen_linecharts(self):
        fig = px.line(self.data, x=self.columnx, y=self.columny, title=self.title, labels=self.label,
                      hover_data=self.hover, color=self.color, text=self.text, template="nice")
        return fig

    # 專門給select生產option  不產生html輸出
    @staticmethod
    def _get_select(datas):
        columns = datas.columns.to_list()
        labels = []
        for i in columns:
            x = {
                "label": f'{i}({datas[i].dtypes})',
                "value": i,
            }
            labels.append(x)
        return labels

    # 生產html輸出
    def _get_data_column_select(self, id_, ):
        columns = self.data.columns.to_list()
        labels = []
        for i in columns:
            x = {
                "label": f'{i}({self.data[i].dtypes})',
                "value": i,
            }
            labels.append(x)

        return dbc.Select(
            options=labels,
            id=f'{self.containerid}_{id_}',
            placeholder='Choose Col'
        )

    def _get_plot_detail_column(self, id_):
        columns = self.DETAIL
        labels = [{"label": i, "value": i} for i in columns]
        return dbc.Select(
            options=labels,
            id=f'{self.containerid}_{id_}',
            placeholder=f'{columns[0]}'
        )

    def gen_linecontainter(self,
                           line_contents: any = CONTENT,
                           fig_id: str = None):
        lineplot = self._gen_linecharts()
        fig_id = fig_id
        line_contents = line_contents
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(html.Div([
                    dbc.InputGroup(
                        [dbc.InputGroupText("X-axis", ),
                         self._get_data_column_select(id_='x', ),
                         dbc.InputGroupText("Y-axis", ),
                         self._get_data_column_select(id_='y', ),
                         ]
                    ),
                    html.Div(
                        [dcc.Dropdown(self._get_select(self.data), placeholder='Color',
                                      id=f'{self.containerid}_color', ),
                         ]
                    ),
                    html.Div(
                        [dcc.Dropdown(self._get_select(self.data),
                                      placeholder='Text', id=f'{self.containerid}_text'), ]
                    ),
                    dbc.InputGroup([
                        dbc.Button('作圖', id=f'{self.containerid}_state')
                    ])
                    , line_contents]), width=4),
                dbc.Col(dcc.Graph(figure=lineplot, id=fig_id), width=8)
            ])
        ])

    def gen_updata_line(self,
                        columnx: str = None,
                        columny: str = None,
                        linetitle: str = None,
                        color: str = None,
                        text: str = None
                        ):
        if linetitle is None:
            linetitle = self.title
        else:
            linetitle = linetitle
        data = self.data
        columnx = columnx
        columny = columny
        color = color
        text = text
        fig = px.line(data_frame=data, x=columnx, y=columny, color=color, template='nice', title=linetitle, text=text)
        return fig


class BoxCharts:
    DATA: pd.DataFrame = []
    TITLE: str = "Default"
    BOXCONTAINERID: str = None
    CONTENT: any = ''

    def __init__(self,
                 title: str = TITLE,
                 data: pd.DataFrame = DATA,
                 boxcid=BOXCONTAINERID,
                 columnx: str = '',
                 columny: str = ''):
        self.data = data
        self.title = title
        self.boxcid = boxcid
        self.columnx = columnx
        self.columny = columny

    # 生產html輸出
    def _get_data_column_select(self, id_, placeholder):
        columns = self.data.columns.to_list()
        labels = []
        placeholder = placeholder
        for i in columns:
            x = {
                "label": f'{i}({self.data[i].dtypes})',
                "value": i,
            }
            labels.append(x)

        return dbc.Select(
            options=labels,
            id=f'{self.boxcid}_{id_}',
            placeholder=placeholder
        )

    @staticmethod
    def _get_select(datas):
        columns = datas.columns.to_list()
        labels = []
        for i in columns:
            x = {
                "label": f'{i}({datas[i].dtypes})',
                "value": i,
            }
            labels.append(x)
        return labels

    # 新增盒鬚圖x的columnx
    # def _get_data_column_select(self, id_, placeholder):
    #     labels = self._get_select(self.data)
    #     placeholder = placeholder
    #     return dbc.Select(
    #         options=labels,
    #         id=f'{self.boxcid}_{id_}',
    #         placeholder=placeholder
    #     )

    # 新增dropdown
    def _gen_data_dropdown(self, id_, placeholder, multi: bool = False, ):
        options = self._get_select(self.data)
        multi = multi
        placeholder = placeholder
        return dcc.Dropdown(
            options=options,
            multi=multi,
            id=f'{self.boxcid}_{id_}',
            placeholder=placeholder
        )

    def _gen_boxchart(self):
        fig = px.box(data_frame=self.data, x=self.columnx, y=self.columny, title=self.title, template='nice')
        return fig

    def gen_boxcontainer(self,
                         box_contents: any = CONTENT,
                         fig_id: str = None):
        boxplot = self._gen_boxchart()
        fig_id = fig_id
        box_contents = box_contents
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div([self._gen_data_dropdown(id_='x', multi=True, placeholder="X_axis"), ]),
                    html.Div([self._get_data_column_select(id_='y', placeholder='Y-axis'), ]),
                    html.Div(
                        [dcc.Dropdown(self._get_select(self.data), placeholder='Color',
                                      id=f'{self.boxcid}_color', ),
                         ]
                    ),
                    html.Div(
                        [dcc.Dropdown(options=[{"label": "group", 'value': "group"},
                                               {'label': "overlay", 'value': 'overlay'}],
                                      placeholder='boxmode', id=f'{self.boxcid}_boxmode'), ]
                    ),
                    dbc.InputGroup([
                        dbc.Button('作圖', id=f'{self.boxcid}_state')
                    ])
                    , box_contents]), width=4),
                dbc.Col(dcc.Graph(figure=boxplot, id=fig_id), width=8)
            ])
        ])

    def gen_updata(self, columnx, columny, color, boxmode):
        fig = px.box(data_frame=self.data, x=columnx, y=columny,
                     color=color, boxmode=boxmode, template='nice',
                     title=self.title)
        return fig


class ScatterPlots:
    DATA: object = []
    TITLE: str = 'Default'

    CONTENT: object = '橫軸為類別，Y軸為數值,' "\n" \
                      'color用的是另一個類別，他會自動分顏色，要使用group起來的話，要更改barmode'


if __name__ == '__main__':
    print(__name__)
