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
    href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Playfair+Display:wght@400;700;900&family=Inter:wght@400;500;600;700&display=swap"
)

# navbar for top of screen - fixed design with integrated search and always-hamburger menu
navbar = html.Div([
    google_fonts_link,
    html.Nav(
        className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-xl border-b border-slate-700/20 shadow-lg",
        children=[
            html.Div(
                className="container mx-auto px-4 py-2",
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
                                                className="w-6 h-6 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 transform rotate-45 rounded-md shadow-lg group-hover:shadow-blue-500/50 transition-all duration-300 group-hover:scale-110 group-hover:rotate-[225deg]",
                                            ),
                                            html.Div(
                                                className="absolute inset-0 w-6 h-6 bg-gradient-to-tl from-cyan-400 via-blue-500 to-purple-600 transform rotate-45 rounded-md opacity-70 group-hover:opacity-90 transition-all duration-300 animate-pulse",
                                            ),
                                        ],
                                    ),
                                    html.A(
                                        "8Knot",
                                        id="navbar-title",
                                        className="text-lg font-black bg-gradient-to-r from-blue-300 via-purple-300 to-pink-300 bg-clip-text text-transparent no-underline hover:from-blue-200 hover:via-purple-200 hover:to-pink-200 transition-all duration-300 tracking-tight",
                                        href="/",
                                        style={"fontFamily": "'Orbitron', 'JetBrains Mono', monospace", "letterSpacing": "0.05em"},
                                    ),
                                    # Navigation Menu Button
                                    html.Button(
                                        "Menu",
                                        id="mobile-menu-button",
                                        n_clicks=0,
                                        className="flex items-center justify-center px-2.5 py-1 rounded-lg hover:bg-slate-800/50 transition-all duration-300 bg-transparent border border-slate-600/30 cursor-pointer text-slate-300 hover:text-white text-xs font-medium",
                                    ),
                                ],
                            ),
                            
                            # Compact Integrated Search Section
                            html.Div(
                                className="flex-1 max-w-4xl mx-3",
                                children=[
                                    html.Div(
                                        className="relative group",
                                        children=[
                                            # Compact Search Bar with Controls - Blended Design
                                            html.Div(
                                                className="flex items-center gap-2 bg-gradient-to-r from-slate-800/70 via-slate-700/80 to-slate-800/70 backdrop-blur-xl rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 group-focus-within:shadow-blue-400/30 px-3 py-1.5 border border-slate-600/20 hover:border-slate-500/30 group-focus-within:border-blue-400/40",
                                                children=[
                                                    # Search Icon
                                                    html.Div(
                                                        className="text-slate-400 group-focus-within:text-blue-400 transition-colors duration-300",
                                                        children=[html.Span("🔍", className="text-sm")],
                                                    ),
                                                    # MultiSelect Component - More Compact
                                                    html.Div(
                                                        className="flex-1 min-w-0",
                                                        children=[
                                                            dmc.MultiSelect(
                                                                id="projects",
                                                                placeholder="Search repositories and organizations...",
                                                                searchable=True,
                                                                clearable=True,
                                                                nothingFound="No matching repos/orgs found.",
                                                                variant="unstyled",
                                                                debounce=100,
                                                                data=[augur.initial_multiselect_option()],
                                                                value=[augur.initial_multiselect_option()["value"]],
                                                                style={"fontSize": 13},
                                                                maxDropdownHeight=350,
                                                                zIndex=9999,
                                                                dropdownPosition="bottom",
                                                                transitionDuration=200,
                                                                className="navbar-search-input",
                                                                styles={
                                                                    "input": {
                                                                        "backgroundColor": "transparent",
                                                                        "border": "none",
                                                                        "color": "#f1f5f9",
                                                                        "fontSize": "13px",
                                                                        "padding": "2px 0",
                                                                        "fontFamily": "'Inter', sans-serif",
                                                                        "minHeight": "auto",
                                                                    },
                                                                    "pill": {
                                                                        "backgroundColor": "rgba(59, 130, 246, 0.2)",
                                                                        "border": "1px solid rgba(139, 92, 246, 0.4)",
                                                                        "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15), rgba(236, 72, 153, 0.1))",
                                                                        "color": "#a5b4fc",
                                                                        "borderRadius": "6px",
                                                                        "fontSize": "11px",
                                                                        "fontWeight": "500",
                                                                        "padding": "2px 8px",
                                                                        "backdropFilter": "blur(8px)",
                                                                        "boxShadow": "0 2px 8px rgba(59, 130, 246, 0.1)",
                                                                    },
                                                                    "dropdown": {
                                                                        "backgroundColor": "#1e293b",
                                                                        "border": "1px solid rgba(59, 130, 246, 0.3)",
                                                                        "borderRadius": "8px",
                                                                        "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                                                                    },
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                    # Bot Filter Toggle - Modern Gradient Style
                                                    html.Div(
                                                        className="hidden md:flex items-center gap-1.5 px-2 py-1 rounded-md",
                                                        style={
                                                            "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1))",
                                                            "border": "1px solid rgba(139, 92, 246, 0.3)",
                                                            "backdropFilter": "blur(8px)",
                                                        },
                                                        children=[
                                                            html.Label(
                                                                "Bot Filter",
                                                                htmlFor="bot-switch",
                                                                className="text-slate-200 text-xs font-medium cursor-pointer",
                                                                style={"fontFamily": "'Inter', sans-serif"},
                                                            ),
                                                            dbc.Switch(
                                                                id="bot-switch",
                                                                value=True,
                                                                className="mb-0",
                                                                input_style={"transform": "scale(0.7)"},
                                                            ),
                                                        ],
                                                    ),
                                                    # Modern Gradient Action Buttons
                                                    html.Div(
                                                        className="flex items-center gap-1",
                                                        children=[
                                                            dbc.Button(
                                                                "Help",
                                                                id="search-help",
                                                                n_clicks=0,
                                                                size="sm",
                                                                className="px-2 py-0.5 text-xs border-0",
                                                                style={
                                                                    "background": "linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7)",
                                                                    "color": "white",
                                                                    "fontFamily": "'Inter', sans-serif",
                                                                    "fontSize": "10px",
                                                                    "fontWeight": "500",
                                                                    "boxShadow": "0 2px 8px rgba(139, 92, 246, 0.3)",
                                                                    "transition": "all 0.3s ease",
                                                                },
                                                            ),
                                                            dbc.Button(
                                                                "List",
                                                                id="repo-list-button",
                                                                n_clicks=0,
                                                                size="sm",
                                                                className="px-2 py-0.5 text-xs border-0",
                                                                style={
                                                                    "background": "linear-gradient(135deg, #10b981, #06b6d4, #3b82f6)",
                                                                    "color": "white",
                                                                    "fontFamily": "'Inter', sans-serif",
                                                                    "fontSize": "10px",
                                                                    "fontWeight": "500",
                                                                    "boxShadow": "0 2px 8px rgba(16, 185, 129, 0.3)",
                                                                    "transition": "all 0.3s ease",
                                                                },
                                                            ),
                                                            dbc.Button(
                                                                "Search",
                                                                id="search",
                                                                n_clicks=0,
                                                                size="sm",
                                                                className="px-2.5 py-0.5 border-0",
                                                                style={
                                                                    "background": "linear-gradient(135deg, #f59e0b, #f97316, #ec4899)",
                                                                    "color": "white",
                                                                    "fontFamily": "'Inter', sans-serif",
                                                                    "fontSize": "11px",
                                                                    "fontWeight": "600",
                                                                    "boxShadow": "0 2px 8px rgba(245, 158, 11, 0.4)",
                                                                    "transition": "all 0.3s ease",
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            # Search Status and Alerts - Positioned Below
                                            html.Div(
                                                className="absolute top-full left-0 right-0 mt-2 space-y-2 z-50",
                                                children=[
                                                    html.Div(id="search-status", className="search-status-indicator", style={"display": "none"}),
                                                    dbc.Alert(
                                                        'Please ensure that your spelling is correct. If your selection definitely isn\'t present, please request that it be loaded using the "REPO/ORG Request" button.',
                                                        id="help-alert",
                                                        color="info",
                                                        dismissable=True,
                                                        is_open=False,
                                                        className="mb-2",
                                                        style={"fontSize": "13px"},
                                                    ),
                                                    dbc.Alert(
                                                        "Repository list will appear here",
                                                        id="repo-list-alert",
                                                        color="secondary",
                                                        dismissable=True,
                                                        is_open=False,
                                                        className="mb-2",
                                                        style={"fontSize": "13px", "maxHeight": "300px", "overflowY": "auto"},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            
                            # Right Side Controls - Login Only
                            html.Div(
                                className="flex items-center space-x-4 flex-shrink-0",
                                children=[
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
            className="pt-16",  # Reduced padding for slimmer navbar
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
