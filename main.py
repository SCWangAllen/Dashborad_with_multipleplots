import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html, dash, State
import Pages
import plotly.express as px
import pandas as pd

data_canada = px.data.gapminder().query("country == 'Canada'")
long_df = px.data.medals_long()


class PlotAndDes:
    TYPES: str = 'bar'
    DATA: object = []
    TITLE: str = 'Default'
    '''
    DATA 要是一個DataFrame
    我們預設的圖形可以有bar chart : 'bar'
                    scatter chart : 'sactter'
                    pie chart : 'pie'
                    line chart : 'line'
    
    '''

    def __init__(self,
                 data: object = pd.DataFrame,
                 types: str = TYPES,
                 title: str = TITLE,
                 columnx: str = '',
                 columny: str = ''):
        self.data = data
        self.types = types
        self.title = title
        self.columnx = columnx
        self.columny = columny

    def _gen_barchart(self):
        fig = px.bar(self.data, x=self.columnx, y=self.columny, title=self.title)
        return fig

    def gen_container(self, idforfig,content):
        bar = self._gen_barchart()
        return [
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Div(content), width=4),
                    dbc.Col(dcc.Graph(id=idforfig), width=8)
                ])
            ])
        ]


PBart = PlotAndDes()
