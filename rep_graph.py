import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# 1. Données
df = pd.read_csv("data_priced.csv")
df['market_price_adj'] = df['price'] * 100
df['diff'] = df['market_price_adj'] - df['theorical_price']

app = dash.Dash(__name__)

def create_quant_chart(data, title):
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.04, # Très collé
        row_heights=[0.7, 0.3]
    )

    # --- HAUT : Prix ---
    # Théorique : Ligne fine
    fig.add_trace(go.Scatter(
        x=data["strike"], y=data["theorical_price"],
        mode='lines+markers',
        name='Theoretical',
        line=dict(color='#1f77b4', width=1.5),
        marker=dict(size=5, symbol='circle')
    ), row=1, col=1)

    # Marché : Points simples
    fig.add_trace(go.Scatter(
        x=data["strike"], y=data["market_price_adj"],
        mode='markers',
        name='Market',
        marker=dict(color='#800000', size=6, symbol='x') # Bordeaux classique
    ), row=1, col=1)

    # --- BAS : Erreur de Pricing (Spread) ---
    # Ligne avec remplissage vers le zéro
    fig.add_trace(go.Scatter(
        x=data["strike"], y=data["diff"],
        mode='lines+markers',
        name='Market - Theo',
        line=dict(color='#555555', width=1),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(85, 85, 85, 0.2)'
    ), row=2, col=1)

    # --- MISE EN FORME "QUANT" STRICTE ---
    fig.update_layout(
        title=dict(text=title, font=dict(family="Arial", size=14, color="black")),
        template="simple_white", # Thème ultra minimaliste
        height=600,
        margin=dict(l=50, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, font=dict(size=11)),
        hovermode="x unified"
    )

    # Axes stricts (lignes noires autour du graphique)
    for row in [1, 2]:
        fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, 
                         showgrid=True, gridwidth=1, gridcolor='#e5e5e5', row=row, col=1)
        fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True, 
                         showgrid=True, gridwidth=1, gridcolor='#e5e5e5', row=row, col=1)

    # Ajustements spécifiques
    fig.update_yaxes(title_text="Price", title_font=dict(size=12), row=1, col=1)
    fig.update_yaxes(title_text="Spread", title_font=dict(size=12), zeroline=True, zerolinewidth=1, zerolinecolor='black', row=2, col=1)
    fig.update_xaxes(title_text="Strike", title_font=dict(size=12), row=2, col=1)

    return fig

# 2. Layout global
app.layout = html.Div(style={'backgroundColor': '#ffffff', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'}, children=[
    
    html.H3("Option Pricing Analysis", style={'borderBottom': '1px solid black', 'paddingBottom': '10px', 'marginBottom': '20px'}),
    
    # Conteneur simple, bord à bord
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'width': '100%'}, children=[
        
        # Colonne Call
        html.Div([
            dcc.Graph(figure=create_quant_chart(df[df["direction"] == 1], "ONE TOUCH CALL"))
        ], style={'width': '50%', 'borderRight': '1px solid #ddd', 'paddingRight': '10px'}),
        
        # Colonne Put
        html.Div([
            dcc.Graph(figure=create_quant_chart(df[df["direction"] == 0], "ONE TOUCH PUT"))
        ], style={'width': '50%', 'paddingLeft': '10px'})
        
    ])
])

if __name__ == '__main__':
    app.run(debug=True)