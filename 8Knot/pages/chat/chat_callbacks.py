from dash import html, callback, Input, Output, State, clientside_callback
from datetime import datetime

def create_chat_bubble(message_text, timestamp, is_user=False):
    """Creates a chat bubble HTML element with styling."""
    return html.Div(
        [
            html.Div(message_text, style={'marginBottom': '5px'}),
            html.Div(
                timestamp,
                style={
                    'fontSize': '12px',
                    'opacity': '0.7',
                    'textAlign': 'right' if is_user else 'left'
                }
            )
        ],
        style={
            'maxWidth': '70%',
            'padding': '10px 15px',
            'borderRadius': '20px',
            'marginBottom': '10px',
            'wordWrap': 'break-word',
            'alignSelf': 'flex-end' if is_user else 'flex-start',
            'backgroundColor': '#333537' if is_user else 'transparent',
            'color': 'white'
        }
    )

# Callback to handle sending messages
@callback(
    [Output("chat-messages", "data"), 
     Output("chat-input", "value")],
    [Input("chat-input", "n_submit")],
    [State("chat-input", "value"),
     State("chat-messages", "data")]
)
def send_message(input_submit, message, current_messages):
    if not message or message.strip() == "":
        return current_messages, message
    
    # Add new message to the list
    new_message = {
        "text": message.strip(),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "sender": "user"
    }
    
    # Add a simple response (you can replace this with actual AI logic)
    response = {
        "text": f"You said: {message.strip()}",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "sender": "bot"
    }
    
    updated_messages = current_messages + [new_message, response]
    
    return updated_messages, ""

# Callback to display chat messages
@callback(
    Output("chat-messages-display", "children"),
    Input("chat-messages", "data")
)
def display_messages(messages):
    if not messages:
        return html.Div(
            "Start a conversation with 8Knot!",
            style={
                'textAlign': 'center',
                'color': '#888',
                'padding': '20px',
                'fontStyle': 'bold'
            }
        )
    
    message_elements = []
    for msg in messages:
        is_user = msg["sender"] == "user"
        bubble = create_chat_bubble(msg["text"], msg["timestamp"], is_user)
        message_elements.append(bubble)
    
    return message_elements

# Clientside callback to auto-scroll to bottom when new messages are added.
# There is no way to do this in native Dash.
clientside_callback(
    """
    function(messages) {
        // Small delay to ensure DOM is updated
        setTimeout(function() {
            const chatDiv = document.getElementById('chat-messages-display');
            if (chatDiv) {
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }
        }, 100);
        return window.dash_clientside.no_update;
    }
    """,
    Output("chat-messages-display", "data-scroll"),  # Dummy output
    Input("chat-messages", "data")
)
