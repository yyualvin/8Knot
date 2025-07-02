from dash import html, dcc, Input, Output, State, callback, no_update
import dash
import dash_bootstrap_components as dbc
import datetime
import random
import warnings

# Import visualization components
from ..repo_overview.visualizations.code_languages import gc_code_language
from ..contributions.visualizations.commits_over_time import gc_commits_over_time
from ..contributors.visualizations.contrib_importance_pie import gc_contrib_importance_pie

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/chat")

# Canned AI responses for demonstration
CANNED_RESPONSES = [
    {"text": "I'm here to help you analyze your repository data! What would you like to know?", "has_cards": False, "cards": []},
    {"text": "Based on the repository metrics, I can see some interesting patterns in your project.", "has_cards": False, "cards": []},
    {"text": "That's a great question! Let me analyze the data to provide you with insights.", "has_cards": False, "cards": []},
    {"text": "I can help you understand contributor behavior, code metrics, and project health.", "has_cards": False, "cards": []},
    {"text": "Here's the commit activity showing trends over time:", "has_cards": True, "cards": [gc_commits_over_time]},
    {"text": "Let me show you the code language distribution for your repository:", "has_cards": True, "cards": [gc_code_language]},
    {"text": "Here's an analysis of contributor importance in your project:", "has_cards": True, "cards": [gc_contrib_importance_pie]},
    {"text": "Here's a comprehensive view of your repository with multiple visualizations:", "has_cards": True, "cards": [gc_code_language, gc_commits_over_time]},
    {"text": "Let me show you both language distribution and contributor analysis:", "has_cards": True, "cards": [gc_code_language, gc_contrib_importance_pie]},
]



def create_message_bubble(message, is_user=True, timestamp=None, card_components=None, message_id=None):
    """Create a message bubble component with optional list of card components"""
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%H:%M")
    
    if message_id is None:
        message_id = f"msg-{random.randint(1000, 9999)}"
    
    # Determine message styling
    align = "end" if is_user else "start"
    bg_color = "#007bff" if is_user else "#333333"
    text_color = "white" if is_user else "#ffffff"
    
    # Create basic message content
    message_content = [
        html.P(message, className="mb-2", style={"margin": "0"}),
        html.Small(timestamp, style={"font-size": "0.8em", "color": "#999999"})
    ]
    
    # Add visualization dropdown if card components are provided
    if card_components and len(card_components) > 0:
        # Create button text based on number of visualizations
        button_text = "View Visualization" if len(card_components) == 1 else f"View {len(card_components)} Visualizations"
        
        visualization_dropdown = [
            html.Hr(style={"margin": "10px 0", "border-color": "#555555"}),
            dbc.Button(
                [
                    html.I(className="fas fa-chart-bar me-2"),
                    button_text + " ",
                    html.I(className="fas fa-chevron-down", id={"type": "chevron", "index": message_id})
                ],
                id={"type": "btn", "index": message_id},
                className="btn-sm",
                color="light",
                outline=True,
                style={
                    "border-color": "#555555",
                    "color": "#ffffff",
                    "font-size": "0.85em",
                    "margin-bottom": "10px"
                }
            ),
            dbc.Collapse(
                html.Div([
                    html.Div(card, style={"margin-bottom": "15px"}) for card in card_components
                ]),
                id={"type": "collapse", "index": message_id},
                is_open=False
            )
        ]
        message_content.extend(visualization_dropdown)
    
    # Return the complete message bubble
    return dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody(message_content),
                style={
                    "background-color": bg_color,
                    "color": text_color,
                    "border": "none",
                    "border-radius": "18px",
                    "width": "100%",
                    "margin-bottom": "10px",
                    "box-shadow": "0 2px 8px rgba(0,0,0,0.15)"
                }
            ),
            width=10
        ),
        justify=align,
        className="mb-2"
    )

layout = dbc.Container([
    # Chat messages container
    dbc.Row([
        dbc.Col([
            html.Div(
                id="chat-messages",
                children=[
                    create_message_bubble("Hello! I'm your 8Knot AI assistant. I can help you analyze repository data, understand metrics, and provide insights about your projects. What would you like to know?", 
                                         is_user=False, message_id="welcome-msg")
                ],
                style={
                    "height": "calc(100vh - 400px)",
                    "overflow-y": "auto",
                    "border": "1px solid #333333",
                    "border-radius": "10px",
                    "padding": "20px",
                    "background-color": "#1D1D1D",
                    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"
                }
            )
        ], width=12)
    ], className="mb-2"),
    
    # Input section
    dbc.Row([
        dbc.Col([
            dbc.Input(
                id="chat-input",
                placeholder="Type your message and press Enter...",
                type="text",
                style={
                    "border-radius": "25px",
                    "padding": "15px 20px",
                    "font-size": "16px",
                    "border": "2px solid #333333",
                    "background-color": "#1D1D1D",
                    "color": "#ffffff",
                    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"
                }
            )
        ], width=12)
    ]),
    
    # Store for message history
    dcc.Store(id="message-history", data=[]),
    
    # Interval for auto-scroll (optional)
    dcc.Interval(id="scroll-interval", interval=100, n_intervals=0, disabled=True)
    
], fluid=True, style={"max-width": "1000px", "margin": "0 auto", "padding": "10px", "height": "100vh"})

# Callback to handle sending messages
@callback(
    [Output("chat-messages", "children"),
     Output("message-history", "data"),
     Output("chat-input", "value")],
    [Input("chat-input", "n_submit")],
    [State("chat-input", "value"),
     State("message-history", "data")]
)
def send_message(input_submit, message, history):
    if not message or message.strip() == "":
        return no_update, no_update, no_update
    
    # Add user message to history
    timestamp = datetime.datetime.now().strftime("%H:%M")
    user_message = {"message": message, "is_user": True, "timestamp": timestamp, "has_cards": False, "cards": []}
    
    # Generate AI response
    ai_response = random.choice(CANNED_RESPONSES)
    ai_timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # Create AI message with potential cards
    ai_message = {
        "message": ai_response["text"], 
        "is_user": False, 
        "timestamp": ai_timestamp,
        "has_cards": ai_response["has_cards"],
        "cards": ai_response.get("cards", [])
    }
    
    # Update history
    new_history = history + [user_message, ai_message]
    
    # Create message bubbles for display
    message_bubbles = []
    for i, msg in enumerate(new_history):
        # Get card components if message has any
        card_components = []
        message_id = f"msg-{i}"
        
        if not msg["is_user"] and msg.get("has_cards", False):
            card_components = msg.get("cards", [])
        
        bubble = create_message_bubble(
            msg["message"], 
            msg["is_user"], 
            msg["timestamp"],
            card_components=card_components,
            message_id=message_id
        )
        message_bubbles.append(bubble)
    
    return message_bubbles, new_history, ""

# Clientside callback to auto-scroll to bottom when new messages are added
dash.clientside_callback(
    """
    function(children) {
        setTimeout(function() {
            var chatContainer = document.getElementById('chat-messages');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 100);
        return window.dash_clientside.no_update;
    }
    """,
    Output("scroll-interval", "disabled"),
    Input("chat-messages", "children"),
    prevent_initial_call=True
)

# Clientside callback to handle visualization dropdown toggles
dash.clientside_callback(
    """
    function(n_clicks, is_open) {
        if (n_clicks) {
            return !is_open;
        }
        return is_open;
    }
    """,
    Output({"type": "collapse", "index": dash.dependencies.MATCH}, "is_open"),
    Input({"type": "btn", "index": dash.dependencies.MATCH}, "n_clicks"),
    State({"type": "collapse", "index": dash.dependencies.MATCH}, "is_open"),
    prevent_initial_call=True
)

# Clientside callback to rotate chevron icon
dash.clientside_callback(
    """
    function(is_open) {
        if (is_open) {
            return "fas fa-chevron-up";
        }
        return "fas fa-chevron-down";
    }
    """,
    Output({"type": "chevron", "index": dash.dependencies.MATCH}, "className"),
    Input({"type": "collapse", "index": dash.dependencies.MATCH}, "is_open"),
    prevent_initial_call=True
)

