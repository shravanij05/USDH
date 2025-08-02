from dash import html, dcc, dash_table, callback_context, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
from dash.exceptions import PreventUpdate

def manage_resources_layout():
    # Connect to the database
    conn = sqlite3.connect('data/USDH.db')
    # Get resources data
    resources_df = pd.read_sql_query("SELECT * FROM ebooks", conn)
    conn.close()
    
    return html.Div([
        # Background Elements
        html.Div([
            # Pattern Overlay
            html.Div(className="resource-pattern-overlay"),
            
            # Animated Particles
            html.Div([
                html.I(className="fas fa-book resource-particle"),
                html.I(className="fas fa-graduation-cap resource-particle"),
                html.I(className="fas fa-laptop resource-particle"),
                html.I(className="fas fa-pencil-alt resource-particle"),
                html.I(className="fas fa-globe resource-particle"),
            ], className="resource-particles"),
            
            # Glowing Orbs
            html.Div([
                html.Div(className="resource-orb"),
                html.Div(className="resource-orb"),
                html.Div(className="resource-orb"),
            ], className="resource-orbs"),
        ], className="resource-bg"),

        # Main Content Container
        html.Div([
            # Header Section with Animation
            html.Div([
                html.Div([
                    html.I(className="fas fa-arrow-left me-2 back-icon"),
                    html.Button("Back to Dashboard", id="back-to-dashboard", className="resource-button back-button", n_clicks=0)
                ], className="back-container animate-fade-in"),
                
                html.H2([
                    html.I(className="fas fa-books me-3"),
                    "E-Resources Management"
                ], className="page-title animate-slide-down"),
                
                html.P("Manage and organize your digital educational resources", className="page-subtitle animate-fade-in")
            ], className="header-section"),
            
            # Resource Management Section
            html.Div([
                # Header with Stats
                html.Div([
                    html.Div([
                        html.H4("Digital Library Resources", className="section-title", style={
                            'color': '#0d1b4a',  # Dark blue color
                            'textShadow': '1px 1px 2px rgba(13, 27, 74, 0.1)',
                            'fontWeight': '700'
                        }),
                        html.P(f"Total Resources: {len(resources_df)}", className="resource-count")
                    ], className="section-header"),
                    
                    dbc.Button([
                        html.I(className="fas fa-plus me-2"),
                        "Add New Resource"
                    ], id="add-resource-btn", className="resource-button add-button", n_clicks=0)
                ], className="management-header animate-slide-up"),
                
                # Filters with Animation
                html.Div([
                    html.Div([
                        html.Label("Filter by State", className="filter-label"),
                        dbc.Select(
                            id="resource-state-filter",
                            options=[
                                {"label": "All States", "value": "all"}
                            ] + [
                                {"label": str(state), "value": str(state)} 
                                for state in resources_df['states'].dropna().unique().tolist()
                            ],
                            value="all",
                            className="resource-select"
                        )
                    ], className="filter-group animate-slide-right"),
                    
                    html.Div([
                        html.Label("Filter by Preference", className="filter-label"),
                        dbc.Select(
                            id="resource-preference-filter",
                            options=[
                                {"label": "All Preferences", "value": "all"},
                                {"label": "School", "value": "School"},
                                {"label": "College", "value": "College"}
                            ],
                            value="all",
                            className="resource-select"
                        )
                    ], className="filter-group animate-slide-right")
                ], className="filters-container"),
                
                # Resources Table with Animation
                html.Div([
                    dash_table.DataTable(
                        id='resources-table',
                        columns=[
                            {"name": "Website", "id": "website"},
                            {"name": "Preference", "id": "preference"},
                            {"name": "Subject", "id": "subject"},
                            {"name": "State", "id": "states"},
                            {"name": "Link", "id": "link", "presentation": "markdown"}
                        ],
                        data=resources_df.to_dict('records'),
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                        style_header={
                            'backgroundColor': '#1a237e',
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left',
                            'padding': '16px',
                            'fontSize': '14px',
                        },
                        style_cell={
                            'backgroundColor': 'white',
                            'color': '#333',
                            'border': '1px solid #e0e0e0',
                            'padding': '16px',
                            'textAlign': 'left',
                            'fontFamily': '"Nunito", sans-serif',
                            'fontSize': '14px',
                            'transition': 'all 0.3s ease'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f8f9fe'
                            },
                            {
                                'if': {'state': 'selected'},
                                'backgroundColor': '#e3f2fd',
                                'border': '2px solid #1a237e'
                            }
                        ],
                        markdown_options={"html": True},
                        row_selectable="single",
                        filter_action="native",
                        sort_action="native",
                    )
                ], className="table-container animate-fade-in"),
                
                # Action Buttons with Animation
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-edit me-2"),
                        "Edit"
                    ], id="edit-resource-btn", className="resource-button edit-button", n_clicks=0),
                    
                    dbc.Button([
                        html.I(className="fas fa-trash-alt me-2"),
                        "Delete"
                    ], id="delete-resource-btn", className="resource-button delete-button", n_clicks=0),
                    
                    dbc.Button([
                        html.I(className="fas fa-eye me-2"),
                        "View Details"
                    ], id="view-resource-btn", className="resource-button view-button", n_clicks=0),
                ], className="action-buttons animate-slide-up")
            ], className="resource-section"),
            
            # Enhanced Modals
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle([
                    html.I(className="fas fa-plus-circle me-2"),
                    "Resource Details"
                ], className="modal-title")),
                dbc.ModalBody([
                    html.Div([
                        html.Label("Website Name", className="modal-label"),
                        dbc.Input(id="resource-website-input", className="resource-input")
                    ], className="modal-input-group"),
                    
                    html.Div([
                        html.Label("Preference", className="modal-label"),
                        dbc.Select(
                            id="resource-preference-input",
                            options=[
                                {"label": "School", "value": "School"},
                                {"label": "College", "value": "College"}
                            ],
                            className="resource-select"
                        )
                    ], className="modal-input-group"),
                    
                    html.Div([
                        html.Label("Subject", className="modal-label"),
                        dbc.Input(id="resource-subject-input", className="resource-input")
                    ], className="modal-input-group"),
                    
                    html.Div([
                        html.Label("State", className="modal-label"),
                        dbc.Input(id="resource-state-input", className="resource-input")
                    ], className="modal-input-group"),
                    
                    html.Div([
                        html.Label("Resource Link", className="modal-label"),
                        dbc.Input(id="resource-link-input", className="resource-input")
                    ], className="modal-input-group"),
                ]),
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-save me-2"),
                        "Save"
                    ], id="save-resource-btn", className="resource-button save-button"),
                    
                    dbc.Button([
                        html.I(className="fas fa-times me-2"),
                        "Cancel"
                    ], id="cancel-resource-btn", className="resource-button cancel-button")
                ])
            ], id="resource-modal", className="resource-modal", size="lg", is_open=False),
            
            # Resource Details Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="resource-detail-title", className="modal-title")),
                dbc.ModalBody(id="resource-detail-body", className="resource-detail-body"),
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-times me-2"),
                        "Close"
                    ], id="close-resource-detail-btn", className="resource-button close-button")
                ])
            ], id="resource-detail-modal", className="resource-modal", size="lg", is_open=False),
            
            # Notification Area
            html.Div(id="resource-notification", className="notification-area"),
            
            # Data Store
            dcc.Store(id="filtered-resources", data=resources_df.to_dict('records'))
        ], className="content-container")
    ], className="resource-management-container")

# Add callback for Back to Dashboard button
@callback(
    Output('url', 'pathname'),
    Input('back-to-dashboard', 'n_clicks'),
    prevent_initial_call=True
)
def navigate_to_dashboard(n_clicks):
    if n_clicks:
        return '/user-dashboard'
    raise PreventUpdate