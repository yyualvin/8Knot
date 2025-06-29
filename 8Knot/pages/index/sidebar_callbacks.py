import dash
from dash import callback, Input, Output, State
from dash.dependencies import Input, Output, State


# Dash callback for sidebar toggle
@dash.callback(
    [
        Output("sidebar-card", "style"),
        Output("sidebar-full-content", "style"),
        Output("repo-overview-text", "style"),
        Output("contributions-text", "style"),
        Output("contributors-text", "style"),
        Output("affiliation-text", "style"),
        Output("chaoss-text", "style"),
        Output("main-card", "style"),
        Output("sidebar-toggle-icon", "className"),
        Output("sidebar-collapsed", "data"),
        Output("contributors-dropdown-content", "style", allow_duplicate=True),
        Output("contributors-dropdown-icon", "className", allow_duplicate=True),
        Output("contributors-dropdown-open", "data", allow_duplicate=True),
        Output("contributors-dropdown-wrapper", "className", allow_duplicate=True),
    ],
    [
        Input("sidebar-toggle-btn", "n_clicks"), 
        Input("contributors-dropdown-toggle", "n_clicks")
    ],
    [
        State("sidebar-collapsed", "data"), 
        State("contributors-dropdown-open", "data")
    ],
    prevent_initial_call=True,
)
def toggle_sidebar(toggle_n, contributors_n, collapsed, contributors_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # If contributors dropdown was clicked, always expand sidebar and toggle dropdown
    if trigger_id == "contributors-dropdown-toggle":
        collapsed = False  # Force expand
        contributors_open = not contributors_open
    # If sidebar toggle was clicked, toggle sidebar state
    elif trigger_id == "sidebar-toggle-btn":
        collapsed = not collapsed
        # When collapsing, close contributors dropdown
        if collapsed:
            contributors_open = False
    
    # Text visibility style
    text_style = {"display": "none"} if collapsed else {"display": "inline"}
    
    # Full content visibility style
    full_content_style = {"display": "none"} if collapsed else {"display": "block"}
    
    sidebar_style = {
        "borderRadius": "14px 0 0 14px",
        "height": "95vh",
        "width": "80px" if collapsed else "340px",
        "background": "#1D1D1D",
        "color": "#fff",
        "padding": "32px 12px 32px 12px" if collapsed else "32px 18px 32px 18px",
        "boxShadow": "none",
        "border": "none",
        "borderRight": "1px solid #404040",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "flex-start",
        "margin": "0px 0 20px 10px",
        "zIndex": 2,
        "overflow": "hidden",
    }
    
    main_style = {
        "borderRadius": "0 14px 14px 0",
        "padding": "0px 40px 40px 40px",
        "margin": "0px 10px 20px 0",
        "width": f"calc(99vw - {'80px' if collapsed else '340px'})",
        "maxWidth": f"calc(100vw - {'80px' if collapsed else '340px'})",
        "boxShadow": "none",
        "border": "none",
        "background": "#1D1D1D",
        "height": "95vh",
        "overflowY": "auto",
        "overflowX": "hidden",
        "display": "flex",
        "flexDirection": "column",
        "marginLeft": "0",
    }
    
    icon = "fas fa-chevron-right" if collapsed else "fas fa-chevron-left"
    
    # Contributors dropdown styling
    if contributors_open:
        dropdown_content_style = {"display": "block", "paddingTop": "4px", "borderRadius": "0 0 8px 8px"}
        dropdown_icon_class = "bi bi-chevron-up"
        dropdown_wrapper_class = "dropdown-open"
    else:
        dropdown_content_style = {"display": "none", "height": 0, "overflow": "hidden", "padding": 0, "border": 0}
        dropdown_icon_class = "bi bi-chevron-down"
        dropdown_wrapper_class = ""
    
    return (
        sidebar_style,
        full_content_style,
        text_style, text_style, text_style, text_style, text_style,
        main_style,
        icon,
        collapsed,
        dropdown_content_style,
        dropdown_icon_class,
        contributors_open,
        dropdown_wrapper_class,
    )


# Simplified callback for navigation links (just closes dropdown)
@dash.callback(
    [
        Output("contributors-dropdown-content", "style", allow_duplicate=True),
        Output("contributors-dropdown-icon", "className", allow_duplicate=True),
        Output("contributors-dropdown-open", "data", allow_duplicate=True),
        Output("contributors-dropdown-wrapper", "className", allow_duplicate=True),
    ],
    [
        Input("repo-overview-navlink", "n_clicks"),
        Input("contributions-navlink", "n_clicks"), 
        Input("affiliation-navlink", "n_clicks"),
        Input("chaoss-navlink", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def close_dropdown_on_navigation(repo_clicks, contrib_clicks, aff_clicks, chaoss_clicks):
    """Close contributors dropdown when any navigation link is clicked"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    # Close dropdown
    dropdown_content_style = {"display": "none", "height": 0, "overflow": "hidden", "padding": 0, "border": 0}
    dropdown_icon_class = "bi bi-chevron-down"
    dropdown_wrapper_class = ""
    
    return dropdown_content_style, dropdown_icon_class, False, dropdown_wrapper_class 