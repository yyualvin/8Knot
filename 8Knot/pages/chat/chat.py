from dash import html, dcc, Input, Output, State, callback, no_update
import dash
import dash_bootstrap_components as dbc
import datetime
import warnings

# Import Pinecone manager for vector database queries
from .pinecone_manager import get_default_index, calculate_embedding

# Repo Overview visualizations
from ..repo_overview.visualizations.code_languages import gc_code_language
from ..repo_overview.visualizations.ossf_scorecard import gc_ossf_scorecard
from ..repo_overview.visualizations.package_version import gc_package_version
from ..repo_overview.visualizations.repo_general_info import gc_repo_general_info

# Contributions visualizations
from ..contributions.visualizations.commits_over_time import gc_commits_over_time
from ..contributions.visualizations.issues_over_time import gc_issues_over_time
from ..contributions.visualizations.issue_staleness import gc_issue_staleness
from ..contributions.visualizations.pr_staleness import gc_pr_staleness
from ..contributions.visualizations.pr_over_time import gc_pr_over_time
from ..contributions.visualizations.cntrib_issue_assignment import gc_cntrib_issue_assignment
from ..contributions.visualizations.issue_assignment import gc_issue_assignment
from ..contributions.visualizations.pr_assignment import gc_pr_assignment
from ..contributions.visualizations.cntrb_pr_assignment import gc_cntrib_pr_assignment
from ..contributions.visualizations.pr_first_response import gc_pr_first_response
from ..contributions.visualizations.pr_review_response import gc_pr_review_response

# Contributors visualizations
from ..contributors.visualizations.contrib_drive_repeat import gc_contrib_drive_repeat
from ..contributors.visualizations.first_time_contributions import gc_first_time_contributions
from ..contributors.visualizations.contributors_types_over_time import gc_contributors_over_time
from ..contributors.visualizations.active_drifting_contributors import gc_active_drifting_contributors
from ..contributors.visualizations.new_contributor import gc_new_contributor
from ..contributors.visualizations.contrib_activity_cycle import gc_contrib_activity_cycle
from ..contributors.visualizations.contribs_by_action import gc_contribs_by_action
from ..contributors.visualizations.contrib_importance_pie import gc_contrib_importance_pie as gc_contrib_importance_pie_contributors
from ..contributors.visualizations.contrib_importance_over_time import gc_lottery_factor_over_time

# CHAOSS metrics visualizations
from ..chaoss.visualizations.contrib_importance_pie import gc_contrib_importance_pie as gc_contrib_importance_pie_chaoss
from ..chaoss.visualizations.project_velocity import gc_project_velocity

# Codebase Visualizations
from ..codebase.visualizations.cntrb_file_heatmap import gc_cntrb_file_heatmap
from ..codebase.visualizations.contribution_file_heatmap import gc_contribution_file_heatmap
from ..codebase.visualizations.reviewer_file_heatmap import gc_reviewer_file_heatmap

# Affiliations Visualizations
from ..affiliation.visualizations.commit_domains import gc_commit_domains
from ..affiliation.visualizations.gh_org_affiliation import gc_gh_org_affiliation
from ..affiliation.visualizations.org_associated_activity import gc_org_associated_activity
from ..affiliation.visualizations.org_core_contributors import gc_org_core_contributors
from ..affiliation.visualizations.unqiue_domains import gc_unique_domains

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/chat")

def query_relevant_graphs(user_message, top_k=5):
    """Query the vector database for relevant graphs based on user message"""
    try:
        # Get the index client
        index_client = get_default_index()
        if index_client is None:
            print("Vector database not available, returning empty results")
            return []
        
        # Calculate embedding for user message
        user_embedding = calculate_embedding(user_message)
        
        # Query the vector database
        results = index_client.query(
            vector=user_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract identifiers from metadata and convert to variables
        selected_graphs = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            identifier = metadata.get("identifier")
            
            if identifier:
                # Use globals() to convert identifier to variable name
                if identifier in globals():
                    graph_component = globals()[identifier]
                    selected_graphs.append(graph_component)
        
        return selected_graphs
        
    except Exception as e:
        print(f"Error querying vector database: {e}")
        return []





def create_message_bubble(message, is_user=True, timestamp=None, card_components=None, message_id=None):
    """Create a message bubble component with optional list of card components"""
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%H:%M")
    
    if message_id is None:
        message_id = f"msg-{datetime.datetime.now().strftime('%H%M%S%f')}"
    
    # Determine message styling
    align = "end" if is_user else "start"
    bg_color = "#292929" if is_user else "transparent"
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
            html.Hr(style={"margin": "10px 0", "border-color": "transparent"}),
            dbc.Button(
                [
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
                    "margin-bottom": "10px",
                    "border-radius": "20px"
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
    
    # Set width based on message type
    bubble_width = 6 if is_user else 12
    
    # Create card style with conditional styling for AI vs user messages
    card_style = {
        "background-color": bg_color,
        "color": text_color,
        "border": "none",
        "margin-bottom": "10px"
    }
    
    # Add bubble styling only for user messages
    if is_user:
        card_style.update({
            "border-radius": "18px",
            "box-shadow": "0 2px 8px rgba(0,0,0,0.15)"
        })
    
    # Return the complete message bubble
    return dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody(message_content),
                style=card_style
            ),
            width=bubble_width
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
    
], fluid=True, style={"max-width": "1400px", "margin": "0 auto", "padding": "10px", "height": "100vh"})

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
    
    # Generate AI response using vector database query
    ai_timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # Query vector database for relevant graphs
    relevant_graphs = query_relevant_graphs(message, top_k=5)
    
    # Create AI message with relevant graphs
    ai_message = {
        "message": "Here are some graphs that may be useful to you:", 
        "is_user": False, 
        "timestamp": ai_timestamp,
        "has_cards": len(relevant_graphs) > 0,
        "cards": relevant_graphs
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

