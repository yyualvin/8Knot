from dash import html, dcc
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from app import augur
import os
import logging


def create_nav_link(icon_src, text, href):
    """Create a navigation link with icon and text"""
    return dbc.NavLink(
        [
            html.Img(
                src=icon_src,
                alt=text,
                style={
                    "width": "24px",
                    "height": "24px",
                    "marginRight": "12px"
                }
            ),
            html.Span(text, style={"color": "#9c9c9c", "fontSize": "16px", "fontWeight": "400"})
        ],
        href=href,
        style={
            "display": "flex",
            "alignItems": "center",
            "padding": "12px 16px",
            "borderRadius": "8px",
            "marginBottom": "8px",
            "textDecoration": "none"
        }
    )

def create_dropdown_nav_link(text, href):
    """Create a dropdown navigation link with just text"""
    return dbc.NavLink(
        text,
        href=href,
        style={
            "color": "#9c9c9c",
            "fontSize": "14px",
            "padding": "8px 16px 8px 32px",
            "marginBottom": "4px",
            "textDecoration": "none",
            "display": "block"
        }
    )

def create_dropdown_nav(icon_src, text, dropdown_links):
    """Create a dropdown navigation with main item and dropdown content"""
    return html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src=icon_src,
                        alt=text,
                        style={
                            "width": "24px",
                            "height": "24px",
                            "marginRight": "12px"
                        }
                    ),
                    html.Span(text, style={"color": "#9c9c9c", "fontSize": "16px", "fontWeight": "400"}),
                    html.I(className="fas fa-chevron-down", style={"color": "#9c9c9c", "fontSize": "12px", "marginLeft": "auto"})
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "12px 16px",
                    "borderRadius": "8px",
                    "cursor": "pointer"
                },
                id="contributors-dropdown-toggle"
            ),
            html.Div(
                dropdown_links,
                id="contributors-dropdown",
                style={
                    "display": "none",
                    "padding": "8px 0",
                    "borderRadius": "0 0 8px 8px"
                }
            )
        ],
        id="contributors-dropdown-container",
        style={
            "borderRadius": "8px",
            "marginBottom": "8px"
        }
    )


# Top bar with logos
topbar = html.Div(
    [
        html.Img(
            src="/assets/8Knot.svg",
            alt="8Knot Logo",
            style={
                "width": "70px",
                "height": "22px",
                "margin": "20px 20px",
                "display": "inline-block",
                "verticalAlign": "middle"
            }
        ),
        html.Img(
            src="/assets/CHAOSS.svg",
            alt="CHAOSS Logo",
            style={
                "width": "70px",
                "height": "22px",
                "margin": "10px -20px",
                "display": "inline-block",
                "verticalAlign": "middle"
            }
        ),
    ],
    id="rectangular-bar",
    style={
        "height": "60px",
        "width": "100%",
        "background-color": "#242424",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "flex-start",
        "paddingLeft": "10px",
    }
)

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
        # Search input section
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
                    style={"fontSize": 16, "zIndex": 9999},  # Updated: moved zIndex to style
                    maxDropdownHeight=300,  # limits the dropdown menu's height to 300px
                    # Removed: dropdownPosition and transitionDuration no longer supported in v2.1.0
                    className="searchbar-dropdown",
                    radius="md",  # Adds more rounded corners
                    styles={
                        "input": {
                            "fontSize": "16px",
                            "height": "48px",  # Set exact height to 48px
                            "padding": "0 16px",  # Remove vertical padding since we're setting exact height
                            "borderRadius": "20px",
                            "display": "flex",
                            "alignItems": "center",
                            "backgroundColor": "#1D1D1D",
                            "borderColor": "#404040",
                        },
                        "dropdown": {
                            "borderRadius": "12px",
                            "backgroundColor": "#1D1D1D",
                            "border": "1px solid #444",
                        },
                        "item": {
                            "borderRadius": "8px",
                            "margin": "2px 4px",
                            "color": "white",
                        },

                    },
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
                "width": "100%",
                "marginBottom": "1rem",
            },
        ),
        # Buttons section below search bar
        dbc.Stack(
            [
                dbc.Button(
                    html.I(className="fas fa-search"),
                    id="search",
                    n_clicks=0,
                    size="sm",
                    color="outline-secondary",
                    title="Search",
                    style={
                        "backgroundColor": "transparent",
                        "border": "none",
                        "padding": "4px 8px",
                        "fontSize": "14px"
                    }
                ),
                dbc.Button(
                    html.I(className="fas fa-question-circle"),
                    id="search-help",
                    n_clicks=0,
                    size="sm",
                    color="outline-secondary",
                    title="Help",
                    style={
                        "backgroundColor": "transparent",
                        "border": "none",
                        "padding": "4px 8px",
                        "fontSize": "14px"
                    }
                ),
                dbc.Button(
                    html.I(className="fas fa-list"),
                    id="repo-list-button",
                    n_clicks=0,
                    size="sm",
                    color="outline-secondary",
                    title="Repo List",
                    style={
                        "backgroundColor": "transparent",
                        "border": "none",
                        "padding": "4px 8px",
                        "fontSize": "14px"
                    }
                ),
                dbc.Switch(
                    id="bot-switch",
                    label="GitHub Bot Filter",
                    value=True,
                    input_class_name="botlist-filter-switch",
                    style={"fontSize": 12, "marginTop": "8px", "marginLeft": "10px"},
                ),
            ],
            direction="horizontal",
            style={
                "width": "100%",
                "justifyContent": "center",
            },
        ),
    ]
)

# We need to wrap the container in a div to allow for custom styling
layout = html.Div(
    dbc.Container(
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
        # navbar,
        # Add login banner overlay (will be positioned via CSS)
        login_banner if login_banner else html.Div(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        topbar,
                        # where our page will be rendered
                        # We are wrapping this in a div to allow for custom styling
                        html.Div(
                            [
                                # Left sidebar
                                html.Div(
                                    [
                                        search_bar,
                                        # Navigation menu
                                        html.Div(
                                            [
                                                                                                 create_nav_link("/assets/repo_overview.svg", "Repo Overview", "/repo_overview"),
                                                create_nav_link("/assets/contributions.svg", "Contributions", "/contributions"),
                                                create_dropdown_nav(
                                                    "/assets/contributors.svg",
                                                    "Contributors",
                                                    [
                                                                                                                 create_dropdown_nav_link("Behavior", "/contributors/behavior"),
                                                         create_dropdown_nav_link("Contribution Types", "/contributors/contribution_types")
                                                    ]
                                                ),
                                                create_nav_link("/assets/affiliation.svg", "Affiliation", "/affiliation"),
                                                create_nav_link("/assets/chaoss.svg", "CHAOSS", "/chaoss"),
                                            ],
                                            style={
                                                "marginTop": "1rem"
                                            }
                                        ),
                                    ],
                                    id="left-sidebar",
                                    style={
                                        "width": "340px",
                                        "background-color": "#1D1D1D",
                                        "border-radius": "12px 0 0 12px",
                                        "border-right": "1.5px solid #292929",
                                        "padding": "1rem",
                                        "flex-shrink": 0
                                    }
                                ),
                                # Main content area (your existing page-container)
                                html.Div(
                                    [
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
                                        dash.page_container,
                                    ],
                                    id="page-container",
                                    style={
                                        "border-radius": "0 12px 12px 0",
                                        "background-color": "#1D1D1D",
                                        "padding": "1rem",
                                        "overflow-y": "auto",
                                        "min-height": "calc(100vh - 90px)",
                                        "max-height": "calc(100vh - 90px)",
                                        "flex": "1"
                                    }
                                ),
                            ],
                            id="main-layout-container",
                            style={
                                "display": "flex",
                                "min-height": "calc(100vh - 90px)",
                                "max-height": "calc(100vh - 90px)"
                            }
                        ),
                    ],
                ),
            ],
            justify="start",
        ),
        # navbar_bottom,
        ],
        fluid=True,
        className="dbc",
        style={
            "background-color": "#242424",
        }
    ),
    style={
        "background-color": "#242424",
        "min-height": "100vh",
        "margin": "0",
        "padding": "0"
    }
)
