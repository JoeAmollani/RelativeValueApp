# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 14:36:09 2020
@author: Joen
"""


# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
from dash.dependencies import Input, Output
import pandas as pd
import RelativeValue as RV

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)#, external_stylesheets=external_stylesheets)

server = app.server

LineColor1 = '#B9FFB0'
LineColor2 = '#FFB0B0'
LineColor3 = '#88BEE6'
LineColor4 = '#ADA1C2'
LineColor5 = '#458CA8'

graph_colors = '#000916'

TimeSeries = pd.ExcelFile('FXMDB.xlsx').parse(index_col=0)['2015-01-01':]
fnameDict = {'Fixed Income': ['opt1_c', 'opt2_c', 'opt3_c'],
             'FX': TimeSeries.columns}

names = list(fnameDict.keys())
nestedOptions = fnameDict[names[0]]

app.layout = html.Div(
    html.Div([
        html.Div(
            [
                html.H1(children='Relative Value',
                        className='nine columns'),
                html.Img(src="/assets/stock-icon.png")
            ], className="banner"
        ),

        html.Div([
            html.Div([
                html.Div(children='''Settings''',
                         className='row'),
                dcc.Dropdown(
                    id='name-dropdown',
                    options=[{'label': name, 'value': str(name)} for name in names],
                    value=list(fnameDict.keys())[0]
                    , className='row',
                    style=dict(
                        width='90%')
                ),

                dcc.Dropdown(
                    id='Asset1', placeholder='First Asset', className='row',
                    style=dict(
                        width='90%')
                ),
                dcc.Dropdown(
                    id='Asset2', placeholder='Second Asset', className='row',
                    style=dict(
                        width='90%')
                ),
                dcc.Dropdown(
                    id='Horizon', options=[{'label': '250 Days', 'value': 250},
                                           {'label': '180 Days', 'value': 180},
                                           {'label': '120 Days', 'value': 120},
                                           {'label': '90 Days', 'value': 90},
                                           {'label': '60 Days', 'value': 60},
                                           {'label': '30 Days', 'value': 30}],
                    placeholder='Rolling Window', className='row',
                    style=dict(
                        width='90%')
                ),

                dcc.Dropdown(
                    id='StDev', options=[{'label': '3 StDevs', 'value': 3},
                                         {'label': '2.5 StDevs', 'value': 2.5},
                                         {'label': '2 StDevs', 'value': 2},
                                         {'label': '1.5 StDevs', 'value': 1.5},
                                         {'label': '1 StDevs', 'value': 1}],
                    placeholder='No of StDevs', className='row',
                    style=dict(
                        width='90%')
                    ),

                dcc.Dropdown(
                    id='Ratio', options=[{'label': 'Rolling', 'value': str('Rolling')},
                                         {'label': 'Fixed', 'value': str('Fixed')}],
                    placeholder='Rebalance Ratio', className='row',
                    style=dict(
                        width='90%')
                ),

            ], className="two columns"),

            html.Div(children=''' ''', className="one columns"),

            dcc.Tabs(id='tabs-example', value='tab-1', children=[
                dcc.Tab(
                    dcc.Loading(id='Loading', children=[
                        html.Div([
                            html.Div(
                                [
                                    html.Div([], id="graph1", className='six columns'),
                                    html.Div([], id="graph2", className='six columns'),
                                ],
                                className="row"),
                            html.Div(
                                [
                                    html.Div([], id="graph3", className='six columns'),
                                    html.Div([], id="graph4", className='six columns'),
                                ],
                                className="row")

                        ])]),
                    label='Overview'),

                dcc.Tab(
                    dcc.Loading(id='Loading2', children=[
                        html.Div(
                            [
                                html.Div([], id="graph5", className='five columns'),
                                html.Div([], id="graph6", className='five columns'),
                            ], className="row"
                        )]), label='Analytics')
            ],colors={
                "border": '#5C5178',
                "primary": '#56ACDB',
                "background": '#473E66'
            })
        ])

    ], className='ten columns offset-by-one')
)


@app.callback(
    [dash.dependencies.Output('Asset1', 'options'),
     dash.dependencies.Output('Asset2', 'options')],
    [dash.dependencies.Input('name-dropdown', 'value')]
)
def update_date_dropdown(name):
    return [{'label': i, 'value': i} for i in fnameDict[name]], [{'label': i, 'value': i} for i in fnameDict[name]]


@app.callback([Output('graph1', 'children'),
               Output('graph2', 'children'),
               Output('graph3', 'children'),
               Output('graph4', 'children'),
               Output('graph5', 'children'),
               Output('graph6', 'children')],
              [Input('Asset1', 'value'),
               Input('Asset2', 'value'),
               Input('Horizon', 'value'),
               Input('StDev', 'value'),
               Input('Ratio', 'value')])

def update_Graph(Asset_A, Asset_B, Window, StDev, Ratio):
    Backtest_Results = RV.Relative_Value_Backtest(TimeSeries, Asset_A, Asset_B, Window, StDev, Ratio)

    Pivot1 = pd.pivot_table(Backtest_Results, values='Cummulative', index=Backtest_Results.index, columns=['Trade'])

    Backtest_Results[['Bollinger Low', 'Bollinger High', 'Rolling Mean', 'Spread']]

    Pivot2 = pd.pivot_table(Backtest_Results, values=Asset_A, index=Backtest_Results.index, columns=['Trade'])
    Pivot3 = pd.pivot_table(Backtest_Results, values=Asset_B, index=Backtest_Results.index, columns=['Trade'])

    RollingBeta = RV.Rolling_Beta(Backtest_Results, Asset_A, Asset_B, Window)
    RollingPvalue = RV.Cointegration_Test(Backtest_Results, Asset_A, Asset_B, Window)

    children = []
    children.append(dcc.Graph(
        figure={'data': [
            {'x': Pivot1.index, 'y': Pivot1[Pivot1.columns[0]].values, 'name': Pivot1.columns[0],'marker' : { "color" : LineColor1}},
            {'x': Pivot1.index, 'y': Pivot1[Pivot1.columns[1]].values, 'name': Pivot1.columns[1],'marker' : { "color" : LineColor2}},
            {'x': Pivot1.index, 'y': Pivot1[Pivot1.columns[2]].values, 'name': Pivot1.columns[2],'marker' : { "color" : LineColor3}}],
            'layout': {
                'plot_bgcolor': graph_colors,
                'paper_bgcolor': graph_colors,
                'title': dict(text ='Performance',
                               font =dict(
                               size=16,
                               color = 'cyan')),
                'legend': dict(font=dict(color='cyan'),
                               orientation="h",
                               size=12,
                               style={'margin-top': 100}),
                'xaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=8,
                        color='cyan'
                    )),
                'yaxis': dict(color='cyan',
                    # title='y Axis',
                    titlefont=dict(
                        family='Helvetica, monospace',
                        size=8,
                        color='cyan'
                    )),
                'margin': dict(
                    l=30,
                    r=30,
                    b=50,
                    t=35,
                    pad=4)
            }
        }
    ))

    children.append(
        dcc.Graph(

            figure={
                'data': [
                    {'x': Backtest_Results.index, 'y': Backtest_Results['Bollinger Low'].values, 'name': u'Lower Band','marker' : { "color" : LineColor1}},
                    {'x': Backtest_Results.index, 'y': Backtest_Results['Bollinger High'].values, 'name': u'Higher Band','marker' : { "color" : LineColor2}},
                    {'x': Backtest_Results.index, 'y': Backtest_Results['Rolling Mean'].values, 'name': u'Mean','marker' : { "color" : LineColor3}},
                    {'x': Backtest_Results.index, 'y': Backtest_Results['Spread'].values, 'name': u'Spread','marker' : { "color" : LineColor4}},

                ],
                'layout': {
                    'plot_bgcolor': graph_colors,
                    'paper_bgcolor': graph_colors,
                    'title': dict(text ='Trade Signals',
                               font =dict(
                               size=16,
                               color = 'cyan')),
                    'legend': dict(font=dict(color='cyan'),
                                   orientation="h",
                                   size=12,
                                   style={'margin-top': 100}),
                    'xaxis': dict(color='cyan',
                        titlefont=dict(
                            family='Courier New, monospace',
                            size=8,
                            color='cyan'
                        )),
                    'yaxis': dict(color='cyan',
                        titlefont=dict(
                            family='Helvetica, monospace',
                            size=8,
                            color='cyan'
                        )),
                    'margin': dict(
                        l=30,
                        r=30,
                        b=50,
                        t=35,
                        pad=4)
                }
            }))
    children.append(dcc.Graph(
        figure={
            'data': [
                {'x': Pivot2.index, 'y': Pivot2[Pivot2.columns[0]].values, 'name': Pivot2.columns[0], 'marker' : { "color" : LineColor1}},
                {'x': Pivot2.index, 'y': Pivot2[Pivot2.columns[1]].values, 'name': Pivot2.columns[1], 'marker' : { "color" : LineColor2}},
                {'x': Pivot2.index, 'y': Pivot2[Pivot2.columns[2]].values, 'name': Pivot2.columns[2], 'marker' : { "color" : LineColor3}},
            ],
            'layout': {
                'plot_bgcolor': graph_colors,
                'paper_bgcolor': graph_colors,
                'title': dict(text =str(Asset_A),
                               font =dict(
                               size=16,
                               color = 'cyan')),
                'legend': dict(font=dict(color='cyan'),
                               orientation="h",
                               size=12,
                               style={'margin-top': 100}),
                'xaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=8,
                        color='cyan'
                    )),
                'yaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Helvetica, monospace',
                        size=8,
                        color='cyan')),

                'margin': dict(
                    l=30,
                    r=30,
                    b=0,
                    t=35,
                    pad=4)

            }
        }))

    children.append(dcc.Graph(
        figure={
            'data': [
                {'x': Pivot3.index, 'y': Pivot3[Pivot3.columns[0]].values, 'name': Pivot3.columns[0],'marker' : { "color" : LineColor1}},
                {'x': Pivot3.index, 'y': Pivot3[Pivot3.columns[1]].values, 'name': Pivot3.columns[1],'marker' : { "color" : LineColor2}},
                {'x': Pivot3.index, 'y': Pivot3[Pivot3.columns[2]].values, 'name': Pivot3.columns[2],'marker' : { "color" : LineColor3}},
            ],
            'layout': {
                'plot_bgcolor': graph_colors,
                'paper_bgcolor': graph_colors,
                'title': dict(text =str(Asset_B),
                               font =dict(
                               size=16,
                               color = 'cyan')),
                'legend': dict(font=dict(color='cyan'),
                               orientation="h",
                               size=12,
                               style={'margin-top': 100}),
                'xaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=8,
                        color='cyan'
                    )),
                'yaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Helvetica, monospace',
                        size=8,
                        color='cyan'
                    )),

                'margin': dict(
                    l=30,
                    r=30,
                    b=0,
                    t=35,
                    pad=4)

            }
        }))

    children.append(dcc.Graph(
        figure={
            'data': [
                {'x': RollingBeta.index, 'y': RollingBeta[RollingBeta.columns[0]].values,'marker' : { "color" : LineColor1}},
            ],
            'layout': {
                'plot_bgcolor': graph_colors,
                'paper_bgcolor': graph_colors,
                'title': dict(text ='Rolling Beta',
                               font =dict(
                               size=16,
                               color = 'cyan')),
                'legend': dict(font=dict(color='cyan'),
                               orientation="h",
                               size=12,
                               style={'margin-top': 100}),
                'xaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=8,
                        color='cyan'
                    )),
                'yaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Helvetica, monospace',
                        size=8,
                        color='cyan'
                    )),

                'margin': dict(
                    l=40,
                    r=40,
                    b=100,
                    t=35,
                    pad=4),
                "height": 700

            }
        }))
    children.append(dcc.Graph(

        figure={
            'data': [
                {'x': RollingPvalue.index, 'y': RollingPvalue[RollingPvalue.columns[0]].values, 'name': 'P-valiue','marker' : { "color" : LineColor1}},
            ],
            'layout': {
                'title': dict(text ='Cointegration Test',
                               font =dict(
                               size=16,
                               color = 'cyan')),
                'plot_bgcolor': graph_colors,
                'paper_bgcolor': graph_colors,
                'legend': dict(font=dict(color='cyan'),
                               orientation="h",
                               size=12,
                               style={'margin-top': 100}),
                'xaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=8,
                        color='cyan'
                    )),
                'yaxis': dict(color='cyan',
                    titlefont=dict(
                        family='Helvetica, monospace',
                        size=8,
                        color='cyan'
                    )),

                'margin': dict(
                    l=40,
                    r=40,
                    b=100,
                    t=35,
                    pad=4),
                "height": 700
            }
        }))

    return children  # figure,figure2,figure3,figure4,figure5,figure6


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)



