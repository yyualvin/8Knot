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

# navbar for top of screen - modern sleek design with responsive sizing and mobile menu
navbar = html.Div([
    google_fonts_link,
    html.Div(
        className="fixed top-0 left-0 right-0 z-50 p-2 sm:p-3 lg:p-4",
        children=[
            html.Nav(
                className="bg-slate-900/80 backdrop-blur-xl border border-slate-700/30 rounded-xl lg:rounded-2xl shadow-2xl mx-auto max-w-full lg:max-w-7xl",
                children=[
                    html.Div(
                        className="px-3 sm:px-4 lg:px-6 py-2 sm:py-2.5 lg:py-3",
                        children=[
                            html.Div(
                                className="flex items-center justify-between",
                                children=[
                                    # Logo and Brand Section with Diamond (properly sized)
                                    html.Div(
                                        className="flex items-center space-x-2 sm:space-x-3 group flex-shrink-0",
                                        children=[
                                            html.Div(
                                                className="relative",
                                                children=[
                                                    html.Div(
                                                        className="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 transform rotate-45 rounded-md shadow-lg group-hover:shadow-blue-500/50 transition-all duration-300 group-hover:scale-110 group-hover:rotate-[225deg]",
                                                    ),
                                                    html.Div(
                                                        className="absolute inset-0 w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 bg-gradient-to-tl from-cyan-400 via-blue-500 to-purple-600 transform rotate-45 rounded-md opacity-70 group-hover:opacity-90 transition-all duration-300 animate-pulse",
                                                    ),
                                                ],
                                            ),
                                            html.A(
                                                "8Knot",
                                                id="navbar-title",
                                                className="text-lg sm:text-xl lg:text-2xl font-black bg-gradient-to-r from-blue-300 via-purple-300 to-pink-300 bg-clip-text text-transparent no-underline hover:from-blue-200 hover:via-purple-200 hover:to-pink-200 transition-all duration-300 tracking-tight",
                                                href="/",
                                                style={"fontFamily": "'Playfair Display', Georgia, serif"},
                                            ),
                                        ],
                                    ),
                                    
                                    # Desktop Navigation Links Section
                                    html.Div(
                                        className="hidden md:flex items-center space-x-0.5 lg:space-x-1 xl:space-x-2 flex-wrap",
                                        children=[
                                            dcc.Link(
                                                "Welcome", 
                                                href="/", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Chat", 
                                                href="/chat", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Overview", 
                                                href="/repo_overview", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Contributions", 
                                                href="/contributions", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                            
                                            # Advanced Dropdown Menu - Responsive
                                            html.Div(
                                                className="relative",
                                                children=[
                                                    html.Button(
                                                        [
                                                            "Contributors",
                                                            html.Span(
                                                                "▼",
                                                                className="ml-1 lg:ml-2 text-xs transition-transform duration-300 inline-block",
                                                                id="contributors-arrow"
                                                            ),
                                                        ],
                                                        id="contributors-dropdown-button",
                                                        n_clicks=0,
                                                        className="flex items-center px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 bg-transparent border-none cursor-pointer tracking-wide whitespace-nowrap",
                                                        style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                                    ),
                                                    html.Div(
                                                        id="contributors-dropdown-panel",
                                                        className="absolute left-0 mt-2 lg:mt-3 w-64 lg:w-72 bg-slate-900/95 backdrop-blur-xl rounded-xl lg:rounded-2xl shadow-2xl border border-slate-700/40 hidden z-50",
                                                        children=[
                                                            html.Div(
                                                                className="p-2 lg:p-3",
                                                                children=[
                                                                    dcc.Link(
                                                                        [
                                                                            html.Div(
                                                                                className="flex items-center p-3 lg:p-4 rounded-lg xl:rounded-xl hover:bg-slate-800/60 transition-all duration-300 group/item",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="w-8 h-8 lg:w-10 lg:h-10 rounded-lg xl:rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mr-3 lg:mr-4 group-hover/item:scale-110 transition-transform duration-300 shadow-lg",
                                                                                        children=[
                                                                                            html.Span("📊", className="text-sm lg:text-lg"),
                                                                                        ],
                                                                                    ),
                                                                                    html.Div(
                                                                                        children=[
                                                                                            html.Div("Behavior", className="text-white font-bold text-sm lg:text-base mb-1", style={"fontFamily": "'Inter', sans-serif"}),
                                                                                            html.Div("Analyze contributor patterns", className="text-slate-300 text-xs lg:text-sm font-medium", style={"fontFamily": "'Inter', sans-serif"}),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                        href="/contributors/behavior", 
                                                                        className="block no-underline"
                                                                    ),
                                                                    dcc.Link(
                                                                        [
                                                                            html.Div(
                                                                                className="flex items-center p-3 lg:p-4 rounded-lg xl:rounded-xl hover:bg-slate-800/60 transition-all duration-300 group/item",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="w-8 h-8 lg:w-10 lg:h-10 rounded-lg xl:rounded-xl bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center mr-3 lg:mr-4 group-hover/item:scale-110 transition-transform duration-300 shadow-lg",
                                                                                        children=[
                                                                                            html.Span("🔧", className="text-sm lg:text-lg"),
                                                                                        ],
                                                                                    ),
                                                                                    html.Div(
                                                                                        children=[
                                                                                            html.Div("Contribution Types", className="text-white font-bold text-sm lg:text-base mb-1", style={"fontFamily": "'Inter', sans-serif"}),
                                                                                            html.Div("Explore contribution categories", className="text-slate-300 text-xs lg:text-sm font-medium", style={"fontFamily": "'Inter', sans-serif"}),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                        href="/contributors/contribution_types", 
                                                                        className="block no-underline"
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            
                                            dcc.Link(
                                                "Affiliation", 
                                                href="/affiliation", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "CHAOSS", 
                                                href="/chaoss", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Codebase", 
                                                href="/codebase", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Info", 
                                                href="/info", 
                                                className="relative px-2 lg:px-3 xl:px-4 py-1.5 lg:py-2 text-xs sm:text-sm lg:text-sm font-semibold text-slate-200 hover:text-white no-underline rounded-lg xl:rounded-xl hover:bg-slate-800/50 transition-all duration-300 before:absolute before:inset-0 before:rounded-lg xl:before:rounded-xl before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/20 hover:before:to-purple-500/20 before:transition-all before:duration-300 tracking-wide whitespace-nowrap",
                                                style={"fontFamily": "'Inter', 'SF Pro Display', sans-serif"},
                                            ),
                                        ],
                                    ),
                                    
                                    # Mobile Menu Button & Login Section
                                    html.Div(
                                        className="flex items-center space-x-2 flex-shrink-0",
                                        children=[
                                            # Mobile Menu Button
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
                                                className="md:hidden flex flex-col items-center justify-center w-8 h-8 rounded-lg hover:bg-slate-800/50 transition-all duration-300 bg-transparent border-none cursor-pointer",
                                            ),
                                            # Login Section
                                            html.Div(
                                                className="flex items-center",
                                                children=[
                                                    # packaged as a list to make linter happy-
                                                    # it keeps making the login_navpar page-wrap as a tuple,
                                                    # so I wrapped it in a list.
                                                    login_navbar[0],
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            
                            # Mobile Menu Panel
                            html.Div(
                                id="mobile-menu-panel",
                                className="md:hidden mt-4 pt-4 border-t border-slate-700/30 hidden",
                                children=[
                                    html.Div(
                                        className="flex flex-col space-y-1",
                                        children=[
                                            dcc.Link(
                                                "Welcome", 
                                                href="/", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Chat", 
                                                href="/chat", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Repo Overview", 
                                                href="/repo_overview", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Contributions", 
                                                href="/contributions", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                            # Contributors submenu for mobile
                                            html.Div(
                                                className="pl-4",
                                                children=[
                                                    html.Div("Contributors:", className="px-4 py-2 text-xs font-medium text-slate-400 uppercase tracking-wider"),
                                                    dcc.Link(
                                                        "Behavior", 
                                                        href="/contributors/behavior", 
                                                        className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline block",
                                                        style={"fontFamily": "'Inter', sans-serif"},
                                                    ),
                                                    dcc.Link(
                                                        "Contribution Types", 
                                                        href="/contributors/contribution_types", 
                                                        className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline block",
                                                        style={"fontFamily": "'Inter', sans-serif"},
                                                    ),
                                                ],
                                            ),
                                            dcc.Link(
                                                "Affiliation", 
                                                href="/affiliation", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "CHAOSS", 
                                                href="/chaoss", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Codebase", 
                                                href="/codebase", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                            dcc.Link(
                                                "Info", 
                                                href="/info", 
                                                className="px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-300 no-underline",
                                                style={"fontFamily": "'Inter', sans-serif"},
                                            ),
                                        ],
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
    # Store for contributors dropdown state
    dcc.Store(id="contributors-dropdown-state", data=False),
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

search_bar = html.Div(
    [
        # Add client-side caching component
        dcc.Store(id="cached-options", storage_type="session"),
        # Hidden div to trigger cache initialization on page load
        html.Div(id="cache-init-trigger", style={"display": "none"}),
        # Storage quota warning
        dcc.Store(id="search-cache-init-hidden", storage_type="session"),
        # Warning alert for when browser storage quota is exceeded
        html.Div(
            dbc.Alert(
                [
                    html.I(className="quota-warning-icon"),  # Warning icon
                    "Browser storage limit reached. Search will use a reduced cache which may slightly impact performance. All features will still work normally.",
                ],
                id="storage-quota-warning",  # ID used by Javascript to show/hide this alert
                color="warning",
                dismissable=True,
                style={"display": "none"},  # Initially hidden, controlled by JavaScript
                className="mt-2 mb-0",
            ),
            className="search-bar-component",
        ),
        dbc.Stack(
            [
                html.Div(
                    [
                        dmc.MultiSelect(
                            id="projects",
                            searchable=True,
                            clearable=True,
                            nothingFound="No matching repos/orgs.",
                            variant="filled",
                            debounce=100,  # debounce time for the search input, since we're implementing client-side caching, we can use a faster debounce
                            data=[augur.initial_multiselect_option()],
                            value=[augur.initial_multiselect_option()["value"]],
                            style={"fontSize": 16},
                            maxDropdownHeight=300,  # limits the dropdown menu's height to 300px
                            zIndex=9999,  # ensures the dropdown menu is on top of other elements
                            dropdownPosition="bottom",  # forces the dropdown to open downwards
                            transitionDuration=150,  # transition duration for the dropdown menu
                            className="searchbar-dropdown",
                        ),
                        # Add search status indicator
                        html.Div(id="search-status", className="search-status-indicator", style={"display": "none"}),
                        dbc.Alert(
                            children='Please ensure that your spelling is correct. \
                                If your selection definitely isn\'t present, please request that \
                                it be loaded using the help button "REPO/ORG Request" \
                                in the bottom right corner of the screen.',
                            id="help-alert",
                            dismissable=True,
                            fade=True,
                            is_open=False,
                            color="info",
                        ),
                        dbc.Alert(
                            children="List of repos",
                            id="repo-list-alert",
                            dismissable=True,
                            fade=True,
                            is_open=False,
                            color="light",
                            # if number of repos is large, render as a scrolling window
                            style={"overflow-y": "scroll", "max-height": "440px"},
                        ),
                    ],
                    style={
                        "width": "50%",
                        "paddingRight": "10px",
                    },
                ),
                dbc.Button(
                    "Search",
                    id="search",
                    n_clicks=0,
                    size="md",
                ),
                dbc.Button(
                    "Help",
                    id="search-help",
                    n_clicks=0,
                    size="md",
                ),
                dbc.Button(
                    "Repo List",
                    id="repo-list-button",
                    n_clicks=0,
                    size="md",
                ),
                dbc.Switch(
                    id="bot-switch",
                    label="GitHub Bot Filter",
                    value=True,
                    input_class_name="botlist-filter-switch",
                    style={"fontSize": 18},
                ),
            ],
            direction="horizontal",
            style={
                "width": "70%",
            },
        ),
    ]
)

layout = dbc.Container(
    [
        # componets to store data from queries
        dcc.Store(id="repo-choices", storage_type="session", data=[]),
        # components to store job-ids for the worker queue
        dcc.Store(id="job-ids", storage_type="session", data=[]),
        dcc.Store(id="user-group-loading-signal", data="", storage_type="memory"),
        dcc.Location(id="url"),
        # Add client-side script to handle storage quota issues
        # This script does two things:
        # 1. Listens for global JavaScript errors related to storage quota being exceeded.
        #    If such an error occurs, finds the element with id 'storage-quota-warning'
        #    and makes it visible to alert the user.
        # 2. Tests if sessionStorage can store a 512KB string.
        #    If the test fails (due to quota limits), it displays the warning.
        # The user will see the warning if the browser's session storage is full
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

            // Test storage capacity
            try {
                var testKey = 'storage_test';
                var testString = new Array(512 * 1024).join('a');  // 512KB
                sessionStorage.setItem(testKey, testString);
                sessionStorage.removeItem(testKey);
            } catch (e) {
                if (e.name === 'QuotaExceededError' ||
                    (e.message &&
                    (e.message.toLowerCase().includes('quota') ||
                     e.message.toLowerCase().includes('exceeded')))) {
                    var warningEl = document.getElementById('storage-quota-warning');
                    if (warningEl) {
                        warningEl.style.display = 'block';
                    }
                }
            }
        """
        ),
        navbar,
        # Add login banner overlay (will be positioned via CSS)
        login_banner if login_banner else html.Div(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label(
                            "Select GitHub repos or orgs:",
                            html_for="projects",
                            width="auto",
                            size="lg",
                        ),
                        search_bar,
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
                                className="me-1",
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
            ],
            justify="start",
        ),
        navbar_bottom,
    ],
    fluid=True,
    className="dbc",
)
