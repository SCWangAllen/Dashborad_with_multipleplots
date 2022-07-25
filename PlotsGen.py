import dash_bootstrap_components as dbc
from dash import dcc, html
import io  # 自動檢查資料需要之模組
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.figure_factory as ff
import pandas as pd

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


class Settings:
    """
    這個class儲存一些在用dash視覺化時，內部需要另外做的處理方式。
    """
    LEFT: int = 4
    COLOR: list or str = []

    def __init__(self, data=None):
        self.data = data

    @staticmethod
    def get_select(data):
        columns = data.columns.to_list()
        labels = []
        for i in columns:
            x = {
                "label": f'{i}({data[i].dtypes})',
                "value": i,
            }
            labels.append(x)
        return labels

    # 下面是將data的description轉成我們能夠輕易看的pd.Dataframe
    @staticmethod
    def get_data_description(data):
        buffer = io.StringIO()
        data.info(buf=buffer)
        lines = buffer.getvalue().splitlines()
        details = (pd.DataFrame([x.split() for x in lines[5:-2]], columns=lines[3].split())
                   .drop('Count', axis=1)
                   .rename(columns={'Non-Null': 'Non-Null Count'})
                   .rename(columns={'#': 'number'}))
        unique_value = []
        for i in data.columns:
            unique_value.append(len(data[i].unique()))
        details['unique'] = unique_value
        return details

    def gen_data_dropdown(self, data, top_id, id_, placeholder: str = None,
                          multi: bool = False, numeric: bool = None, ):
        """
        替圖表新增dropdown選項 /n
        numeric true代表只留下數值型態欄位，numeric False代表留下類別欄位，None代表都留
        """
        datades = self.get_data_description(data)
        options = []
        if numeric:
            for i in range(len(data.columns) - 1):
                if datades['Dtype'][i] != 'object':
                    options.append({
                        "label": f'{data.columns[i]}({data[data.columns[i]].dtypes})',
                        "value": data.columns[i],
                    })
                else:
                    pass
        elif numeric is False:
            for i in range(len(data.columns) - 1):
                if datades['Dtype'][i] == 'object':
                    options.append({
                        "label": f'{data.columns[i]}({data[data.columns[i]].dtypes})',
                        "value": data.columns[i],
                    })
                else:
                    pass
        else:
            options = self.get_select(data)

        multi = multi
        placeholder = placeholder
        return dcc.Dropdown(
            options=options,
            multi=multi,
            id=f'{top_id}_{id_}',
            placeholder=placeholder
        )

    @staticmethod
    def fig_layout_set(fig,
                       width: int = 1000,
                       height: int = 500,
                       template: str = 'plotly_white',
                       yaxis_range=None,
                       xaxis_range=None,
                       ):

        return fig.update_layout(
            # title_text='Heatmap',
            title_x=0.5,
            width=width,
            height=height,
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_zeroline=False,
            yaxis_zeroline=False,
            # yaxis_autorange='reversed',
            yaxis_range=yaxis_range,
            xaxis_range=xaxis_range,
            template=template
        )


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
                self._gen_navlink_(),
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


class BarAndDes(Settings):
    """
    更快的產生bar chart的相關視覺化dash app
    """
    DATA: object = []
    TITLE: str = 'Barchart'
    HOVER: list = []
    LABEL: dict = {}
    BARDMODE: str = ''
    BARCONTAINERID: str = ''
    DETAIL: list = ['color', 'text']
    CONTENT: object = '橫軸為類別，Y軸為數值,' "\n" \
                      'color用的是另一個類別，他會自動分顏色，要使用group起來的話，要更改barmode'

    def __init__(self, data: pd.DataFrame, title: str = TITLE, columnx: str = '', columny: str = '', color: str = None,
                 label: str = None, hover: str = None, barmode: str = None, barcid=None, content=CONTENT):
        super().__init__(data)
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

        fig = px.bar(self.data, x=self.columnx, y=self.columny, title=self.title,
                     labels=self.label,
                     hover_data=self.HOVER, barmode=self.barmode, template='nice')

        return fig

    def _gen_historgram(self):
        fig = px.histogram(data_frame=self.data, x=self.columnx, y=self.columny, title=self.title,
                           labels=self.label,
                           hover_data=self.HOVER, barmode=self.barmode, template='nice')

    '''
    下面是拿來生長放到select裡面的column,id_是每個select欄位的，方便我們做callback
    型式就是containerid_(id_)
    '''

    # 專門給select生產option  不產生html輸出

    # 生產html輸出
    def _get_data_column_select(self, id_: str = None, ):
        id_ = id_
        # columns = self.data.columns.to_list()
        labels = super().get_select(self.data)
        return dbc.Select(
            options=labels,
            id=f'{self.containerid}_{id_}',
            placeholder=f'Choose Col'
        )

    def gen_barcontainer(self,
                         bar_contents: str = CONTENT,
                         fig_id: str = None,
                         ):
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
                        [dcc.Dropdown(super().get_select(self.data), placeholder='Color',
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
                    ), dbc.Button('作圖', id=f'{self.containerid}_state', n_clicks=0),
                    html.Div(bar_contents, id=f'{self.containerid}_content')]), width=4),
                dbc.Col(dcc.Graph(figure=bar, id=fig_id), width=8)
            ])
        ], id=self.containerid)

    def gen_updata_bar(self,
                       columnx: str = None,
                       columny: str = None,
                       title: str = TITLE,
                       color: str = None,
                       barmode: str = None):
        data = self.data
        columnx = columnx
        columny = columny
        title = title
        color = color
        barmode = barmode
        fig = px.bar(data, x=columnx, y=columny, title=title, color=color,
                     labels=self.label,
                     hover_data=self.HOVER, barmode=barmode, template='nice')

        return fig


class HistAndDes(Settings):
    """hist plot and probability"""

    def __init__(self,
                 data: pd.DataFrame,
                 columnx: str = None,
                 columny: str = None,
                 ):
        self.data = data
        self.columnx = columnx
        self.columnx = columny

    def _gen_hist(self):
        fig = go.Histogram()


class LineAndDes(Settings):
    DATA: object = []  # 資料
    TITLE: str = 'LineChart'  # 圖片標題
    COLOR: list or str = []  # 是否分組畫圖
    LABEL: dict = {}  # X軸和Y軸的名稱
    TEXT: str = ''  # 折線圖上的點顯示的資料
    CONTAINERID: str = ''  # 裡面container的ID
    DETAIL: list = ['color', 'text']
    CONTENT: any = 'text為每個點上顯示的變數維和，color能根據不同變數做分組'

    def __init__(self, data: pd.DataFrame = None, title: str = TITLE, columnx: str = '', columny: str = '',
                 label: dict = None, hover: list = None, color=None, text=None, linecid=None):
        super().__init__(data)
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

    # 生產Select的html輸出
    def _get_data_column_select(self, id_, ):
        return dbc.Select(
            options=super().get_select(self.data),
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
                        [dcc.Dropdown(super().get_select(self.data), placeholder='Color',
                                      id=f'{self.containerid}_color', ),
                         ]
                    ),
                    html.Div(
                        [dcc.Dropdown(super().get_select(self.data),
                                      placeholder='Text', id=f'{self.containerid}_text'), ]
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("X-range_min", ),
                            dbc.Input(id=f'{self.containerid}_x_range_min', ),
                            dbc.InputGroupText("X-range_max", ),
                            dbc.Input(id=f'{self.containerid}_x_range_max', ),
                        ]
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Y-range_min", ),
                            dbc.Input(id=f'{self.containerid}_y_range_min', ),
                            dbc.InputGroupText("Y-range_max", ),
                            dbc.Input(id=f'{self.containerid}_y_range_max', ),
                        ]
                    ),
                    dbc.InputGroup(
                        [dbc.InputGroupText("width", ),
                         dbc.Input(id=f'{self.containerid}_width', ),
                         dbc.InputGroupText("height", ),
                         dbc.Input(id=f'{self.containerid}_height', ),
                         ]
                    ),
                    html.Div(id=f'{self.containerid}_xy_range_word'),
                    html.Div([
                        dbc.Button('作圖', id=f'{self.containerid}_state'),
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


# 改盒需圖的color選項，只有oobject能在裡面
class BoxCharts(Settings):
    """
    更快的產生BOX chart的相關視覺化dash app
    """
    DATA: pd.DataFrame = []
    TITLE: str = "BoxChart"
    BOXCONTAINERID: str = None
    CONTENT: any = ''

    def __init__(self, title: str = TITLE, data: pd.DataFrame = DATA, boxcid=BOXCONTAINERID, columnx: str = '',
                 columny: str = ''):
        super().__init__(data)
        self.data = data
        self.title = title
        self.boxcid = boxcid
        self.columnx = columnx
        self.columny = columny

    # 生產select的html輸出
    def _get_data_column_select(self, id_, placeholder):
        return dbc.Select(
            options=super().get_select(self.data),
            id=f'{self.boxcid}_{id_}',
            placeholder=placeholder
        )

    # 新增盒鬚圖x的columnx
    # def _get_data_column_select(self, id_, placeholder):
    #     labels = self._get_select(self.data)
    #     placeholder = placeholder
    #     return dbc.Select(
    #         options=labels,
    #         id=f'{self.boxcid}_{id_}',
    #         placeholder=placeholder
    #     )

    def _gen_boxchart(self):
        fig = px.box(data_frame=self.data, x=self.columnx, y=self.columny, title=self.title, template='nice')
        super().fig_layout_set(fig, width=1000, height=500, template='nice')
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
                    html.Div(
                        [super().gen_data_dropdown(data=self.data, top_id=self.boxcid,
                                                   id_='x', multi=True, placeholder="X_axis"), ]),
                    html.Div([super().gen_data_dropdown(data=self.data, top_id=self.boxcid,
                                                        id_='y', multi=False, placeholder="Y_axis")]),
                    html.Div(
                        [dcc.Dropdown(super().get_select(self.data), placeholder='Color',
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
        """
        callback的更新，返回figure

        """
        fig = px.box(data_frame=self.data, x=columnx, y=columny,
                     color=color, boxmode=boxmode, template='nice',
                     title=self.title)
        super().fig_layout_set(fig, width=1000, height=500, template='nice')

        return fig


class ScatterPlots(Settings):
    TITLE: str = 'Scatter Plot'
    CONTENT: any = '關於圖片的說明'
    SCID: str = None

    def __init__(self, data=None, scaid: str = None):
        super().__init__(data)
        self.data = data
        self.scaid = scaid

    def gen_scatter(self, columnx,
                    columny,
                    width: int = 1000,
                    height: int = 500,
                    tmeplate: str = "plotly_white",
                    x_range: list = None,
                    y_range: list = None,
                    color: str = None,
                    ):
        fig = px.scatter(data_frame=self.data, x=columnx, y=columny, color=color)
        super().fig_layout_set(fig=fig, width=width, height=height, template=tmeplate,
                               xaxis_range=x_range, yaxis_range=y_range, )
        return fig

    # 若想要一開始在html上面就有圖表，可以填充數值
    def gen_scacon(self, x, y, fig_id: str = None, sca_contents: any = CONTENT):
        fig = self.gen_scatter(columnx=x, columny=y, height=500)
        fig_id = fig_id
        sca_contents = sca_contents
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div(
                        [super().gen_data_dropdown(data=self.data, top_id=self.scaid,
                                                   id_='x', multi=False, placeholder="X_axis"), ]),
                    html.Div([super().gen_data_dropdown(data=self.data, top_id=self.scaid,
                                                        id_='y', multi=False, placeholder="Y_axis")]),
                    html.Div(
                        [super().gen_data_dropdown(data=self.data, top_id=self.scaid, id_='color',
                                                   placeholder='Color', multi=False, numeric=False),
                         # dcc.Dropdown(super().get_select(self.data), placeholder='Color',
                         #              id=f'{self.scaid}_color', ),
                         ]
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("X-range_min", ),
                            dbc.Input(id=f'{self.scaid}_x_range_min', ),
                            dbc.InputGroupText("X-range_max", ),
                            dbc.Input(id=f'{self.scaid}_x_range_max', ),
                        ]
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Y-range_min", ),
                            dbc.Input(id=f'{self.scaid}_y_range_min', ),
                            dbc.InputGroupText("Y-range_max", ),
                            dbc.Input(id=f'{self.scaid}_y_range_max', ),
                        ]
                    ),
                    dbc.InputGroup(
                        [dbc.InputGroupText("width", ),
                         dbc.Input(id=f'{self.scaid}_width', ),
                         dbc.InputGroupText("height", ),
                         dbc.Input(id=f'{self.scaid}_height', ),
                         ]
                    ),
                    html.Div(id=f'{self.scaid}_xy_range_word'),
                    dbc.InputGroup([
                        dbc.Button('作圖', id=f'{self.scaid}_state')
                    ], )
                    , sca_contents]), width=4),
                dbc.Col(dcc.Graph(figure=fig, id=fig_id), width=8)
            ])
        ])


class HeatMap(Settings):
    """
    快速產生heatmap的dash app部分
    """
    DATA: pd.DataFrame = []
    TITLE: str = "Default"
    LEFT: int = 4

    def __init__(self, data: pd.DataFrame = DATA, heatid: str = None):
        super().__init__(data)
        self.heatid = heatid
        self.data = data
        self.corr = data.corr()
        self.columns = data.columns

    #     z = self.corr.to_numpy
    #     y = self.columns.to_list()
    #     x = self.columns.to_list()
    @staticmethod
    def _get_heatmap(x,
                     y,
                     z):
        """
        :param x:  same length as z
        :type x: list
        :param y: same length as z
        :type y: list
        :param z: correalation matrix(numpy array)
        :type z: numpy.array
        :return:
        :rtype:
        """
        fig = ff.create_annotated_heatmap(z=z,
                                          x=x,  # 要求為list
                                          y=y,
                                          colorscale=px.colors.diverging.RdBu,
                                          hoverinfo="none",  # Shows hoverinfo for null values
                                          showscale=True, ygap=1, xgap=1
                                          )
        fig.update_xaxes(side="bottom")
        # 注意這是個靜態方法，沒有使用到繼承，因此直接用super會出錯
        Settings.fig_layout_set(fig=fig, width=1000, height=1000, )
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
        FIGURE = self._get_heatmap(x=self.corr.columns.to_list(),
                                   y=self.corr.columns.to_list(),
                                   z=self.corr.to_numpy())
        return dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.Div(super().gen_data_dropdown(data=self.data, top_id=self.heatid, id_='vars',
                                                       multi=True, placeholder='varaibles', numeric=True)),
                    html.Div(id=f'{self.heatid}_var_list'),
                    dbc.Button('作圖', id=f'{self.heatid}_state')], width=left),
                dbc.Col([html.H4(title, style={'text-align': 'center'}),
                         dcc.Graph(figure=FIGURE, id=id_)], width=(12 - left))
            ])
        ], id=self.heatid)

    def gen_update(self, var: list, rounds: int = 5):
        corr = self.data[var].corr().round(rounds)
        fig = self._get_heatmap(x=corr.columns.to_list(),
                                y=corr.columns.to_list(),
                                z=corr.to_numpy())
        return fig


if __name__ == '__main__':
    print(__name__)
