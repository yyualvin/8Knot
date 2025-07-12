from dash import html, callback, Input, Output, State, clientside_callback
from datetime import datetime
from pages.chat.llm import call_openai
# Import the ossf scorecard
from pages.repo_overview.visualizations.ossf_scorecard import ossf_scorecard_context as ossf_scorecard_context
from app import augur

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

# Callback for populating chat repo dropdown
@callback(
    [Output("chat-repo-selection", "data"),
     Output("chat-repo-selection", "value")],
    [Input("repo-choices", "data")]
)
def populate_chat_repo_dropdown(repo_ids):
    if not repo_ids:
        return [], None
    
    # Create dropdown options from repo_ids
    data_array = []
    for repo_id in repo_ids:
        entry = {"value": repo_id, "label": augur.repo_id_to_git(repo_id)}
        data_array.append(entry)
    
    # Default to first repo if available
    default_value = repo_ids[0] if repo_ids else None
    return data_array, default_value

# Callback to handle sending messages
@callback(
    [Output("chat-messages", "data"), 
     Output("chat-input", "value")],
    [Input("chat-input", "n_submit")],
    [State("chat-input", "value"),
     State("chat-messages", "data"),
     State("chat-repo-selection", "value")]  # Use chat repo selection
)
def send_message(input_submit, message, current_messages, selected_repo):
    if not message or message.strip() == "":
        return current_messages, message
    
    # Get OSSF data if a repo is selected
    ossf_info = ""
    if selected_repo:
        try:
            repo_url = augur.repo_id_to_git(selected_repo)
            
            ossf_results = ossf_scorecard_context(selected_repo)
            
            ossf_info = f"""
                        Return plaintext only, no markdown. Try to be concise and to the point.
                        Repository Context: {repo_url} (ID: {selected_repo})
                        {ossf_results}  
                        """
                
        except Exception as e:
            repo_url = augur.repo_id_to_git(selected_repo) if selected_repo else "Unknown"
            ossf_info = f"\n\nRepository Context: {repo_url} selected, but OSSF data unavailable: {str(e)}"
    else:
        ossf_info = "\n\nContext: No repository selected. Please select a repository from the dropdown above to get specific insights."

    # Add user message to the list
    new_message = {
        "text": message.strip(),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "sender": "user"
    }
    
    try:
        # Enhance the message with repo context and actual OSSF data
        enhanced_message = f"{message.strip()}{ossf_info}"
        
        # Call OpenAI and get response
        ai_response = call_openai(enhanced_message)
        
        # Add bot response
        bot_response = {
            "text": ai_response,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "sender": "bot"
        }
        
        updated_messages = current_messages + [new_message, bot_response]
        
    except Exception as e:
        # Handle errors gracefully
        error_response = {
            "text": f"Sorry, there was an error: {str(e)}",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "sender": "bot"
        }
        
        updated_messages = current_messages + [new_message, error_response]
    
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

# Clientside callback to auto-scroll to bottom when new messages are added
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
