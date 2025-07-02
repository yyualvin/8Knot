from dash import html, dcc, Input, Output, State, callback, no_update
import dash
import dash_bootstrap_components as dbc
import datetime
import random
import warnings

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/chat")

# Canned AI responses for demonstration
CANNED_RESPONSES = [
    "I'm here to help you analyze your repository data! What would you like to know?",
    "Based on the repository metrics, I can see some interesting patterns in your project.",
    "That's a great question! Let me analyze the data to provide you with insights.",
    "I can help you understand contributor behavior, code metrics, and project health.",
    "Interesting! The data shows some trends that might be worth exploring further.",
    "Let me break down those metrics for you in a more digestible way.",
    "From what I can see in the repository data, here are some key insights...",
    "That's an important aspect of software development analytics. Here's what the data tells us...",
]

def create_message_bubble(message, is_user=True, timestamp=None):
    """Create a message bubble component"""
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%H:%M")
    
    bubble_class = "user-message" if is_user else "ai-message"
    align = "end" if is_user else "start"
    bg_color = "#007bff" if is_user else "#333333"
    text_color = "white" if is_user else "#ffffff"
    
    return dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P(message, className="mb-2", style={"margin": "0"}),
                    html.Small(timestamp, style={"font-size": "0.8em", "color": "#999999"})
                ]),
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
                                         is_user=False)
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
    user_message = {"message": message, "is_user": True, "timestamp": timestamp}
    
    # Generate AI response
    ai_response_text = random.choice(CANNED_RESPONSES)
    ai_timestamp = datetime.datetime.now().strftime("%H:%M")
    ai_message = {"message": ai_response_text, "is_user": False, "timestamp": ai_timestamp}
    
    # Update history
    new_history = history + [user_message, ai_message]
    
    # Create message bubbles for display
    message_bubbles = []
    for msg in new_history:
        bubble = create_message_bubble(
            msg["message"], 
            msg["is_user"], 
            msg["timestamp"]
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

