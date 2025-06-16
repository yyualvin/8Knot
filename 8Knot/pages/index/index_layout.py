from dash import html, dcc
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from app import augur
import os
import logging

#  login banner that will be displayed when login is disabled
login_banner = None
if os.getenv("AUGUR_LOGIN_ENABLED", "False") != "True":
    login_banner = html.Div(
        dbc.Alert(
            [
                html.H4(
                    "Login is Currently Disabled",
                    className="alert-heading",
                    style={"color": "black", "fontWeight": "600", "margin": "0 0 8px 0", "textShadow": "none"},
                ),
                html.P(
                    [
                        "If you need to collect data on new repositories, please ",
                        html.A(
                            "create a repository collection request",
                            href="https://github.com/oss-aspen/8Knot/issues/new?template=augur_load.md",
                            target="_blank",
                            style={"fontWeight": "500", "color": "#1565C0"},
                        ),
                        ".",
                    ],
                    style={"color": "#333333", "margin": "0 0 10px 0"},
                ),
            ],
            color="light",
            dismissable=True,
            id="login-disabled-banner",
            className="mb-0",
            style={
                "backgroundColor": "#EDF7ED",  # Light green background
                "borderColor": "#6b8976",  # Darker green border from palette
                "border": "1px solid #6b8976",
                "borderLeft": "5px solid #6b8976",
                "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
                "maxWidth": "400px",
                "padding": "15px",
                "zIndex": "1000",
            },
        ),
        style={"position": "fixed", "top": "70px", "right": "20px", "zIndex": "1000"},  # Position below navbar
    )

# if param doesn't exist, default to False. Otherwise, use the param's value.
# this determines if the login option will be shown or not
if os.getenv("AUGUR_LOGIN_ENABLED", "False") == "True":
    logging.warning("LOGIN ENABLED")
    login_navbar = [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Nav(
                        [
                            dcc.Loading(
                                children=[
                                    html.Div(
                                        id="nav-login-container",
                                        children=[],
                                    ),
                                ]
                            ),
                            dbc.NavItem(
                                dbc.NavLink("Refresh Groups", id="refresh-button", disabled=True),
                            ),
                            dbc.NavItem(
                                dbc.NavLink(
                                    "Manage Groups",
                                    id="manage-group-button",
                                    disabled=True,
                                    href=f"{augur.user_account_endpoint}?section=tracker",
                                    external_link="True",
                                    target="_blank",
                                ),
                            ),
                            dbc.NavItem(
                                dbc.NavLink(
                                    "Log out",
                                    id="logout-button",
                                    disabled=True,
                                    href="/logout/",
                                    external_link=True,
                                ),
                            ),
                            dbc.Popover(
                                children="Login Failed",
                                body=True,
                                id="login-popover",
                                is_open=False,
                                placement="bottom-end",
                                target="nav-dropdown",
                            ),
                        ]
                    )
                )
            ],
            align="center",
        ),
    ]
else:
    logging.warning("LOGIN DISABLED")
    login_navbar = [html.Div()]

# Add Google Fonts link for remote font loading
google_fonts_link = html.Link(
    rel="stylesheet",
    href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@400;500;600;700&display=swap"
)

# navbar for top of screen - fixed design with integrated search and always-hamburger menu
navbar = html.Div([
    google_fonts_link,
    html.Nav(
        className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-xl border-b border-slate-700/20 shadow-lg",
        children=[
            html.Div(
                className="container mx-auto px-4 py-3",
                children=[
                    html.Div(
                        className="flex items-center justify-between",
                        children=[
                            # Logo and Brand Section with Diamond
                            html.Div(
                                className="flex items-center space-x-3 group flex-shrink-0",
                                children=[
                                    html.Div(
                                        className="relative",
                                        children=[
                                            html.Div(
                                                className="w-7 h-7 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 transform rotate-45 rounded-md shadow-lg group-hover:shadow-blue-500/50 transition-all duration-300 group-hover:scale-110 group-hover:rotate-[225deg]",
                                            ),
                                            html.Div(
                                                className="absolute inset-0 w-7 h-7 bg-gradient-to-tl from-cyan-400 via-blue-500 to-purple-600 transform rotate-45 rounded-md opacity-70 group-hover:opacity-90 transition-all duration-300 animate-pulse",
                                            ),
                                        ],
                                    ),
                                    html.A(
                                        "8Knot",
                                        id="navbar-title",
                                        className="text-xl font-black bg-gradient-to-r from-blue-300 via-purple-300 to-pink-300 bg-clip-text text-transparent no-underline hover:from-blue-200 hover:via-purple-200 hover:to-pink-200 transition-all duration-300 tracking-tight",
                                        href="/",
                                        style={"fontFamily": "'Playfair Display', Georgia, serif"},
                                    ),
                                ],
                            ),
                            
                            # Integrated Search Bar (Center)
                            html.Div(
                                className="flex-1 max-w-2xl mx-6",
                                children=[
                                    html.Div(
                                        className="relative",
                                        children=[
                                            # Search Input Field
                                            html.Div(
                                                className="flex items-center bg-slate-800/50 backdrop-blur-sm border border-slate-600/30 rounded-xl shadow-inner",
                                                children=[
                                                    # Search Icon
                                                    html.Div(
                                                        className="pl-4 pr-2 text-slate-400",
                                                        children=[
                                                            html.Span("🔍", className="text-lg"),
                                                        ],
                                                    ),
                                                    # MultiSelect Component
                                                    html.Div(
                                                        className="flex-1",
                                                        children=[
                                                            dmc.MultiSelect(
                                                                id="projects",
                                                                placeholder="Select GitHub repos or organizations...",
                                                                searchable=True,
                                                                clearable=True,
                                                                nothingFound="No matching repos/orgs.",
                                                                variant="unstyled",
                                                                debounce=100,
                                                                data=[augur.initial_multiselect_option()],
                                                                value=[augur.initial_multiselect_option()["value"]],
                                                                style={"fontSize": 14},
                                                                maxDropdownHeight=300,
                                                                zIndex=9999,
                                                                dropdownPosition="bottom",
                                                                transitionDuration=150,
                                                                className="navbar-search-input",
                                                                styles={
                                                                    "input": {
                                                                        "backgroundColor": "transparent",
                                                                        "border": "none",
                                                                        "color": "#e2e8f0",
                                                                        "fontSize": "14px",
                                                                        "padding": "8px 0",
                                                                    },
                                                                    "pill": {
                                                                        "backgroundColor": "rgba(59, 130, 246, 0.1)",
                                                                        "border": "1px solid rgba(59, 130, 246, 0.3)",
                                                                        "color": "#93c5fd",
                                                                    },
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                    # Search Button
                                                    html.Button(
                                                        "Search",
                                                        id="search",
                                                        n_clicks=0,
                                                        className="px-4 py-2 mx-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white text-sm font-semibold rounded-lg transition-all duration-300 shadow-md hover:shadow-lg border-none cursor-pointer",
                                                        style={"fontFamily": "'Inter', sans-serif"},
                                                    ),
                                                ],
                                            ),
                                            # Search Status and Alerts
                                            html.Div(
                                                className="absolute top-full left-0 right-0 mt-2 space-y-2",
                                                children=[
                                                    html.Div(id="search-status", className="search-status-indicator", style={"display": "none"}),
                                                    dbc.Alert(
                                                        children='Please ensure that your spelling is correct. If your selection definitely isn\'t present, please request that it be loaded using the "REPO/ORG Request" button.',
                                                        id="help-alert",
                                                        dismissable=True,
                                                        fade=True,
                                                        is_open=False,
                                                        color="info",
                                                        className="text-sm",
                                                    ),
                                                    dbc.Alert(
                                                        children="List of repos",
                                                        id="repo-list-alert",
                                                        dismissable=True,
                                                        fade=True,
                                                        is_open=False,
                                                        color="light",
                                                        className="text-sm",
                                                        style={"overflow-y": "scroll", "max-height": "300px"},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            
                            # Right Side Controls
                            html.Div(
                                className="flex items-center space-x-3 flex-shrink-0",
                                children=[
                                    # Bot Filter Switch
                                    html.Div(
                                        className="hidden sm:flex items-center",
                                        children=[
                                            dbc.Switch(
                                                id="bot-switch",
                                                label="Bot Filter",
                                                value=True,
                                                input_class_name="botlist-filter-switch",
                                                className="text-slate-300 text-sm",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                        ],
                                    ),
                                    
                                    # Search Help & Repo List Buttons
                                    html.Div(
                                        className="hidden sm:flex items-center space-x-2",
                                        children=[
                                            dbc.Button(
                                                "Help",
                                                id="search-help",
                                                n_clicks=0,
                                                size="sm",
                                                className="bg-slate-700/50 border-slate-600/30 text-slate-300 hover:bg-slate-600/50 hover:text-white transition-all duration-300",
                                            ),
                                            dbc.Button(
                                                "Repo List",
                                                id="repo-list-button",
                                                n_clicks=0,
                                                size="sm",
                                                className="bg-slate-700/50 border-slate-600/30 text-slate-300 hover:bg-slate-600/50 hover:text-white transition-all duration-300",
                                            ),
                                        ],
                                    ),
                                    
                                    # Hamburger Menu Button (Always Visible)
                                    html.Button(
                                        [
                                            html.Div(
                                                className="w-5 h-0.5 bg-slate-200 rounded transition-all duration-300"
                                            ),
                                            html.Div(
                                                className="w-5 h-0.5 bg-slate-200 rounded mt-1 transition-all duration-300"
                                            ),
                                            html.Div(
                                                className="w-5 h-0.5 bg-slate-200 rounded mt-1 transition-all duration-300"
                                            ),
                                        ],
                                        id="mobile-menu-button",
                                        n_clicks=0,
                                        className="flex flex-col items-center justify-center w-9 h-9 rounded-lg hover:bg-slate-800/50 transition-all duration-300 bg-transparent border-none cursor-pointer",
                                    ),
                                    
                                    # Login Section
                                    html.Div(
                                        className="flex items-center",
                                        children=[
                                            login_navbar[0],
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    
                    # Navigation Menu Panel (Always Hamburger Style)
                    html.Div(
                        id="mobile-menu-panel",
                        className="mt-4 pt-4 border-t border-slate-700/30 hidden",
                        children=[
                            html.Div(
                                className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3",
                                children=[
                                    # Navigation Links in Grid Layout
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("🏠", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Welcome", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("💬", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Chat", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/chat",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("📊", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Overview", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/repo_overview",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("📈", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Contributions", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/contributions",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("👥", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Contributors", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/contributors/behavior",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("🔧", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Types", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/contributors/contribution_types",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("🏢", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Affiliation", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/affiliation",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("📋", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("CHAOSS", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/chaoss",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("💻", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Codebase", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/codebase",
                                        className="no-underline",
                                    ),
                                    dcc.Link(
                                        [
                                            html.Div(
                                                className="flex flex-col items-center p-3 rounded-xl hover:bg-slate-800/50 transition-all duration-300 group",
                                                children=[
                                                    html.Div("ℹ️", className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300"),
                                                    html.Div("Info", className="text-sm font-semibold text-slate-200 group-hover:text-white", style={"fontFamily": "'Inter', sans-serif"}),
                                                ],
                                            ),
                                        ],
                                        href="/info",
                                        className="no-underline",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
    
    # Store for mobile menu state
    dcc.Store(id="mobile-menu-state", data=False),
    # Storage quota warning for search
    html.Script(
        """
        window.addEventListener('error', function(event) {
            if (event.message && event.message.toLowerCase().includes('quota') &&
                event.message.toLowerCase().includes('exceeded')) {
                var warningEl = document.getElementById('storage-quota-warning');
                if (warningEl) {
                    warningEl.style.display = 'block';
                }
            }
        });
        """
    ),
])

navbar_bottom = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                "Visualization request",
                href="https://github.com/oss-aspen/8Knot/issues/new?assignees=&labels=enhancement%2Cvisualization&template=visualizations.md",
                external_link="True",
                target="_blank",
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Bug",
                href="https://github.com/oss-aspen/8Knot/issues/new?assignees=&labels=bug&template=bug_report.md",
                external_link="True",
                target="_blank",
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Repo/Org Request",
                href="https://github.com/oss-aspen/8Knot/issues/new?assignees=&labels=augur&template=augur_load.md",
                external_link="True",
                target="_blank",
            )
        ),
    ],
    brand="",
    brand_href="#",
    color="primary",
    dark=True,
    fluid=True,
)

layout = dbc.Container(
    [
        # Storage components for data and caching
        dcc.Store(id="repo-choices", storage_type="session", data=[]),
        dcc.Store(id="job-ids", storage_type="session", data=[]),
        dcc.Store(id="user-group-loading-signal", data="", storage_type="memory"),
        dcc.Store(id="cached-options", storage_type="session"),
        dcc.Store(id="cache-init-trigger", storage_type="memory"),
        dcc.Store(id="search-cache-init-hidden", storage_type="session"),
        dcc.Location(id="url"),
        
        # Storage quota warning
        html.Div(
            dbc.Alert(
                [
                    html.I(className="quota-warning-icon"),
                    "Browser storage limit reached. Search will use a reduced cache which may slightly impact performance. All features will still work normally.",
                ],
                id="storage-quota-warning",
                color="warning",
                dismissable=True,
                style={"display": "none"},
                className="mt-2 mb-0 fixed top-20 right-4 z-40 max-w-md",
            ),
        ),
        
        # Fixed navbar with integrated search
        navbar,
        
        # Add login banner overlay
        login_banner if login_banner else html.Div(),
        
        # Main content area with top padding for fixed navbar
        html.Div(
            className="pt-20",  # Add padding to account for fixed navbar
            children=[
                dcc.Loading(
                    children=[html.Div(id="results-output-container", className="mb-4")],
                    color="#119DFF",
                    type="dot",
                    fullscreen=True,
                ),
                dcc.Loading(
                    dbc.Badge(
                        children="Data Loaded",
                        id="data-badge",
                        color="#436755",
                        className="me-1 mb-4",
                        style={"marginBottom": ".5%"},
                        text_color="dark",
                    ),
                    type="cube",
                    color="#436755",
                ),
                # where our page will be rendered
                dash.page_container,
            ],
        ),
        
        navbar_bottom,
    ],
    fluid=True,
    className="dbc",
)
