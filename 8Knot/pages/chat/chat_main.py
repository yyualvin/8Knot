from dash import html, dcc
import dash
import dash_bootstrap_components as dbc
import warnings

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/chat")

layout = dbc.Card(
    [
        dbc.Input(
            id="chat-input",
            placeholder="Type your message...",
            type="text",
            style={
                'color': 'white',
                'backgroundColor': '#FFFFFF',
                'border': '1px solid #1D1D1D',
                'borderRadius': '20px',
                'width': '100%',
                'maxWidth': '600px'
            }
        )
    ],
    style={
        'backgroundColor': '#1D1D1D', 
        'height': '700px', 
        'width': 'calc(100vw - 60px)',
        'borderRadius': '20px', 
        'border': '1px solid #1D1D1D',
        'margin': '20px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'flex-end',  # Push content to bottom
        'alignItems': 'center',       # Center horizontally
        'padding': '20px'             # Add padding around the edges
    }
)