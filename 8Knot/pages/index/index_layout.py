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

# navbar for top of screen - modern sleek design
navbar = html.Nav(
    className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 backdrop-blur-md bg-opacity-95 text-white sticky top-0 z-50 shadow-2xl border-b border-slate-700/50",
    children=[
        html.Div(
            className="container mx-auto px-6 py-3",
            children=[
                html.Div(
                    className="flex items-center justify-between",
                    children=[
                        # Logo and Brand Section
                        html.Div(
                            className="flex items-center space-x-3 group",
                            children=[
                                html.Div(
                                    className="relative p-2 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg group-hover:shadow-blue-500/25 transition-all duration-300 group-hover:scale-105",
                                    children=[
                                        html.Img(
                                            src=dash.get_asset_url("8knot-logo-vertical.png"),
                                            className="h-8 w-8 filter brightness-0 invert",
                                        ),
                                    ],
                                ),
                                html.A(
                                    "8Knot",
                                    id="navbar-title",
                                    className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent no-underline hover:from-blue-300 hover:to-purple-300 transition-all duration-300",
                                    href="/",
                                ),
                            ],
                        ),
                        
                        # Navigation Links Section
                        html.Div(
                            className="hidden lg:flex items-center space-x-1",
                            children=[
                                dcc.Link(
                                    "Welcome", 
                                    href="/", 
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                                dcc.Link(
                                    "Chat", 
                                    href="/chat", 
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                                dcc.Link(
                                    "Repo Overview", 
                                    href="/repo_overview", 
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                                dcc.Link(
                                    "Contributions", 
                                    href="/contributions", 
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                                
                                # Advanced Dropdown Menu
                                html.Div(
                                    className="relative group",
                                    children=[
                                        html.Button(
                                            [
                                                "Contributors",
                                                html.Span(
                                                    "▼",
                                                    className="ml-2 text-xs transition-transform duration-200 group-hover:rotate-180 inline-block",
                                                ),
                                            ],
                                            className="flex items-center px-4 py-2 text-sm font-medium text-slate-300 hover:text-white rounded-lg hover:bg-slate-800/50 transition-all duration-200 bg-transparent border-none cursor-pointer",
                                        ),
                                        html.Div(
                                            className="absolute left-0 mt-2 w-64 bg-slate-800/95 backdrop-blur-md rounded-xl shadow-2xl border border-slate-700/50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform group-hover:translate-y-0 translate-y-2 z-50",
                                            children=[
                                                html.Div(
                                                    className="p-2",
                                                    children=[
                                                        dcc.Link(
                                                            [
                                                                html.Div(
                                                                    className="flex items-center p-3 rounded-lg hover:bg-slate-700/50 transition-all duration-200 group/item",
                                                                    children=[
                                                                        html.Div(
                                                                            className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center mr-3 group-hover/item:scale-110 transition-transform duration-200",
                                                                            children=[
                                                                                html.Span("📊", className="text-sm"),
                                                                            ],
                                                                        ),
                                                                        html.Div(
                                                                            children=[
                                                                                html.Div("Behavior", className="text-white font-medium text-sm"),
                                                                                html.Div("Analyze contributor patterns", className="text-slate-400 text-xs"),
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
                                                                    className="flex items-center p-3 rounded-lg hover:bg-slate-700/50 transition-all duration-200 group/item",
                                                                    children=[
                                                                        html.Div(
                                                                            className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mr-3 group-hover/item:scale-110 transition-transform duration-200",
                                                                            children=[
                                                                                html.Span("🔧", className="text-sm"),
                                                                            ],
                                                                        ),
                                                                        html.Div(
                                                                            children=[
                                                                                html.Div("Contribution Types", className="text-white font-medium text-sm"),
                                                                                html.Div("Explore different contributions", className="text-slate-400 text-xs"),
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
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                                dcc.Link(
                                    "CHAOSS", 
                                    href="/chaoss", 
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                                dcc.Link(
                                    "Codebase", 
                                    href="/codebase", 
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                                dcc.Link(
                                    "Info", 
                                    href="/info", 
                                    className="relative px-4 py-2 text-sm font-medium text-slate-300 hover:text-white no-underline rounded-lg hover:bg-slate-800/50 transition-all duration-200 before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-blue-500/0 before:to-purple-500/0 hover:before:from-blue-500/10 hover:before:to-purple-500/10 before:transition-all before:duration-200"
                                ),
                            ],
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
    ],
)

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
