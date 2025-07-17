from dash import html, callback, Input, Output, State, clientside_callback
from datetime import datetime
from pages.chat.llm import call_openai
from pages.chat.llm import call_tools

# Import all tool functions directly
from pages.contributions.visualizations.commits_over_time import commits_over_time_tool
from pages.contributions.visualizations.pr_over_time import pull_requests_over_time_tool
from pages.contributions.visualizations.pr_assignment import pull_request_review_status_counts_tool
from pages.contributions.visualizations.pr_review_response import pull_request_conversation_engagement_tool
from pages.contributions.visualizations.pr_first_response import pull_request_first_response_tool
from pages.contributions.visualizations.pr_staleness import pull_request_activity_staleness_tool
from pages.contributions.visualizations.issue_staleness import issue_activity_staleness_tool
from pages.contributions.visualizations.issues_over_time import issues_over_time_tool
from pages.contributions.visualizations.cntrb_pr_assignment import contributor_pull_request_review_assignment_tool
from pages.contributions.visualizations.cntrib_issue_assignment import contributor_issue_assignment_tool

# Pinecone vector search
from pages.chat.tools.embed import *

from app import augur
import json




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
     State("repo-choices", "data"),  # Use repo choices data for multiple repos
     State("chat-repo-selection", "value")]  # Use chat repo selection for focused analysis
)
def send_message(input_submit, message, current_messages, repo_list, selected_repo):
    if not message or message.strip() == "":
        return current_messages, message

    index = create_index("8knot-index", pc)

    tools = search_function(index, message, top_k=5)

    print(tools)
    response = call_tools(message, tools)

    graphs = []
    for tool in response:
        args = getattr(tool, 'arguments', {})
        name = getattr(tool, 'name', None)
        
        # Parse JSON string to dict if needed
        if isinstance(args, str):
            args = json.loads(args)
        
        if name and name in globals():
            import inspect
            func = globals()[name]
            sig = inspect.signature(func)
            
            # Only add parameters that the function accepts
            if "repolist" in sig.parameters:
                args["repolist"] = repo_list
            if "repo" in sig.parameters:
                args["repo"] = selected_repo
            
            graphs.append(func(**args))
        else:
            print(f"Function {name} not found in globals")
            print(f"Available functions: {[k for k in globals().keys() if not k.startswith('_')]}")
    
    # Get OSSF data from repo list
    # results = package_version_graph(repo_list)

    print(graphs)

    full_prompt = f"""
                Return plaintext only, no markdown. Try to be concise and to the point.
                {graphs}  
                """

    # Add user message to the list
    new_message = {
        "text": message.strip(),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "sender": "user"
    }
    

    # Enhance the message with repo context and actual OSSF data
    enhanced_message = f"{message.strip()}{full_prompt}"
    
    # Call OpenAI and get response
    ai_response = call_openai(enhanced_message)
    
    # Add bot response
    bot_response = {
        "text": ai_response,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "sender": "bot"
    }
    
    updated_messages = current_messages + [new_message, bot_response]
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
