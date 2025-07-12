from dash import html, dcc
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import warnings
import pages.chat.chat_callbacks

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/chat")

layout = dbc.Card(
    [
        # Store component to hold chat messages
        dcc.Store(id="chat-messages", data=[], storage_type="session"),
        
        # Repository selection area
        html.Div(
            [
                html.Label("Select Repository for Chat:", style={'color': 'white', 'marginBottom': '10px'}),
                dmc.Select(
                    id="chat-repo-selection",
                    placeholder="Select a repository to chat about",
                    classNames={"values": "dmc-multiselect-custom"},
                    searchable=True,
                    clearable=True,
                    style={'marginBottom': '15px'}
                ),
            ],
            style={'padding': '10px', 'borderBottom': '1px solid #333'}
        ),
        
        # Chat messages display area
        html.Div(
            id="chat-messages-display",
            style={
                'height': '550px',
                'overflow-y': 'auto',
                'padding': '10px',
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column',
                'scrollBehavior': 'smooth',
                'gap': '10px'
            }
        ),
        
        # Input area at bottom
        html.Div(
            dcc.Input(
                id="chat-input",
                placeholder="Ask 8Knot about the selected repository (press Enter to send)",
                type="text",
                style={
                    'width': '100%',
                    'maxWidth': '600px'
                }
            ),
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'padding': '10px'
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
        'padding': '20px'
    }
)

