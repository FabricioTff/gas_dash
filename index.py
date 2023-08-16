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
                            dcc.Graph(id = "static-maxmin", config={'displayModeBar': False, 'showTips': False})
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
                        ], sm = 12, md= 6),
                    ])
                ])
            ])
        ])
    ]),
    
    ###### Row 2 #######
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3("Preço x Estado"),
                            html.H6("Comparação temporal entre estados")
                        ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id = "preco_estado", config={'displayModeBar': False, 'showTips': False})
                        ])
                    ])
                    ])
                ])
            ])
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
                                ], sm = 6),
                                dbc.Col([
                                    dcc.Dropdown(
                                        id = "select_estado2",
                                        clearable= False,
                                        className= 'dbc',
                                        value= df_main.at[df_main.index[2], "ESTADO"],
                                        options= [{"label": x , "value": x } for x in df_main["ESTADO"].unique()]
                                    )
                                ], sm = 6),
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id = "compare_graph", config={'displayModeBar': False, 'showTips': False})
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ], sm = 4),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Teste"),
                        ])
                    ])
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Teste2")
                        ])
                    ])
                ])
            ])
        ])
    ])



], fluid=True, style={'height': '100%'})


# ======== Callbacks ========== #


# Run server
if __name__ == '__main__':
    app.run_server(debug=True)

