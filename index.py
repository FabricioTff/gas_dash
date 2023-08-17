import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
import pandas as pd 
import numpy as np


# ========= App ============== #

FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc_css])
app.scripts.config.serve_locally = True
server = app.server


# ========== Styles ============ #

template_theme1 = "flatly"
template_theme2 = "vapor"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.VAPOR

tab_card = {'height':"100%"}

main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.9, 
                "xanchor":"left",
                "x":0.1,
                "title": {"text": None},
                "font" :{"color":"white"},
                "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":0, "r":0, "t":10, "b":0}
}


# ===== Reading n cleaning File ====== #

df_main = pd.read_csv("data_gas.csv")
df_main["DATA INICIAL"] = pd.to_datetime(df_main["DATA INICIAL"])
df_main["DATA FINAL"] = pd.to_datetime(df_main["DATA FINAL"])

df_main["DATA MEDIA"] = ((df_main["DATA FINAL"] - df_main["DATA INICIAL"])/2) + df_main["DATA INICIAL"]
df_main.rename(columns= {"DATA MEDIA":"DATA", "PREÇO MÉDIO REVENDA": "VALOR REVENDA (R$/L)"}, inplace=True)

df_main["ANO"] = df_main["DATA"].apply(lambda x: str(x.year))
df_main = df_main.reset_index() 

df_main.drop(['UNIDADE DE MEDIDA', 'COEF DE VARIAÇÃO REVENDA', 'COEF DE VARIAÇÃO DISTRIBUIÇÃO', 
    'NÚMERO DE POSTOS PESQUISADOS', 'DATA INICIAL', 'DATA FINAL', 'PREÇO MÁXIMO DISTRIBUIÇÃO', 'PREÇO MÍNIMO DISTRIBUIÇÃO', 
    'DESVIO PADRÃO DISTRIBUIÇÃO', 'MARGEM MÉDIA REVENDA', 'PREÇO MÍNIMO REVENDA', 'PREÇO MÁXIMO REVENDA', 'DESVIO PADRÃO REVENDA', 
    'PRODUTO', 'PREÇO MÉDIO DISTRIBUIÇÃO'], inplace=True, axis=1)
 
df_store = df_main.to_dict()

# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Armazenar o dataset
    dcc.Store(id='dataset', data=df_store),
    dcc.Store(id='dataset_fixed', data=df_store),
    
    # Layout 
    ###### Row 1 #######
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Legend("Gas prices Analysis")
                        ], sm = 8),
                        dbc.Col([
                            html.I(className="fa fa-filter", style= {"font-size": "300%"})
                        ],sm = 4, align = 'center'),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id= 'theme', themes = [url_theme1, url_theme2]),
                            html.Legend("Fabricio Ferreira")                                
                        ])
                    ], style= {"margin-top": "10px"}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Linkedin", href = "https://www.linkedin.com/in/fabricioferreiratf/", target="_blank")
                        ])
                    ], style= {"margin-top": "10px"})
                    ])
                ])
            ], style=tab_card)
        ],sm=4,lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3("Máximos e Mínimos"),
                            dcc.Graph(id = "static_maxmin", config={'displayModeBar': False, 'showTips': False})
                        ])
                    ])
                ])
            ], style=tab_card)
        ],sm=8, lg=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Ano de análise"),
                            dcc.Dropdown(
                                id = "select_ano",
                                value= df_main.at[df_main.index[1], "ANO"],
                                clearable= False,
                                className= 'dbc',
                                options= 
                                [{"label": x, "value":x } for x in df_main["ANO"].unique()
                            ])
                        ], sm=6),
                        dbc.Col([
                            html.H6("Região de análise"),
                            dcc.Dropdown(
                                id = "select_regiao",
                                value= df_main.at[df_main.index[1], "REGIÃO"],
                                clearable= False,
                                className= 'dbc',
                                options=[
                                    {"label": x, "value": x} for x in df_main["REGIÃO"].unique()
                                ]
                            )
                        ], sm =6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='regiaobar_graph', config={'displayModeBar': False, 'showTips': False})
                        ], sm = 12, md= 6),
                        dbc.Col([
                            dcc.Graph(id='estadobar_graph', config={'displayModeBar': False, 'showTips': False})
                        ], sm = 12, md= 6)
                    ],style= {"column-gap":"0px"})
                ])
            ],style= tab_card)
        ],sm=12 , lg = 7)
    ],className= "g-2 my-auto"),
    
    ###### Row 2 #######
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3("Preço x Estado"),
                            html.H6("Comparação temporal entre estados"),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id = "select_estado0",
                                        className= 'dbc',
                                        value= df_main.at[df_main.index[1], "ESTADO"],
                                        options= [{"label": x , "value": x } for x in df_main["ESTADO"].unique()],
                                        multi = True
                                    )
                                ], sm = 10)
                            ])
                            
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id = "animation_graph", config={'displayModeBar': False, 'showTips': False})
                            ])
                        ])
                    ])
                ])
            ],style=tab_card)
        ], sm = 5),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3("Comparação direta"),
                            html.H6("Qual preço é menor em um dado periodo de tempo"),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id = "select_estado1",
                                        clearable= False,
                                        className= 'dbc',
                                        value= df_main.at[df_main.index[1], "ESTADO"],
                                        options= [{"label": x , "value": x } for x in df_main["ESTADO"].unique()]
                                    )
                                ], sm = 10,  md = 6),
                                dbc.Col([
                                    dcc.Dropdown(
                                        id = "select_estado2",
                                        clearable= False,
                                        className= 'dbc',
                                        value= df_main.at[df_main.index[3], "ESTADO"],
                                        options= [{"label": x , "value": x } for x in df_main["ESTADO"].unique()]
                                    )
                                ], sm = 10, md = 6),
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id = "direct_comparison_graph", config={'displayModeBar': False, 'showTips': False})
                                    ])
                                ]),
                                html.P(id="desc_comparison", style={"color": "gray", "font-size":"80%"})
                            ])
                        ])
                    ])
                ])
            ],style=tab_card)
        ], sm = 12, md = 6, lg = 4),
        
        dbc.Col([
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="card1_indicators", config={'displayModeBar': False, 'showTips': False}, style= {"margin-top": "30px"})
                        ])
                    ],style=tab_card)
                ])
            ], justify='center', style={'padding-bottom': '7px', 'height': '50%'}),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="card2_indicators", config={'displayModeBar': False, 'showTips': False}, style= {"margin-top": "30px"})
                        ])
                    ],style=tab_card)
                ])
            ], justify='center', style={'height': '50%'})
            
        ],sm=12, lg = 3,style={"height": "100%"})
    ],className= "g-2 my-auto"),
       
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        dbc.Button([html.I(className="fa fa-play")], id="play-button", style={"margin-right": "15px"}),
                        dbc.Button([html.I(className="fa fa-stop")], id="stop-button"),
                    ], sm= 12, md = 1, style={"justify-content":"center", "margin-top":"10px"}),
                    dbc.Col([
                        dcc.RangeSlider(
                            id="rangeslider",
                            marks = {int(x): f"{x}" for x in df_main["ANO"].unique()},
                            step= 3,
                            min=int(df_main["ANO"].min()),
                            max=int(df_main["ANO"].max()),
                            value = [int(df_main["ANO"].min()),int(df_main["ANO"].max())],
                            dots= True,
                            pushable= 3,
                            tooltip= {"always_visible": False, "placement": "bottom"}
                        )
                    ],sm = 12, md = 10, style= {"margin-top": "15px"}),
                    dcc.Interval(id="interval", interval = 2000)
                ], class_name='g-1', style={"height": "20%", "justify-content":"center"})
            ],style= tab_card)
        ])        
    ],className= "g-2 my-auto")
    
], fluid=True, style={'height': '100%'})


# ======== Callbacks ========== #

@app.callback(
    Output("static_maxmin", "figure"),
    [Input('dataset', "data"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def func(data, toggle):
    template = template_theme1 if toggle else template_theme2
    
    dff = pd.DataFrame(data)
    
    min = dff.groupby(["ANO"])["VALOR REVENDA (R$/L)"].min()
    max = dff.groupby(["ANO"])["VALOR REVENDA (R$/L)"].max()

    final_df = pd.concat([max, min], axis = 1)
    final_df.columns = ["Máximo", "Mínimo"]
    
    fig = px.line(final_df, x = final_df.index, y = final_df.columns, template=template)
    
    fig.update_layout(main_config, height = 150, xaxis_title = None, yaxis_title = None)
    
    return fig





# Run server
if __name__ == '__main__':
    app.run_server(debug=True)

