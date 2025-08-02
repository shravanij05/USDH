import dash
from dash import html, dcc, callback_context, no_update, ALL
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
from flask import session
import plotly.graph_objs as go
import plotly.express as px
from dash.exceptions import PreventUpdate
import random
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from datetime import datetime, date
import json
from ebooks_formatter import format_ebooks_table
from courses_formatter import format_courses_table
from school_courses_formatter import format_courses2_table
from themes import get_theme_colors, get_theme_styles

def user_dashboard():
    # New Profile Settings Dropdown with nested options
    profile_settings_dropdown = dbc.DropdownMenu(
        label="Profile Settings",
        children=[
            dbc.DropdownMenuItem("User Profile", id="user-profile-item"),
            dbc.DropdownMenuItem("My Certificate", id="my-certificate-item"),
            dbc.Collapse(
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem("Add Certificate", id="add-certificate-item", action=True),
                        dbc.ListGroupItem("View Certificate", id="view-certificate-item", action=True),
                    ],
                    flush=True,
                ),
                id="my-certificate-collapse",
                is_open=False,
            ),
            dbc.DropdownMenuItem("Logout", href="/logout", id="logout-item"),
        ],
        direction="left",
        id="profile-settings-dropdown",
        className="ms-auto profile-settings-dropdown",  # Added profile-settings-dropdown class
        nav=True,
        in_navbar=True,
    )

    # Header with profile icon, username and new profile settings dropdown
    header = html.Div([
        html.Div([
            html.H2("Unified Skill Development Hub", className="dashboard-title"),
            html.Div([
                html.Span(id="username-display", className="me-2"),
                html.Div(
                    html.I(className="fas fa-user-circle fa-2x"),
                    id="profile-icon",
                    className="profile-icon",
                    **{'data-bs-toggle': 'dropdown'},
                ),
                profile_settings_dropdown,
            ], className="profile-container d-flex align-items-center"),
        ], className="d-flex justify-content-between align-items-center mb-3"),
        
        # Navigation buttons
        html.Div([
            # Primary navigation group (main actions)
            html.Div([
                dbc.Button("E-Books", id="ebooks-btn", color="primary", className="dashboard-btn"),
                dbc.Button("Courses", id="courses-btn", color="primary", className="dashboard-btn active"),
                dbc.Button("School Courses", id="courses2-btn", color="primary", className="dashboard-btn"),
                dbc.Button("Schemes", id="schemes-btn", color="primary", className="dashboard-btn"),
                dbc.Button(html.I(className="fas fa-map-marker-alt"), id="map-btn", color="primary", className="dashboard-btn"),
            ], className="nav-group-primary"),
            
            # Secondary navigation group (additional features)
            html.Div([
                dbc.Button("Resume Maker", id="resume-btn", color="primary", className="dashboard-btn"),
                dbc.Button("My Space", id="my-space-btn", color="primary", className="dashboard-btn"),
                dbc.Button("Study Plan", id="study-plan-btn", color="primary", className="dashboard-btn"),
                dbc.Button("Live", id="live-btn", color="primary", className="dashboard-btn"),
            ], className="nav-group-secondary"),
        ], className="button-container mb-3"),
        
        # Search and filter area
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Input(id="search-input", placeholder="Search...", type="text"),
                ], width=6),
                dbc.Col([
                    dbc.Button("Search", id="search-button", color="success", className="ms-2"),
                    dbc.Button("Reset", id="reset-button", color="secondary", className="ms-2"),
                ], width=6, className="d-flex"),
            ], className="mb-3"),
            html.Div(id="filter-area", className="mb-3"),
        ], id="search-filter-area", className="mb-3"),
    ], className="dashboard-header")
    
    # Main content area
    content = html.Div([
        # Statistics cards
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Total Items", className="card-title"),
                            html.H3(id="total-items-count", className="card-text"),
                        ])
                    ]),
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Categories", className="card-title"),
                            html.H3(id="categories-count", className="card-text"),
                        ])
                    ]),
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(id="special-stat-title", className="card-title"),
                            html.H3(id="special-stat-value", className="card-text"),
                        ])
                    ]),
                ], width=4),
            ], className="mb-4"),
        ], id="stats-area"),
        
        html.Div(id="table-content", className="table-container"),
        
        # Welcome message
        html.Div([
            html.H3("Welcome to the Unified Skill Development Hub", className="text-center mb-4"),
            html.P("Select a button above to view the corresponding data.", className="text-center"),
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("E-Books", className="card-title"),
                        html.P("Access educational e-books from various sources categorized by subject and state."),
                        dbc.Button("View E-Books", id="card-ebooks-btn", color="primary"),
                    ])
                ], className="m-2"),
                dbc.Card([
                    dbc.CardBody([
                        html.H5("UG/PG Courses", className="card-title"),
                        html.P("Explore higher education courses and programs available online."),
                        dbc.Button("View Courses", id="card-courses-btn", color="primary"),
                    ])
                ], className="m-2"),
                dbc.Card([
                    dbc.CardBody([
                        html.H5("School Courses", className="card-title"),
                        html.P("Find educational resources for grades 1-12 across various subjects."),
                        dbc.Button("View School Courses", id="card-courses2-btn", color="primary"),
                    ])
                ], className="m-2"),
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Schemes", className="card-title"),
                        html.P("Discover educational schemes, scholarships, and benefits available to students."),
                        dbc.Button("View Schemes", id="card-schemes-btn", color="primary"),
                    ])
                ], className="m-2"),
            ], className="d-flex flex-wrap justify-content-center")
        ], id="welcome-content", className="welcome-container", style={"display": "none"}),
    ], className="dashboard-content")

    # Chatbot Modal
    chatbot_modal = dbc.Modal([
        dbc.ModalHeader([
            html.Div([
                html.Div([
                    html.I(className="fas fa-robot me-2", style={
                        'color': '#3498db',
                        'fontSize': '32px',
                        'textShadow': '0 0 10px rgba(52, 152, 219, 0.5)',
                        'animation': 'pulse 2s infinite'
                    }),
                    html.H4("USDH Assistant", className="mb-0", style={
                        'color': '#2c3e50',
                        'fontSize': '28px',
                        'fontWeight': 'bold',
                        'letterSpacing': '0.5px'
                    }),
                    html.Div([
                        html.Span("●", style={
                            'color': '#2ecc71',
                            'marginRight': '5px',
                            'animation': 'glow 1.5s ease-in-out infinite alternate'
                        }),
                        "Online"
                    ], className="status-indicator", style={
                        'fontSize': '14px',
                        'color': '#2ecc71',
                        'marginLeft': '15px',
                        'display': 'flex',
                        'alignItems': 'center'
                    })
                ], className="d-flex align-items-center")
            ], className="d-flex align-items-center justify-content-between w-100")
        ], style={
            'backgroundColor': '#ffffff',
            'borderBottom': '2px solid #e9ecef',
            'padding': '20px 25px'
        }),
        dbc.ModalBody([
            html.Div([
                # Chat messages container with enhanced styling
                html.Div(id="chat-messages", className="chat-messages mb-4", style={
                    'height': '400px',
                    'overflowY': 'auto',
                    'padding': '25px',
                    'backgroundColor': '#ffffff',
                    'borderRadius': '20px',
                    'border': '1px solid #e9ecef',
                    'boxShadow': '0 5px 15px rgba(0, 0, 0, 0.05)',
                    'background': 'linear-gradient(to bottom, #ffffff, #f8f9fa)'
                }),
                
                # Options container with enhanced styling
                html.Div([
                    html.Div([
                        html.H5("How can I assist you today?", className="text-center mb-4", style={
                            'color': '#2c3e50',
                            'fontSize': '22px',
                            'fontWeight': 'bold',
                            'position': 'relative',
                            'paddingBottom': '15px'
                        }),
                        html.Div(style={
                            'width': '60px',
                            'height': '3px',
                            'background': 'linear-gradient(to right, #3498db, #2980b9)',
                            'margin': '0 auto 30px',
                            'borderRadius': '3px'
                        })
                    ]),
                    
                    # Options grid with enhanced styling
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.I(className="fas fa-route me-2"),
                                    "Course Roadmap"
                                ],
                                id="chat-roadmap-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-briefcase me-2"),
                                    "Career Roadmap"
                                ],
                                id="chat-career-roadmap-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.I(className="fas fa-lightbulb me-2"),
                                    "Career Guidance"
                                ],
                                id="chat-career-guidance-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-question-circle me-2"),
                                    "Help"
                                ],
                                id="chat-help-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            )
                        ], width=6)
                    ])
                ], className="options-container", style={
                    'padding': '25px',
                    'background': 'linear-gradient(to bottom right, #ffffff, #f8f9fa)',
                    'borderRadius': '20px',
                    'boxShadow': '0 5px 15px rgba(0, 0, 0, 0.05)'
                })
            ])
        ], style={'backgroundColor': '#ffffff', 'padding': '25px'}),
        dbc.ModalFooter([
            dbc.Button(
                "Close Chat",
                id="close-chatbot-btn",
                className="ms-auto",
                style={
                    'background': 'linear-gradient(135deg, #95a5a6, #7f8c8d)',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '10px',
                    'fontWeight': '600',
                    'transition': 'all 0.3s ease'
                }
            )
        ], style={
            'backgroundColor': '#ffffff',
            'borderTop': '2px solid #e9ecef',
            'padding': '20px 25px'
        })
    ], id="chatbot-modal", is_open=False, backdrop="static", keyboard=False,
       size="lg", contentClassName="cyber-modal", style={
           'borderRadius': '25px',
           'overflow': 'hidden',
           'boxShadow': '0 10px 30px rgba(0, 0, 0, 0.15)'
       })

    # Chat button with enhanced styling
    chat_button = html.Div([
        dbc.Button(
            html.I(className="fas fa-comments fa-lg"),
            id="open-chatbot-btn",
            className="chat-button",
            style={
                'position': 'fixed',
                'bottom': '30px',
                'right': '30px',
                'width': '65px',
                'height': '65px',
                'borderRadius': '50%',
                'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                'border': 'none',
                'boxShadow': '0 5px 20px rgba(52, 152, 219, 0.4)',
                'zIndex': '1000',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'transition': 'all 0.3s ease',
                'animation': 'pulse 2s infinite'
            }
        )
    ])


    # Combine all components
    dashboard_layout = html.Div([
        # Add logo
        html.Div(
            html.Img(src="/static/images/logo.png", alt="USDH Logo"),
            className="dashboard-logo"
        ),
        dbc.Container([
            header,
            content,
            chatbot_modal,
            chat_button,
            
            # Store components for state management
            dcc.Store(id="current-table", data="courses"),
            dcc.Store(id="filtered-data"),
            dcc.Store(id="user-data"),
            
            # Hidden div for triggering callbacks
            html.Div(id="callback-trigger", style={"display": "none"}),
            
            # Certificate Upload Modal
            dbc.Modal([
                dbc.ModalHeader([
                    html.I(className="fas fa-certificate me-2", style={'color': '#0ff'}),
                    html.Span("Upload Certificate", style={'color': '#0ff'})
                ], style={'backgroundColor': '#111', 'borderBottom': '1px solid #0ff'}),
                dbc.ModalBody([
                    html.Div([
                        html.H5("Certificate Details", style={'color': '#0ff', 'marginBottom': '15px'}),
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Certificate Name", style={'color': '#0ff'}),
                                    dbc.Input(id="certificate-name", type="text", className="cyber-input mb-3",
                                             placeholder="Enter certificate name")
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Issuing Organization", style={'color': '#0ff'}),
                                    dbc.Input(id="certificate-org", type="text", className="cyber-input mb-3",
                                             placeholder="Enter issuing organization")
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Issue Date", style={'color': '#0ff'}),
                                    dbc.Input(id="certificate-date", type="date", className="cyber-input mb-3")
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Certificate File (PDF/JPEG)", style={'color': '#0ff'}),
                                    dcc.Upload(
                                        id='certificate-upload',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select a File', style={'color': '#0ff'})
                                        ], style={'color': '#0ff'}),
                                        style={
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px 0',
                                            'borderColor': '#0ff'
                                        },
                                        multiple=False
                                    ),
                                    html.Div(id='certificate-upload-output', className="mt-2")
                                ], width=12),
                            ]),
                            html.Div(id="certificate-upload-status", className="mt-3")
                        ])
                    ])
                ], style={'backgroundColor': '#111'}),
                dbc.ModalFooter([
                    dbc.Button("Upload Certificate", id="upload-certificate-btn", className="cyber-button"),
                    dbc.Button("Cancel", id="cancel-certificate-btn", className="cyber-button ms-2")
                ], style={'backgroundColor': '#111', 'borderTop': '1px solid #0ff'})
            ], id="certificate-upload-modal", is_open=False, backdrop="static", keyboard=False,
               size="lg", contentClassName="cyber-modal"),

            # View Certificate Modal
            dbc.Modal([
                dbc.ModalHeader([
                    html.I(className="fas fa-certificate me-2", style={'color': '#0ff'}),
                    html.Span("View Certificates", style={'color': '#0ff'})
                ], style={'backgroundColor': '#111', 'borderBottom': '1px solid #0ff'}),
                dbc.ModalBody([
                    html.Div([
                        html.H5("Your Certificates", style={'color': '#0ff', 'marginBottom': '15px'}),
                        html.Div(id="certificates-list", className="certificates-container")
                    ])
                ], style={'backgroundColor': '#111'}),
                dbc.ModalFooter([
                    dbc.Button("Close", id="close-view-certificates-btn", className="cyber-button")
                ], style={'backgroundColor': '#111', 'borderTop': '1px solid #0ff'})
            ], id="view-certificates-modal", is_open=False, backdrop="static", keyboard=False,
               size="lg", contentClassName="cyber-modal"),

            # Skill India Map Modal
            dbc.Modal([
                dbc.ModalBody([
                    html.Div([
                        html.Div([
                            html.Iframe(
                                src="https://www.skillindiadigital.gov.in/skill-india-map",
                                style={
                                    'width': '100%',
                                    'height': 'calc(100% + 150px + 500px)',
                                    'position': 'absolute',
                                    'top': '-150px',
                                    'left': '0',
                                    'bottom': '-500px',
                                    'border': 'none'
                                }
                            )
                        ], style={
                            'width': '100vw',
                            'height': '100vh',
                            'position': 'relative',
                            'overflow': 'hidden'
                        }),
                        dbc.Button(
                            html.I(className="fas fa-times"),
                            id="close-map-modal-btn",
                            className="position-absolute top-0 end-0 m-3",
                            style={'backgroundColor': '#0ff', 'border': 'none', 'color': '#111'}
                        )
                    ], style={'position': 'relative'})
                ], style={'backgroundColor': '#111', 'padding': '0', 'margin': '0', 'overflow': 'hidden'})
            ], id="map-modal", is_open=False, backdrop="static", keyboard=True,
               size="xl", contentClassName="cyber-modal"),

            # User Profile Modal
            dbc.Modal([
                dbc.ModalHeader([
                    html.I(className="fas fa-user me-2", style={'color': '#1a237e'}),
                    html.Span("User Profile", style={'color': '#1a237e', 'fontWeight': 'bold'})
                ], style={'backgroundColor': '#f5f6fa', 'borderBottom': '1px solid #e0e0e0'}),
                dbc.ModalBody([
                    html.Div([
                        html.H5("Profile Information", style={'color': '#1a237e', 'marginBottom': '15px', 'fontWeight': 'bold'}),
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Current Username", style={'color': '#1a237e'}),
                                    html.P(id="user-profile-username", className="form-control-static",
                                         style={'color': '#2c3e50', 'padding': '0.375rem 0.75rem',
                                               'border': '1px solid #e0e0e0', 'borderRadius': '0.25rem',
                                               'backgroundColor': '#ffffff'})
                                ], width=12, className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("New Username", style={'color': '#1a237e'}),
                                    dbc.Input(
                                        type="text",
                                        id="new-username",
                                        placeholder="Enter new username",
                                        style={'backgroundColor': '#ffffff', 'color': '#2c3e50', 'borderColor': '#e0e0e0'}
                                    )
                                ], width=12, className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Current Email", style={'color': '#1a237e'}),
                                    html.P(id="user-profile-email", className="form-control-static",
                                         style={'color': '#2c3e50', 'padding': '0.375rem 0.75rem',
                                               'border': '1px solid #e0e0e0', 'borderRadius': '0.25rem',
                                               'backgroundColor': '#ffffff'})
                                ], width=12, className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("New Email", style={'color': '#1a237e'}),
                                    dbc.Input(
                                        type="email",
                                        id="new-email",
                                        placeholder="Enter new email",
                                        style={'backgroundColor': '#ffffff', 'color': '#2c3e50', 'borderColor': '#e0e0e0'}
                                    )
                                ], width=12, className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Current Password", style={'color': '#1a237e'}),
                                    dbc.Input(
                                        type="password",
                                        id="current-password",
                                        placeholder="Enter current password",
                                        style={'backgroundColor': '#ffffff', 'color': '#2c3e50', 'borderColor': '#e0e0e0'}
                                    )
                                ], width=12, className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("New Password", style={'color': '#1a237e'}),
                                    dbc.Input(
                                        type="password",
                                        id="new-password",
                                        placeholder="Enter new password",
                                        style={'backgroundColor': '#ffffff', 'color': '#2c3e50', 'borderColor': '#e0e0e0'}
                                    )
                                ], width=12, className="mb-3"),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Confirm New Password", style={'color': '#1a237e'}),
                                    dbc.Input(
                                        type="password",
                                        id="confirm-password",
                                        placeholder="Confirm new password",
                                        style={'backgroundColor': '#ffffff', 'color': '#2c3e50', 'borderColor': '#e0e0e0'}
                                    )
                                ], width=12, className="mb-3"),
                            ]),
                            html.Div(id="password-change-status", className="mt-2"),
                            dbc.Button(
                                "Change Password",
                                id="change-password-btn",
                                color="primary",
                                className="mt-3",
                                style={'backgroundColor': '#1a237e', 'borderColor': '#1a237e', 'color': 'white'}
                            )
                        ])
                    ])
                ], style={'backgroundColor': '#ffffff'}),
                dbc.ModalFooter([
                    dbc.Button("Close", id="close-user-profile-btn", className="btn-secondary")
                ], style={'backgroundColor': '#f5f6fa', 'borderTop': '1px solid #e0e0e0'})
            ], id="user-profile-modal", is_open=False, backdrop="static", keyboard=False,
               size="lg", contentClassName="profile-modal"),
        ], fluid=True, className="dashboard-container py-4")
    ], className="dashboard-bg")
    
    return dashboard_layout


# Register callbacks for the user dashboard
def register_callbacks(app):
    # Callback to update filters based on each other
    @app.callback(
        [Output("website-filter", "options"),
         Output("website-filter", "value")],
        [Input("discipline-filter", "value")],
        [State("current-table", "data")]
    )
    def update_website_options(discipline, current_table):
        if current_table != "courses":
            return [], None
            
        try:
            conn = sqlite3.connect('data/USDH.db')
            
            # Build query based on discipline filter
            if discipline:
                query = "SELECT DISTINCT website_name FROM courses WHERE dispcipline = ?"
                params = [discipline]
            else:
                query = "SELECT DISTINCT website_name FROM courses"
                params = []
            
            # Get unique websites
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            websites = [w[0] for w in cursor.fetchall() if w[0]]  # Filter out None/empty values
            conn.close()
            
            return [{"label": w, "value": w} for w in sorted(websites)], None
            
        except Exception as e:
            print(f"Error updating website options: {e}")
            return [], None

    # Callback for applying combined filters
    @app.callback(
        Output("table-content", "children", allow_duplicate=True),
        [Input("discipline-filter", "value"),
         Input("website-filter", "value")],
        [State("current-table", "data"),
         State("search-input", "value")],
        prevent_initial_call=True
    )
    def apply_combined_filters(discipline, website, current_table, search_query):
        if current_table != "courses":
            return dash.no_update
            
        try:
            conn = sqlite3.connect('data/USDH.db')
            
            # Start with base query
            query = "SELECT * FROM courses"
            where_clauses = []
            params = []
            
            # Add search condition if exists
            if search_query:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(courses)")
                columns = [col[1] for col in cursor.fetchall()]
                search_conditions = " OR ".join([f"{col} LIKE ?" for col in columns])
                where_clauses.append(f"({search_conditions})")
                params.extend([f"%{search_query}%" for _ in columns])
            
            # Apply discipline filter
            if discipline:
                where_clauses.append("dispcipline = ?")
                params.append(discipline)
            
            # Apply website filter
            if website:
                where_clauses.append("website_name = ?")
                params.append(website)
            
            # Combine where clauses
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            
            return format_courses_table(df)
            
        except Exception as e:
            return html.Div([
                html.H3("Error Applying Filters", className="text-danger"),
                html.P(f"Error: {str(e)}")
            ])

    # Callback for ebooks filters
    @app.callback(
        [Output("ebook-state-filter", "options"),
         Output("ebook-state-filter", "value")],
        [Input("ebook-subject-filter", "value")],
        [State("current-table", "data")]
    )
    def update_state_options(subject, current_table):
        if current_table != "ebooks":
            return [], None
            
        try:
            conn = sqlite3.connect('data/USDH.db')
            
            # Build query based on subject filter
            if subject:
                query = "SELECT DISTINCT states FROM ebooks WHERE subject = ?"
                params = [subject]
            else:
                query = "SELECT DISTINCT states FROM ebooks"
                params = []
            
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            states = [s[0] for s in cursor.fetchall() if s[0]]
            conn.close()
            
            return [{"label": s, "value": s} for s in sorted(states)], None
            
        except Exception as e:
            print(f"Error updating state options: {e}")
            return [], None

    # Callback for applying combined ebooks filters
    @app.callback(
        Output("table-content", "children", allow_duplicate=True),
        [Input("ebook-subject-filter", "value"),
         Input("ebook-state-filter", "value")],
        [State("current-table", "data"),
         State("search-input", "value")],
        prevent_initial_call=True
    )
    def apply_combined_ebook_filters(subject, state, current_table, search_query):
        if current_table != "ebooks":
            return dash.no_update
            
        try:
            conn = sqlite3.connect('data/USDH.db')
            
            # Start with base query
            query = "SELECT * FROM ebooks"
            where_clauses = []
            params = []
            
            # Add search condition if exists
            if search_query:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(ebooks)")
                columns = [col[1] for col in cursor.fetchall()]
                search_conditions = " OR ".join([f"{col} LIKE ?" for col in columns])
                where_clauses.append(f"({search_conditions})")
                params.extend([f"%{search_query}%" for _ in columns])
            
            # Apply subject filter
            if subject:
                where_clauses.append("subject = ?")
                params.append(subject)
            
            # Apply state filter
            if state:
                where_clauses.append("states = ?")
                params.append(state)
            
            # Combine where clauses
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            
            return format_ebooks_table(df)
            
        except Exception as e:
            return html.Div([
                html.H3("Error Applying Filters", className="text-danger"),
                html.P(f"Error: {str(e)}")
            ])
    # Update username display
    @app.callback(
        Output("username-display", "children"),
        Input("callback-trigger", "children"),
    )
    def update_username(_):
        username = session.get("username", "User")
        return f"Hello, {username}"
    
    # Initialize default view on page load
    @app.callback(
        [Output("table-content", "children"),
         Output("filter-area", "children")],
        [Input("callback-trigger", "children")]
    )
    def initialize_default_view(_):
        # Load courses table as default
        table_content = load_table_content("courses", None)
        filter_dropdowns = get_filter_dropdowns("courses")
        return table_content, filter_dropdowns
    
    # Handle table button clicks
    @app.callback(
        [Output("table-content", "children", allow_duplicate=True),
         Output("welcome-content", "style"),
         Output("current-table", "data"),
         Output("filter-area", "children", allow_duplicate=True)],
        [Input("ebooks-btn", "n_clicks"),
         Input("courses-btn", "n_clicks"),
         Input("courses2-btn", "n_clicks"),
         Input("schemes-btn", "n_clicks"),
         Input("card-ebooks-btn", "n_clicks"),
         Input("card-courses-btn", "n_clicks"),
         Input("card-courses2-btn", "n_clicks"),
         Input("card-schemes-btn", "n_clicks")],
        [State("current-table", "data")],
        prevent_initial_call=True
    )
    def update_table_content(ebooks_clicks, courses_clicks, courses2_clicks, schemes_clicks,
                             card_ebooks_clicks, card_courses_clicks, card_courses2_clicks, card_schemes_clicks,
                             current_table):
        ctx = callback_context
        
        # Determine which button was clicked
        if not ctx.triggered:
            # Initial load or no button clicked, keep current state
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Map buttons to table names
        table_mapping = {
            "ebooks-btn": "ebooks",
            "courses-btn": "courses",
            "courses2-btn": "courses2",
            "schemes-btn": "schemes",
            "card-ebooks-btn": "ebooks",
            "card-courses-btn": "courses",
            "card-courses2-btn": "courses2",
            "card-schemes-btn": "schemes"
        }
        
        if button_id in table_mapping:
            table_name = table_mapping[button_id]
            return load_table_content(table_name, None), {"display": "none"}, table_name, get_filter_dropdowns(table_name)
        
        # Fallback - keep current state
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Handle search and reset actions
    @app.callback(
        Output("table-content", "children", allow_duplicate=True),
        [Input("search-button", "n_clicks"),
         Input("reset-button", "n_clicks")],
        [State("current-table", "data"),
         State("search-input", "value")],
        prevent_initial_call=True
    )
    def handle_search_reset(search_clicks, reset_clicks, current_table, search_query):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "reset-button":
            # Reset the search (reload without filters)
            return load_table_content(current_table, None)
        elif button_id == "search-button":
            # Apply search filter
            return load_table_content(current_table, search_query)
            
        return dash.no_update
    
    # Update statistics based on current table
    @app.callback(
        [Output("total-items-count", "children"),
         Output("categories-count", "children"),
         Output("special-stat-title", "children"),
         Output("special-stat-value", "children")],
        [Input("current-table", "data")]
    )
    def update_statistics(table_name):
        if not table_name:
            return "0", "0", "N/A", "N/A"
            
        try:
            conn = sqlite3.connect('data/USDH.db')
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            conn.close()
            
            total_items = len(df)
            
            # Different category metrics based on table
            if table_name == "ebooks":
                categories = df['subject'].nunique() if 'subject' in df.columns else 0
                special_title = "States"
                special_value = df['states'].nunique() if 'states' in df.columns else 0
            elif table_name == "courses":
                categories = df['dispcipline'].nunique() if 'dispcipline' in df.columns else 0
                special_title = "Courses"
                special_value = total_items
            elif table_name == "courses2":
                categories = df['subjects'].nunique() if 'subjects' in df.columns else 0
                special_title = "Grades"
                special_value = df['grade'].nunique() if 'grade' in df.columns else 0
            elif table_name == "schemes":
                categories = df['name'].nunique() if 'name' in df.columns else 0
                special_title = "Benefits"
                special_value = total_items
            else:
                categories = 0
                special_title = "N/A"
                special_value = "N/A"
                
            return str(total_items), str(categories), special_title, str(special_value)
        except Exception as e:
            print(f"Error updating statistics: {e}")
            return "Error", "Error", "Error", "Error"
    
    # Filter dropdown callbacks
    @app.callback(
        Output("table-content", "children", allow_duplicate=True),
        [Input("subject-filter", "value"),
         Input("grade-filter", "value"),
         Input("discipline-filter", "value"),
         Input("ebook-subject-filter", "value"),
         Input("ebook-state-filter", "value")],
        [State("current-table", "data"),
         State("search-input", "value")],
        prevent_initial_call=True
    )
    def apply_filters(subject, grade, discipline, ebook_subject, ebook_state, current_table, search_query):
        try:
            conn = sqlite3.connect('data/USDH.db')
            
            # Start with base query
            query = f"SELECT * FROM {current_table}"
            where_clauses = []
            params = []
            
            # Add search condition if exists
            if search_query:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({current_table})")
                columns = [col[1] for col in cursor.fetchall()]
                search_conditions = " OR ".join([f"{col} LIKE ?" for col in columns])
                where_clauses.append(f"({search_conditions})")
                params.extend([f"%{search_query}%" for _ in columns])
            
            # Apply subject filter
            if subject:
                where_clauses.append("subjects = ?")
                params.append(subject)
            
            # Apply grade filter
            if grade:
                where_clauses.append("grade = ?")
                params.append(grade)
            
            # Apply discipline filter
            if discipline:
                where_clauses.append("dispcipline = ?")
                params.append(discipline)
            
            # Apply ebook subject filter
            if ebook_subject:
                where_clauses.append("subject = ?")
                params.append(ebook_subject)
            
            # Apply ebook state filter
            if ebook_state:
                where_clauses.append("states = ?")
                params.append(ebook_state)
            
            # Combine where clauses
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            
            # Format based on current table type
            if current_table == "courses2":
                return format_courses2_table(df)
            elif current_table == "courses":
                return format_courses_table(df)
            elif current_table == "ebooks":
                return format_ebooks_table(df)
            else:
                return html.Div([
                    html.H3(f"{current_table.capitalize()} Table", className="mb-3"),
                    dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
                ])
                    
        except Exception as e:
            return html.Div([
                html.H3("Error Applying Filters", className="text-danger"),
                html.P(f"Error: {str(e)}")
            ])
    
    # Profile dropdown toggle (existing)
    @app.callback(
        Output("profile-dropdown", "className"),
        [Input("profile-icon", "n_clicks")],
        [State("profile-dropdown", "className")]
    )
    def toggle_profile_dropdown(n_clicks, current_class):
        if n_clicks:
            if "show" in current_class:
                return "dropdown-menu"
            else:
                return "dropdown-menu show"
        return "dropdown-menu"
    
    # Callback to toggle nested options for "My Courses"
    @app.callback(
        Output("my-courses-collapse", "is_open"),
        [Input("my-courses-item", "n_clicks")],
        [State("my-courses-collapse", "is_open")]
    )
    def toggle_my_courses(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # Callback to toggle nested options for "My Certificate"
    @app.callback(
        Output("my-certificate-collapse", "is_open"),
        [Input("my-certificate-item", "n_clicks")],
        [State("my-certificate-collapse", "is_open")]
    )
    def toggle_my_certificate(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # Callback to open certificate upload modal
    @app.callback(
        Output("certificate-upload-modal", "is_open"),
        [Input("add-certificate-item", "n_clicks"),
         Input("cancel-certificate-btn", "n_clicks")],
        [State("certificate-upload-modal", "is_open")]
    )
    def toggle_certificate_upload_modal(add_clicks, cancel_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "add-certificate-item":
            return True
        elif trigger_id == "cancel-certificate-btn":
            return False
        return is_open

    # Callback to handle certificate file upload
    @app.callback(
        [Output("certificate-upload-output", "children"),
         Output("certificate-upload-status", "children")],
        [Input("certificate-upload", "contents")],
        [State("certificate-upload", "filename")]
    )
    def handle_certificate_upload(contents, filename):
        if contents is None:
            return "", ""
            
        if filename is None:
            return "", html.Div("No file selected", style={"color": "red"})
            
        # Check file extension
        if not filename.lower().endswith(('.pdf', '.jpg', '.jpeg')):
            return "", html.Div("Please upload a PDF or JPEG file", style={"color": "red"})
            
        return html.Div(f"Selected file: {filename}", style={"color": "#0ff"}), ""

    # Callback to handle certificate upload submission
    @app.callback(
        [Output("certificate-upload-modal", "is_open", allow_duplicate=True),
         Output("certificate-upload-status", "children", allow_duplicate=True)],
        [Input("upload-certificate-btn", "n_clicks")],
        [State("certificate-name", "value"),
         State("certificate-org", "value"),
         State("certificate-date", "value"),
         State("certificate-upload", "contents"),
         State("certificate-upload", "filename")],
        prevent_initial_call=True
    )
    def handle_certificate_submission(n_clicks, name, org, date, contents, filename):
        if not n_clicks:
            return dash.no_update, dash.no_update
            
        if not all([name, org, date, contents, filename]):
            return dash.no_update, html.Div("Please fill in all fields and upload a file", style={"color": "red"})
            
        try:
            # Get user ID from session
            user_id = session.get("user_id")
            if not user_id:
                return dash.no_update, html.Div("Session expired. Please log in again.", style={"color": "red"})
                
            # Create certificates directory if it doesn't exist
            import os
            cert_dir = os.path.join("static", "certificates", str(user_id))
            os.makedirs(cert_dir, exist_ok=True)
            
            # Save certificate file
            import base64
            
            # Decode base64 content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Generate unique filename
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(filename)[1].lower()
            new_filename = f"{current_time}{file_extension}"
            filepath = os.path.join(cert_dir, new_filename)
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(decoded)
                
            # Save certificate details to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Create certificates table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certificates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    organization TEXT,
                    issue_date TEXT,
                    file_path TEXT,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Get current timestamp for upload_date
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert certificate record
            cursor.execute('''
                INSERT INTO certificates (user_id, name, organization, issue_date, file_path, upload_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, org, date, new_filename, current_timestamp))
            
            conn.commit()
            conn.close()
            
            return False, html.Div("Certificate uploaded successfully!", style={"color": "green"})
            
        except Exception as e:
            print(f"Error uploading certificate: {str(e)}")
            return dash.no_update, html.Div(f"Error uploading certificate: {str(e)}", style={"color": "red"})

    # Callback to open view certificates modal
    @app.callback(
        Output("view-certificates-modal", "is_open"),
        [Input("view-certificate-item", "n_clicks"),
         Input("close-view-certificates-btn", "n_clicks")],
        [State("view-certificates-modal", "is_open")]
    )
    def toggle_view_certificates_modal(view_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "view-certificate-item":
            return True
        elif trigger_id == "close-view-certificates-btn":
            return False
        return is_open

    # Callback to load and display certificates
    @app.callback(
        Output("certificates-list", "children"),
        [Input("view-certificates-modal", "is_open")]
    )
    def load_certificates(is_open):
        if not is_open:
            return []
            
        try:
            # Get user ID from session
            user_id = session.get("user_id")
            if not user_id:
                return html.Div("Session expired. Please log in again.", style={"color": "red"})
                
            # Connect to database and create certificates table if it doesn't exist
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Create certificates table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certificates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    organization TEXT,
                    issue_date TEXT,
                    file_path TEXT,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Fetch certificates
            cursor.execute('''
                SELECT id, name, organization, issue_date, file_path, upload_date
                FROM certificates
                WHERE user_id = ?
                ORDER BY upload_date DESC
            ''', (user_id,))
            certificates = cursor.fetchall()
            conn.close()
            
            if not certificates:
                return html.Div("No certificates found.", style={"color": "#0ff"})
                
            # Create certificate cards
            certificate_cards = []
            for cert in certificates:
                cert_id, name, org, issue_date, file_path, upload_date = cert
                cert_url = f"/static/certificates/{user_id}/{file_path}"
                
                card = dbc.Card([
                    dbc.CardHeader([
                        html.H5(name, className="mb-0", style={'color': '#0ff'})
                    ], style={'backgroundColor': '#222', 'borderBottom': '1px solid #0ff'}),
                    dbc.CardBody([
                        html.P([
                            html.Strong("Organization: ", style={'color': '#0ff'}),
                            org
                        ], className="mb-2"),
                        html.P([
                            html.Strong("Issue Date: ", style={'color': '#0ff'}),
                            issue_date
                        ], className="mb-2"),
                        html.P([
                            html.Strong("Upload Date: ", style={'color': '#0ff'}),
                            upload_date
                        ], className="mb-2"),
                        html.A(
                            "View Certificate",
                            href=cert_url,
                            target="_blank",
                            className="btn btn-primary mt-2",
                            style={'backgroundColor': '#0ff', 'borderColor': '#0ff'}
                        )
                    ], style={'backgroundColor': '#222'})
                ], className="mb-3", style={'border': '1px solid #0ff'})
                certificate_cards.append(card)
            
            return certificate_cards
            
        except Exception as e:
            print(f"Error loading certificates: {str(e)}")
            return html.Div(f"Error loading certificates: {str(e)}", style={"color": "red"})

    # Callback to open/close map modal
    @app.callback(
        Output("map-modal", "is_open"),
        [Input("map-btn", "n_clicks"),
         Input("close-map-modal-btn", "n_clicks")],
        [State("map-modal", "is_open")]
    )
    def toggle_map_modal(map_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "map-btn":
            return True
        elif trigger_id == "close-map-modal-btn":
            return False
        return is_open

    # Callback to toggle user profile modal
    @app.callback(
        Output("user-profile-modal", "is_open"),
        [Input("user-profile-item", "n_clicks"),
         Input("close-user-profile-btn", "n_clicks")],
        [State("user-profile-modal", "is_open")]
    )
    def toggle_user_profile_modal(profile_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "user-profile-item":
            return True
        elif trigger_id == "close-user-profile-btn":
            return False
        return is_open

    # Callback to load and display user profile information
    @app.callback(
        [Output("user-profile-username", "children"),
         Output("user-profile-email", "children")],
        [Input("user-profile-modal", "is_open"),
         Input("change-email-btn", "n_clicks")]
    )
    def load_user_profile(is_open, _):
        if not is_open:
            return "", ""
            
        try:
            # Get user ID from session
            user_id = session.get("user_id")
            if not user_id:
                return "Session expired", "Please log in again"
                
            # Connect to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Fetch user details
            cursor.execute('''
                SELECT username, email
                FROM users
                WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return user[0], user[1]
            else:
                return "User not found", "N/A"
                
        except Exception as e:
            print(f"Error loading user profile: {str(e)}")
            return "Error loading profile", "Please try again"

    # Callback to handle password change
    @app.callback(
        [Output("password-change-status", "children"),
         Output("current-password", "value"),
         Output("new-password", "value"),
         Output("confirm-password", "value")],
        [Input("change-password-btn", "n_clicks")],
        [State("current-password", "value"),
         State("new-password", "value"),
         State("confirm-password", "value")]
    )
    def change_password(n_clicks, current_password, new_password, confirm_password):
        if not n_clicks:
            return "", None, None, None
            
        if not all([current_password, new_password, confirm_password]):
            return html.Div("Please fill in all password fields", style={"color": "red"}), None, None, None
            
        if new_password != confirm_password:
            return html.Div("New passwords do not match", style={"color": "red"}), None, None, None
            
        try:
            # Get user ID from session
            user_id = session.get("user_id")
            if not user_id:
                return html.Div("Session expired. Please log in again.", style={"color": "red"}), None, None, None
                
            # Connect to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Verify current password
            cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
            stored_password = cursor.fetchone()
            
            if not stored_password or stored_password[0] != current_password:
                conn.close()
                return html.Div("Current password is incorrect", style={"color": "red"}), None, None, None
                
            # Update password
            cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
            conn.commit()
            conn.close()
            
            return html.Div("Password changed successfully!", style={"color": "green"}), None, None, None
            
        except Exception as e:
            print(f"Error changing password: {str(e)}")
            return html.Div(f"Error changing password: {str(e)}", style={"color": "red"}), None, None, None

    # Callback to handle username change
    @app.callback(
        [Output("username-change-status", "children"),
         Output("new-username", "value"),
         Output("username-display", "children", allow_duplicate=True),
         Output("user-profile-username", "children", allow_duplicate=True)],
        [Input("change-username-btn", "n_clicks")],
        [State("new-username", "value"),
         State("current-password", "value")],
        prevent_initial_call=True
    )
    def change_username(n_clicks, new_username, current_password):
        if not n_clicks:
            return "", None, dash.no_update, dash.no_update
            
        if not new_username:
            return html.Div("Please enter a new username", style={"color": "red"}), None, dash.no_update, dash.no_update
            
        if len(new_username) < 3:
            return html.Div("Username must be at least 3 characters long", style={"color": "red"}), None, dash.no_update, dash.no_update
            
        try:
            # Get user ID from session
            user_id = session.get("user_id")
            if not user_id:
                return html.Div("Session expired. Please log in again.", style={"color": "red"}), None, dash.no_update, dash.no_update
                
            # Connect to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', (new_username, user_id))
            existing_user = cursor.fetchone()
            
            if existing_user:
                conn.close()
                return html.Div("Username already exists. Please choose another.", style={"color": "red"}), None, dash.no_update, dash.no_update
            
            # If current password is provided, verify it
            if current_password:
                cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
                stored_password = cursor.fetchone()
                
                if not stored_password or stored_password[0] != current_password:
                    conn.close()
                    return html.Div("Current password is incorrect", style={"color": "red"}), None, dash.no_update, dash.no_update
            
            # Update username
            cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
            conn.commit()
            conn.close()
            
            # Update session
            session["username"] = new_username
            
            return html.Div("Username changed successfully!", style={"color": "green"}), None, f"Hello, {new_username}", new_username
            
        except Exception as e:
            print(f"Error changing username: {str(e)}")
            return html.Div(f"Error changing username: {str(e)}", style={"color": "red"}), None, dash.no_update, dash.no_update

    # Callback to handle email change
    @app.callback(
        [Output("email-change-status", "children"),
         Output("new-email", "value"),
         Output("user-profile-email", "children", allow_duplicate=True)],
        [Input("change-email-btn", "n_clicks")],
        [State("new-email", "value"),
         State("current-password", "value")],
        prevent_initial_call=True
    )
    def change_email(n_clicks, new_email, current_password):
        if not n_clicks:
            return "", None, dash.no_update
            
        if not new_email:
            return html.Div("Please enter a new email address", style={"color": "red"}), None, dash.no_update
            
        # Basic email validation using regex
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(new_email):
            return html.Div("Please enter a valid email address", style={"color": "red"}), None, dash.no_update
            
        try:
            # Get user ID from session
            user_id = session.get("user_id")
            if not user_id:
                return html.Div("Session expired. Please log in again.", style={"color": "red"}), None, dash.no_update
                
            # Connect to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Check if email already exists for another user
            cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (new_email, user_id))
            existing_user = cursor.fetchone()
            
            if existing_user:
                conn.close()
                return html.Div("Email already in use. Please use a different email.", style={"color": "red"}), None, dash.no_update
            
            # If current password is provided, verify it
            if current_password:
                cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
                stored_password = cursor.fetchone()
                
                if not stored_password or stored_password[0] != current_password:
                    conn.close()
                    return html.Div("Current password is incorrect", style={"color": "red"}), None, dash.no_update
            
            # Update email
            cursor.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, user_id))
            conn.commit()
            conn.close()
            
            # Update session if needed
            if "email" in session:
                session["email"] = new_email
            
            return html.Div("Email changed successfully!", style={"color": "green"}), None, new_email
            
        except Exception as e:
            print(f"Error changing email: {str(e)}")
            return html.Div(f"Error changing email: {str(e)}", style={"color": "red"}), None, dash.no_update

    # Callback to handle resume maker button click
    @app.callback(
        Output("url", "pathname"),
        [Input("resume-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def navigate_to_resume_maker(n_clicks):
        if n_clicks:
            return "/resume-maker"
        return dash.no_update

    # Callback to handle My Space button click
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        [Input("my-space-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def navigate_to_my_space(n_clicks):
        if n_clicks:
            return "/my-space"
        return dash.no_update

    # Callback to handle Study Plan button click
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        [Input("study-plan-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def navigate_to_study_plan(n_clicks):
        if n_clicks:
            return "/study-plan"
        return dash.no_update

    # Chatbot callbacks
    @app.callback(
        Output("chatbot-modal", "is_open"),
        [Input("open-chatbot-btn", "n_clicks"),
         Input("close-chatbot-btn", "n_clicks")],
        [State("chatbot-modal", "is_open")]
    )
    def toggle_chatbot(open_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "open-chatbot-btn":
            return True
        elif trigger_id in ["close-chatbot-btn", "chat-close-option"]:
            return False
            
        return is_open

    @app.callback(
        [Output("chat-messages", "children"),
         Output("url", "pathname", allow_duplicate=True),
         Output("table-content", "children", allow_duplicate=True),
         Output("welcome-content", "style", allow_duplicate=True),
         Output("current-table", "data", allow_duplicate=True),
         Output("filter-area", "children", allow_duplicate=True)],
        [Input("chat-roadmap-option", "n_clicks"),
         Input("chat-career-roadmap-option", "n_clicks"),
         Input("chat-career-guidance-option", "n_clicks"),
         Input("chat-help-option", "n_clicks")],
        [State("chat-messages", "children")],
        prevent_initial_call=True
    )
    def handle_chat_options(roadmap_clicks, career_roadmap_clicks, career_guidance_clicks, help_clicks, current_messages):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        responses = get_chatbot_responses()
        
        if current_messages is None:
            current_messages = []
        
        if trigger_id == "chat-roadmap-option":
            # Fetch courses from both UG/PG and school courses tables
            try:
                conn = sqlite3.connect('data/USDH.db')
                
                # Get UG/PG courses
                ug_pg_df = pd.read_sql("SELECT course_name_ as name, 'UG/PG' as type FROM courses", conn)
                
                # Get school courses - updated query to get unique subjects
                school_df = pd.read_sql("SELECT DISTINCT subjects as name, 'School' as type FROM courses2 WHERE subjects IS NOT NULL", conn)
                
                conn.close()
                
                # Combine both dataframes
                all_courses = pd.concat([ug_pg_df, school_df], ignore_index=True)
                
                # Create course selection buttons with type indicators
                course_options = [
                    html.Div([
                        html.H5("Select a Course for Roadmap", 
                                style={'color': '#2c3e50', 'marginBottom': '15px'}),
                        html.P("Choose a course to see its detailed learning path:", 
                               style={'color': '#34495e', 'marginBottom': '20px'})
                    ], className="chat-message bot-message mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.Div(course['name'], className="course-name"),
                                    html.Small(f"({course['type']})", 
                                             style={'display': 'block', 'fontSize': '0.8em', 'opacity': '0.8'})
                                ],
                                id={"type": "roadmap-course", "index": f"{course['type']}_{course['name']}"},
                                className="w-100 mb-2 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            )
                        ]) for _, course in all_courses.iterrows()
                    ])
                ]
                return current_messages + course_options, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            except Exception as e:
                error_message = html.Div([
                    html.Div("Sorry, I couldn't load the courses. Please try again later.", 
                             className="chat-message bot-message")
                ], className="d-flex justify-content-start mb-2")
                return current_messages + [error_message], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        elif trigger_id == "chat-career-roadmap-option":
            career_options = html.Div([
                html.Div([
                    html.Div([
                        html.H2("Career Roadmap Explorer", className="career-roadmap-title"),
                        html.P("Choose your career path and discover the journey ahead", 
                               className="career-roadmap-subtitle")
                    ], className="career-roadmap-header"),
                    
                    # Technology Category
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-microchip"),
                            html.H3("Technology", className="career-category-title")
                        ], className="career-category-header"),
                        dbc.Button(
                            [
                                html.I(className="fas fa-code"),
                                html.Span("Software Development"),
                                html.Span("Build the future of technology through code", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "software"},
                            className="career-option-btn"
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-database"),
                                html.Span("Data Science"),
                                html.Span("Transform data into actionable insights", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "data_science"},
                            className="career-option-btn"
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-shield-alt"),
                                html.Span("Cybersecurity"),
                                html.Span("Protect digital assets and ensure online safety", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "cybersecurity"},
                            className="career-option-btn"
                        )
                    ], className="career-category"),
                    
                    # Business Category
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-briefcase"),
                            html.H3("Business", className="career-category-title")
                        ], className="career-category-header"),
                        dbc.Button(
                            [
                                html.I(className="fas fa-chart-line"),
                                html.Span("Finance & Investment"),
                                html.Span("Navigate the world of financial markets", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "finance"},
                            className="career-option-btn"
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-bullhorn"),
                                html.Span("Marketing"),
                                html.Span("Create compelling campaigns and drive growth", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "marketing"},
                            className="career-option-btn"
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-handshake"),
                                html.Span("Business Management"),
                                html.Span("Lead teams and drive organizational success", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "management"},
                            className="career-option-btn"
                        )
                    ], className="career-category"),
                    
                    # Creative Category
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-palette"),
                            html.H3("Creative", className="career-category-title")
                        ], className="career-category-header"),
                        dbc.Button(
                            [
                                html.I(className="fas fa-pencil-ruler"),
                                html.Span("UI/UX Design"),
                                html.Span("Create beautiful and intuitive user experiences", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "design"},
                            className="career-option-btn"
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-film"),
                                html.Span("Digital Media"),
                                html.Span("Tell stories through multimedia content", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "media"},
                            className="career-option-btn"
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-paint-brush"),
                                html.Span("Graphic Design"),
                                html.Span("Create visually stunning designs and artwork", 
                                        className="option-description")
                            ],
                            id={"type": "career-roadmap", "index": "graphic_design"},
                            className="career-option-btn"
                        )
                    ], className="career-category")
                ], className="career-roadmap-container chat-message bot-message")
            ], className="d-flex justify-content-start mb-3")

            # Initialize current_messages if None
            if current_messages is None:
                current_messages = []
            
            # Add user message first
            user_message = html.Div([
                html.Div("Show me career roadmaps", className="chat-message user-message")
            ], className="d-flex justify-content-end mb-3")
            
            # Return both user message and career options
            return current_messages + [user_message, career_options], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        elif trigger_id == "chat-career-guidance-option":
            guidance_message = html.Div([
                html.Div([
                    html.H5("Career Guidance", 
                            style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    html.P("Let me help you explore your career options. What are your interests?", 
                           style={'color': '#34495e', 'marginBottom': '20px'}),
                    html.Div([
                        dbc.Button(
                            [
                                html.I(className="fas fa-laptop-code me-2"),
                                "Technology"
                            ],
                            id={"type": "career-guidance", "index": "tech"},
                            className="w-100 mb-2 chat-option-btn",
                            style={
                                'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                'border': 'none',
                                'padding': '12px 20px',
                                'borderRadius': '12px',
                                'fontWeight': '600',
                                'letterSpacing': '0.5px',
                                'transition': 'all 0.3s ease',
                                'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                            }
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-chart-bar me-2"),
                                "Business"
                            ],
                            id={"type": "career-guidance", "index": "business"},
                            className="w-100 mb-2 chat-option-btn",
                            style={
                                'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                'border': 'none',
                                'padding': '12px 20px',
                                'borderRadius': '12px',
                                'fontWeight': '600',
                                'letterSpacing': '0.5px',
                                'transition': 'all 0.3s ease',
                                'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                            }
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-flask me-2"),
                                "Science"
                            ],
                            id={"type": "career-guidance", "index": "science"},
                            className="w-100 mb-2 chat-option-btn",
                            style={
                                'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                'border': 'none',
                                'padding': '12px 20px',
                                'borderRadius': '12px',
                                'fontWeight': '600',
                                'letterSpacing': '0.5px',
                                'transition': 'all 0.3s ease',
                                'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                            }
                        )
                    ])
                ], className="chat-message bot-message")
            ], className="d-flex justify-content-start mb-2")
            return current_messages + [guidance_message], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        elif trigger_id == "chat-help-option":
            help_message = html.Div([
                html.Div([
                    html.H5("How can I help you today?", 
                            style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    html.P("Select an option below:", 
                           style={'color': '#34495e', 'marginBottom': '20px'}),
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-book me-2"),
                                        "See My Study Materials"
                                    ],
                                    id={"type": "help-option", "index": "study-materials"},
                                    className="w-100 mb-3 chat-option-btn",
                                    style={
                                        'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                        'border': 'none',
                                        'padding': '12px 20px',
                                        'borderRadius': '12px',
                                        'fontWeight': '600',
                                        'letterSpacing': '0.5px',
                                        'transition': 'all 0.3s ease',
                                        'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)',
                                        'textAlign': 'left',
                                        'display': 'block',
                                        'width': '100%'
                                    }
                                ),
                            ], width=12),
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-file-pdf me-2"),
                                        "Access E-Books"
                                    ],
                                    id={"type": "help-option", "index": "ebooks"},
                                    className="w-100 mb-3 chat-option-btn",
                                    style={
                                        'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                        'border': 'none',
                                        'padding': '12px 20px',
                                        'borderRadius': '12px',
                                        'fontWeight': '600',
                                        'letterSpacing': '0.5px',
                                        'transition': 'all 0.3s ease',
                                        'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)',
                                        'textAlign': 'left',
                                        'display': 'block',
                                        'width': '100%'
                                    }
                                ),
                            ], width=12),
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-file-alt me-2"),
                                        "Create Resume"
                                    ],
                                    id={"type": "help-option", "index": "resume"},
                                    className="w-100 mb-3 chat-option-btn",
                                    style={
                                        'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                        'border': 'none',
                                        'padding': '12px 20px',
                                        'borderRadius': '12px',
                                        'fontWeight': '600',
                                        'letterSpacing': '0.5px',
                                        'transition': 'all 0.3s ease',
                                        'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)',
                                        'textAlign': 'left',
                                        'display': 'block',
                                        'width': '100%'
                                    }
                                ),
                            ], width=12),
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-tasks me-2"),
                                        "View My Progress"
                                    ],
                                    id={"type": "help-option", "index": "progress"},
                                    className="w-100 mb-3 chat-option-btn",
                                    style={
                                        'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                        'border': 'none',
                                        'padding': '12px 20px',
                                        'borderRadius': '12px',
                                        'fontWeight': '600',
                                        'letterSpacing': '0.5px',
                                        'transition': 'all 0.3s ease',
                                        'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)',
                                        'textAlign': 'left',
                                        'display': 'block',
                                        'width': '100%'
                                    }
                                ),
                            ], width=12),
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-certificate me-2"),
                                        "My Certificates"
                                    ],
                                    id={"type": "help-option", "index": "certificates"},
                                    className="w-100 mb-3 chat-option-btn",
                                    style={
                                        'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                        'border': 'none',
                                        'padding': '12px 20px',
                                        'borderRadius': '12px',
                                        'fontWeight': '600',
                                        'letterSpacing': '0.5px',
                                        'transition': 'all 0.3s ease',
                                        'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)',
                                        'textAlign': 'left',
                                        'display': 'block',
                                        'width': '100%'
                                    }
                                ),
                            ], width=12),
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-user-cog me-2"),
                                        "Update Profile"
                                    ],
                                    id={"type": "help-option", "index": "profile"},
                                    className="w-100 mb-3 chat-option-btn",
                                    style={
                                        'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                        'border': 'none',
                                        'padding': '12px 20px',
                                        'borderRadius': '12px',
                                        'fontWeight': '600',
                                        'letterSpacing': '0.5px',
                                        'transition': 'all 0.3s ease',
                                        'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)',
                                        'textAlign': 'left',
                                        'display': 'block',
                                        'width': '100%'
                                    }
                                ),
                            ], width=12),
                        ], className="g-3")
                    ], fluid=True, className="p-0")
                ], className="chat-message bot-message")
            ], className="d-flex justify-content-start mb-3")

            # Initialize current_messages if None
            if current_messages is None:
                current_messages = []
            
            # Add user message first
            user_message = html.Div([
                html.Div("I need help", className="chat-message user-message")
            ], className="d-flex justify-content-end mb-3")
            
            # Return both user message and help options
            return current_messages + [user_message, help_message], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Add callback for help options
    @app.callback(
        [Output("chat-messages", "children", allow_duplicate=True),
         Output("url", "pathname", allow_duplicate=True)],
        [Input({"type": "help-option", "index": ALL}, "n_clicks")],
        [State("chat-messages", "children")],
        prevent_initial_call=True
    )
    def handle_help_options(n_clicks, current_messages):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update
        
        # Get the triggered button's index
        trigger = ctx.triggered[0]
        if not trigger["value"]:  # If no click occurred
            return dash.no_update, dash.no_update
        
        # Get the button that was clicked
        button_id = json.loads(trigger["prop_id"].split(".")[0])
        option = button_id["index"]
        
        if current_messages is None:
            current_messages = []
        
        # Define responses and redirects for each option
        options = {
            "study-materials": {
                "message": "Taking you to your study materials...",
                "redirect": "/my-space"
            },
            "ebooks": {
                "message": "Opening your e-books...",
                "redirect": "/ebooks"
            },
            "resume": {
                "message": "Opening resume maker...",
                "redirect": "/resume-maker"
            },
            "progress": {
                "message": "Loading your progress...",
                "redirect": "/my-progress"
            },
            "certificates": {
                "message": "Opening your certificates...",
                "redirect": "/certificates"
            },
            "profile": {
                "message": "Opening your profile settings...",
                "redirect": "/profile"
            }
        }
        
        if option in options:
            response = options[option]
            bot_message = html.Div([
                html.Div(response["message"], className="chat-message bot-message")
            ], className="d-flex justify-content-start mb-2")
            
            return current_messages + [bot_message], response["redirect"]
        
        return dash.no_update, dash.no_update

    # Add callback for Live button
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        [Input("live-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def navigate_to_live(n_clicks):
        if n_clicks:
            return "/live"
        return dash.no_update

    # Add callback for roadmap course selection
    @app.callback(
        Output("chat-messages", "children", allow_duplicate=True),
        [Input({"type": "roadmap-course", "index": ALL}, "n_clicks")],
        [State("chat-messages", "children")],
        prevent_initial_call=True
    )
    def show_course_roadmap(n_clicks, current_messages):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update
        
        # Get the triggered button's index
        trigger = ctx.triggered[0]
        if not trigger["value"]:  # If no click occurred
            return dash.no_update
        
        # Get the button that was clicked
        button_id = json.loads(trigger["prop_id"].split(".")[0])
        course_name = button_id["index"]
        
        if current_messages is None:
            current_messages = []
        
        # Generate roadmap image
        roadmap_base64 = create_roadmap_image(course_name)
        
        # Create roadmap message with enhanced styling
        roadmap_message = html.Div([
            html.Div([
                html.H5(f"Learning Roadmap for {course_name}", 
                        style={'color': '#2c3e50', 'marginBottom': '15px'}),
                html.P("Here's your personalized learning path:", 
                       style={'color': '#34495e', 'marginBottom': '20px'}),
                html.Img(
                    src=f"data:image/png;base64,{roadmap_base64}",
                    style={
                        'width': '100%',
                        'maxWidth': '800px',
                        'borderRadius': '15px',
                        'marginTop': '10px',
                        'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
                        'border': '1px solid #e9ecef'
                    }
                ),
                html.Div([
                    html.P("Key Features:", style={'color': '#2c3e50', 'fontWeight': 'bold', 'marginTop': '20px'}),
                    html.Ul([
                        html.Li("Progressive learning path from basics to advanced topics"),
                        html.Li("Clear milestones and checkpoints"),
                        html.Li("Practical projects and hands-on experience"),
                        html.Li("Industry-relevant skills and certifications")
                    ], style={'color': '#34495e', 'marginTop': '10px'})
                ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '10px', 'marginTop': '20px'})
            ], className="chat-message bot-message", style={
                'backgroundColor': '#ffffff',
                'borderRadius': '15px',
                'padding': '20px',
                'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.05)'
            })
        ], className="d-flex justify-content-start mb-3")
        
        return current_messages + [roadmap_message]

    @app.callback(
        Output("chat-messages", "children", allow_duplicate=True),
        [Input({"type": "career-roadmap", "index": ALL}, "n_clicks")],
        [State("chat-messages", "children")],
        prevent_initial_call=True
    )
    def show_career_roadmap(n_clicks, current_messages):
        if not n_clicks:
            return current_messages
        
        ctx = callback_context
        if not ctx.triggered:
            return current_messages
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not button_id:
            return current_messages
        
        # Add user's selection to chat
        current_messages = current_messages or []
        current_messages.append(
            html.Div(
                "I want to explore career roadmaps",
                className="chat-message user-message"
            )
        )
        
        # Create career roadmap options
        career_options = html.Div([
            html.Div([
                html.H4("Career Roadmap Options", className="text-center mb-4", style={'color': '#0d47a1'}),
                
                # Technology Careers
                html.Div([
                    html.Div([
                        html.H5("Technology Careers", className="career-category-title"),
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-code"),
                                "Software Development",
                                html.Div("Build applications and systems", className="option-description")
                            ], className="career-option-btn", id={"type": "tech-career", "index": "software"}),
                            html.Button([
                                html.I(className="fas fa-shield-alt"),
                                "Cybersecurity",
                                html.Div("Protect systems and data", className="option-description")
                            ], className="career-option-btn", id={"type": "tech-career", "index": "cybersecurity"}),
                            html.Button([
                                html.I(className="fas fa-network-wired"),
                                "Network Engineering",
                                html.Div("Design and maintain networks", className="option-description")
                            ], className="career-option-btn", id={"type": "tech-career", "index": "network"}),
                            html.Button([
                                html.I(className="fas fa-robot"),
                                "AI/ML Engineering",
                                html.Div("Develop intelligent systems", className="option-description")
                            ], className="career-option-btn", id={"type": "tech-career", "index": "ai"}),
                        ])
                    ], className="career-category")
                ]),
                
                # Business Careers
                html.Div([
                    html.Div([
                        html.H5("Business Careers", className="career-category-title"),
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-chart-line"),
                                "Business Analytics",
                                html.Div("Analyze business data", className="option-description")
                            ], className="career-option-btn", id={"type": "business-career", "index": "analytics"}),
                            html.Button([
                                html.I(className="fas fa-handshake"),
                                "Business Management",
                                html.Div("Lead and manage organizations", className="option-description")
                            ], className="career-option-btn", id={"type": "business-career", "index": "management"}),
                            html.Button([
                                html.I(className="fas fa-bullhorn"),
                                "Marketing",
                                html.Div("Promote products and services", className="option-description")
                            ], className="career-option-btn", id={"type": "business-career", "index": "marketing"}),
                            html.Button([
                                html.I(className="fas fa-file-invoice-dollar"),
                                "Finance",
                                html.Div("Manage financial resources", className="option-description")
                            ], className="career-option-btn", id={"type": "business-career", "index": "finance"}),
                        ])
                    ], className="career-category")
                ]),
                
                # Creative Careers
                html.Div([
                    html.Div([
                        html.H5("Creative Careers", className="career-category-title"),
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-palette"),
                                "Graphic Design",
                                html.Div("Create visual content", className="option-description")
                            ], className="career-option-btn", id={"type": "creative-career", "index": "design"}),
                            html.Button([
                                html.I(className="fas fa-video"),
                                "Digital Media",
                                html.Div("Produce digital content", className="option-description")
                            ], className="career-option-btn", id={"type": "creative-career", "index": "media"}),
                            html.Button([
                                html.I(className="fas fa-camera"),
                                "Photography",
                                html.Div("Capture and edit images", className="option-description")
                            ], className="career-option-btn", id={"type": "creative-career", "index": "photography"}),
                            html.Button([
                                html.I(className="fas fa-pen-fancy"),
                                "Content Writing",
                                html.Div("Create written content", className="option-description")
                            ], className="career-option-btn", id={"type": "creative-career", "index": "writing"}),
                        ])
                    ], className="career-category")
                ]),
                
                # Healthcare Careers
                html.Div([
                    html.Div([
                        html.H5("Healthcare Careers", className="career-category-title"),
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-user-md"),
                                "Medical Practice",
                                html.Div("Provide medical care", className="option-description")
                            ], className="career-option-btn", id={"type": "healthcare-career", "index": "medical"}),
                            html.Button([
                                html.I(className="fas fa-heartbeat"),
                                "Nursing",
                                html.Div("Patient care and support", className="option-description")
                            ], className="career-option-btn", id={"type": "healthcare-career", "index": "nursing"}),
                            html.Button([
                                html.I(className="fas fa-pills"),
                                "Pharmacy",
                                html.Div("Medication management", className="option-description")
                            ], className="career-option-btn", id={"type": "healthcare-career", "index": "pharmacy"}),
                            html.Button([
                                html.I(className="fas fa-brain"),
                                "Mental Health",
                                html.Div("Psychological support", className="option-description")
                            ], className="career-option-btn", id={"type": "healthcare-career", "index": "mental"}),
                        ])
                    ], className="career-category")
                ])
            ], className="career-roadmap-container")
        ])
        
        # Add bot response with options
        current_messages.append(
            html.Div([
                html.Div(
                    "I'll help you explore different career paths. Please select a career category and specific role to view its roadmap.",
                    className="chat-message bot-message"
                ),
                career_options
            ])
        )
        
        return current_messages

    @app.callback(
        Output("chat-messages", "children", allow_duplicate=True),
        [Input({"type": "tech-career", "index": ALL}, "n_clicks"),
         Input({"type": "business-career", "index": ALL}, "n_clicks"),
         Input({"type": "creative-career", "index": ALL}, "n_clicks"),
         Input({"type": "healthcare-career", "index": ALL}, "n_clicks")],
        [State("chat-messages", "children")],
        prevent_initial_call=True
    )
    def show_career_details(tech_clicks, business_clicks, creative_clicks, healthcare_clicks, current_messages):
        ctx = callback_context
        if not ctx.triggered:
            return current_messages
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not button_id:
            return current_messages
        
        # Get the career type and specific role
        career_type = button_id.split("-")[0]  # tech, business, creative, or healthcare
        role_index = ctx.triggered[0]["value"]
        
        # Define career roadmaps
        roadmaps = {
            "tech": {
                "software": {
                    "title": "Software Development Career Roadmap",
                    "stages": [
                        {
                            "title": "Foundation (0-6 months)",
                            "items": [
                                "Learn programming basics (Python, Java, or JavaScript)",
                                "Understand data structures and algorithms",
                                "Learn version control (Git)",
                                "Basic web development (HTML, CSS, JavaScript)"
                            ]
                        },
                        {
                            "title": "Building Skills (6-12 months)",
                            "items": [
                                "Advanced programming concepts",
                                "Database management",
                                "API development",
                                "Testing and debugging"
                            ]
                        },
                        {
                            "title": "Specialization (1-2 years)",
                            "items": [
                                "Choose a specialization (Frontend/Backend/Full-stack)",
                                "Learn frameworks (React, Node.js, Django)",
                                "Cloud platforms (AWS, Azure, GCP)",
                                "DevOps practices"
                            ]
                        },
                        {
                            "title": "Advanced Level (2+ years)",
                            "items": [
                                "System architecture",
                                "Microservices",
                                "Security best practices",
                                "Team leadership"
                            ]
                        }
                    ]
                },
                "cybersecurity": {
                    "title": "Cybersecurity Career Roadmap",
                    "stages": [
                        {
                            "title": "Foundation (0-6 months)",
                            "items": [
                                "Networking basics",
                                "Operating systems",
                                "Programming fundamentals",
                                "Security concepts"
                            ]
                        },
                        {
                            "title": "Building Skills (6-12 months)",
                            "items": [
                                "Network security",
                                "System security",
                                "Cryptography basics",
                                "Security tools"
                            ]
                        },
                        {
                            "title": "Specialization (1-2 years)",
                            "items": [
                                "Penetration testing",
                                "Security analysis",
                                "Incident response",
                                "Security frameworks"
                            ]
                        },
                        {
                            "title": "Advanced Level (2+ years)",
                            "items": [
                                "Security architecture",
                                "Threat intelligence",
                                "Security management",
                                "Team leadership"
                            ]
                        }
                    ]
                }
            },
            "business": {
                "analytics": {
                    "title": "Business Analytics Career Roadmap",
                    "stages": [
                        {
                            "title": "Foundation (0-6 months)",
                            "items": [
                                "Statistics and mathematics",
                                "Data analysis basics",
                                "Excel and SQL",
                                "Business fundamentals"
                            ]
                        },
                        {
                            "title": "Building Skills (6-12 months)",
                            "items": [
                                "Data visualization",
                                "Statistical analysis",
                                "Business intelligence tools",
                                "Data cleaning"
                            ]
                        },
                        {
                            "title": "Specialization (1-2 years)",
                            "items": [
                                "Advanced analytics",
                                "Machine learning basics",
                                "Business reporting",
                                "Project management"
                            ]
                        },
                        {
                            "title": "Advanced Level (2+ years)",
                            "items": [
                                "Predictive analytics",
                                "Business strategy",
                                "Team management",
                                "Stakeholder communication"
                            ]
                        }
                    ]
                }
            }
        }
        
        # Get the roadmap for the selected career
        roadmap = roadmaps.get(career_type, {}).get(role_index)
        if not roadmap:
            roadmap = {
                "title": f"{career_type.title()} Career Roadmap",
                "stages": [
                    {
                        "title": "Foundation (0-6 months)",
                        "items": [
                            "Basic knowledge and skills",
                            "Industry fundamentals",
                            "Essential tools and technologies",
                            "Professional development"
                        ]
                    },
                    {
                        "title": "Building Skills (6-12 months)",
                        "items": [
                            "Advanced concepts",
                            "Practical experience",
                            "Industry best practices",
                            "Professional networking"
                        ]
                    },
                    {
                        "title": "Specialization (1-2 years)",
                        "items": [
                            "Area specialization",
                            "Advanced tools",
                            "Project experience",
                            "Leadership skills"
                        ]
                    },
                    {
                        "title": "Advanced Level (2+ years)",
                        "items": [
                            "Expert knowledge",
                            "Strategic thinking",
                            "Team management",
                            "Industry influence"
                        ]
                    }
                ]
            }
        
        # Create roadmap visualization
        roadmap_html = html.Div([
            html.H4(roadmap["title"], className="text-center mb-4", style={'color': '#0d47a1'}),
            html.Div([
                html.Div([
                    html.H5(stage["title"], className="stage-title"),
                    html.Ul([
                        html.Li(item, className="stage-item")
                        for item in stage["items"]
                    ], className="stage-list")
                ], className="roadmap-stage")
                for stage in roadmap["stages"]
            ], className="roadmap-container")
        ], className="roadmap-visualization")
        
        # Add the roadmap to chat
        current_messages.append(
            html.Div([
                html.Div(
                    f"Here's the career roadmap for {roadmap['title']}:",
                    className="chat-message bot-message"
                ),
                roadmap_html
            ])
        )
        
        return current_messages

    # Update the CSS styles
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>USDH</title>
            {%favicon%}
            {%css%}
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                /* Modern Color Scheme */
                :root {
                    --primary: #3498db;
                    --primary-dark: #2980b9;
                    --secondary: #2ecc71;
                    --secondary-dark: #27ae60;
                    --text-dark: #2c3e50;
                    --text-light: #ffffff;
                    --background: #f8f9fa;
                    --border: #e9ecef;
                }

                /* Enhanced Animations */
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px) scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }

                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                @keyframes pulse {
                    0% {
                        transform: scale(1);
                        box-shadow: 0 5px 20px rgba(52, 152, 219, 0.4);
                    }
                    50% {
                        transform: scale(1.05);
                        box-shadow: 0 8px 25px rgba(52, 152, 219, 0.6);
                    }
                    100% {
                        transform: scale(1);
                        box-shadow: 0 5px 20px rgba(52, 152, 219, 0.4);
                    }
                }

                @keyframes glow {
                    from {
                        text-shadow: 0 0 5px var(--secondary),
                                   0 0 10px var(--secondary);
                    }
                    to {
                        text-shadow: 0 0 10px var(--secondary),
                                   0 0 20px var(--secondary);
                    }
                }

                @keyframes shimmer {
                    0% {
                        background-position: -1000px 0;
                    }
                    100% {
                        background-position: 1000px 0;
                    }
                }

                /* Enhanced Chat Messages */
                .chat-message {
                    max-width: 80%;
                    padding: 15px 20px;
                    border-radius: 20px;
                    margin: 12px 0;
                    font-size: 15px;
                    line-height: 1.5;
                    position: relative;
                    animation: slideIn 0.4s ease;
                    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
                    transition: all 0.3s ease;
                }

                .chat-message:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
                }

                .user-message {
                    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                    color: var(--text-light);
                    margin-left: auto;
                    border-bottom-right-radius: 5px;
                }

                .bot-message {
                    background: linear-gradient(135deg, var(--background), #e9ecef);
                    color: var(--text-dark);
                    border-bottom-left-radius: 5px;
                }

                /* Enhanced Chat Container */
                .chat-messages {
                    background: linear-gradient(to bottom, #ffffff, var(--background));
                    border-radius: 20px;
                    padding: 25px;
                    border: none;
                    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
                }

                /* Enhanced Chat Options */
                .chat-option-btn {
                    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                    border: none;
                    color: var(--text-light);
                    transition: all 0.4s ease;
                    border-radius: 15px;
                    padding: 12px 20px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    position: relative;
                    overflow: hidden;
                }

                .chat-option-btn::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(
                        90deg,
                        transparent,
                        rgba(255, 255, 255, 0.2),
                        transparent
                    );
                    transition: 0.5s;
                }

                .chat-option-btn:hover::before {
                    left: 100%;
                }

                .chat-option-btn:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 7px 15px rgba(52, 152, 219, 0.3);
                }

                /* Enhanced Modal */
                .cyber-modal {
                    background: linear-gradient(to bottom right, #ffffff, var(--background));
                    border: none;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
                    border-radius: 25px;
                    overflow: hidden;
                }

                .modal-header {
                    background: linear-gradient(135deg, #ffffff, var(--background));
                    border-bottom: 2px solid var(--border);
                    padding: 20px 25px;
                }

                .modal-body {
                    background: #ffffff;
                    padding: 25px;
                }

                .modal-footer {
                    background: linear-gradient(135deg, #ffffff, var(--background));
                    border-top: 2px solid var(--border);
                    padding: 20px 25px;
                }

                /* Enhanced Options Container */
                .options-container {
                    background: linear-gradient(to bottom right, #ffffff, var(--background));
                    border-radius: 20px;
                    padding: 25px;
                    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
                }

                /* Enhanced Chat Button */
                .chat-button {
                    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                    border: none;
                    width: 65px !important;
                    height: 65px !important;
                    border-radius: 50% !important;
                    box-shadow: 0 5px 20px rgba(52, 152, 219, 0.4);
                    transition: all 0.4s ease;
                    animation: pulse 2s infinite;
                }

                .chat-button:hover {
                    transform: scale(1.1) rotate(10deg);
                    box-shadow: 0 8px 25px rgba(52, 152, 219, 0.6);
                }

                /* Enhanced Scrollbar */
                ::-webkit-scrollbar {
                    width: 8px;
                }

                ::-webkit-scrollbar-track {
                    background: var(--background);
                    border-radius: 10px;
                }

                ::-webkit-scrollbar-thumb {
                    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                    border-radius: 10px;
                    border: 2px solid var(--background);
                }

                ::-webkit-scrollbar-thumb:hover {
                    background: linear-gradient(135deg, var(--primary-dark), var(--primary));
                }

                /* Enhanced Status Indicator */
                .status-indicator {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    animation: fadeIn 0.5s ease;
                }

                .status-indicator::before {
                    content: '';
                    width: 8px;
                    height: 8px;
                    background-color: var(--secondary);
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                /* Enhanced Typography */
                h1, h2, h3, h4, h5, h6 {
                    color: var(--text-dark);
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }

                /* Enhanced Buttons */
                .btn {
                    border: none;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }

                .btn::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(
                        90deg,
                        transparent,
                        rgba(255, 255, 255, 0.2),
                        transparent
                    );
                    transition: 0.5s;
                }

                .btn:hover::before {
                    left: 100%;
                }

                /* Enhanced Cards */
                .card {
                    border: none;
                    border-radius: 20px;
                    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
                    transition: all 0.4s ease;
                    background: linear-gradient(135deg, #ffffff, var(--background));
                }

                .card:hover {
                    transform: translateY(-8px);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
                }

                /* Enhanced Tables */
                .table-container {
                    background: linear-gradient(135deg, #ffffff, var(--background));
                    border-radius: 20px;
                    padding: 25px;
                    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
                }

                .table {
                    border-radius: 15px;
                    overflow: hidden;
                }

                .table thead th {
                    background: linear-gradient(135deg, var(--background), #e9ecef);
                    color: var(--text-dark);
                    font-weight: 600;
                    border: none;
                    padding: 15px;
                }

                .table tbody td {
                    padding: 15px;
                    border: none;
                    transition: all 0.3s ease;
                }

                .table tbody tr:hover {
                    background: linear-gradient(135deg, var(--background), #e9ecef);
                    transform: scale(1.01);
                }

                /* Loading Effects */
                .shimmer {
                    background: linear-gradient(
                        90deg,
                        var(--background) 0%,
                        #f0f0f0 50%,
                        var(--background) 100%
                    );
                    background-size: 1000px 100%;
                    animation: shimmer 2s infinite linear;
                }

                /* Responsive Design */
                @media (max-width: 768px) {
                    .chat-message {
                        max-width: 90%;
                    }

                    .chat-button {
                        width: 55px !important;
                        height: 55px !important;
                    }
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

# Helper functions
def load_table_content(table_name, search_query=None):
    """Load content from the database and return formatted HTML table"""
    try:
        conn = sqlite3.connect('data/USDH.db')
        
        # Apply search if provided
        if search_query:
            # Get column names first
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Build search query with proper column name handling
            search_conditions = []
            params = []
            for col in columns:
                # Skip problematic column name in the search
                if col == '_ug/pg':
                    continue
                search_conditions.append(f'"{col}" LIKE ?')
                params.append(f"%{search_query}%")
            
            # Combine conditions with OR
            where_clause = " OR ".join(search_conditions)
            query = f'SELECT * FROM "{table_name}" WHERE {where_clause}'
            
            df = pd.read_sql(query, conn, params=params)
        else:
            # For regular queries, use double quotes around table name
            query = f'SELECT * FROM "{table_name}"'
            df = pd.read_sql(query, conn)
            
        conn.close()
        
        # Use the appropriate formatter based on table name
        if table_name == "ebooks":
            from ebooks_formatter import format_ebooks_table
            return format_ebooks_table(df)
        elif table_name == "courses":
            return format_courses_table(df)
        elif table_name == "courses2":
            return format_courses2_table(df)
        elif table_name == "schemes":
            return format_schemes_table(df)
        else:
            return html.Div([
                html.H3(f"{table_name.capitalize()} Table", className="mb-3"),
                dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
            ])
            
    except Exception as e:
        print(f"Error in load_table_content: {str(e)}")  # Add better error logging
        return html.Div([
            html.H3("Error Loading Data", className="text-danger"),
            html.P(f"Error: {str(e)}")
        ])

def format_courses2_table(df):
    """Format the courses2 table with minimal info and show details button"""
    table_header = [
        html.Thead(
            html.Tr([
                html.Th("Subject"), 
                html.Th("Grade"),
                html.Th("Action")
            ])
        )
    ]
    
    rows = []
    for i, row in df.iterrows():
        rows.append(html.Tr([
            html.Td(row['subjects']),
            html.Td(row['grade']),
            html.Td(
                dbc.Button("Show Details", 
                          href=row['video_link'],  # Open link directly
                          target="_blank",  # Open in new tab
                          color="primary",
                          size="sm")
            )
        ]))
    
    table_body = [html.Tbody(rows)]
    
    return html.Div([
        html.H3("School Courses (Grades 1-12)", className="mb-3"),
        html.P(f"Showing {len(df)} educational resources", className="text-muted mb-3"),
        dbc.Table(table_header + table_body, 
                 bordered=True, 
                 hover=True, 
                 responsive=True, 
                 striped=True,
                 className="align-middle")
    ])

def format_schemes_table(df):
    """Format the schemes table with interactive elements"""
    cards = []
    for i, row in df.iterrows():
        card = dbc.Card([
            dbc.CardHeader(html.H5(row['name'], className="scheme-title")),
            dbc.CardBody([
                html.H6("Benefits:", className="card-subtitle mb-2 text-muted"),
                html.P(row['benefits'], className="card-text"),
                html.H6("Eligibility Criteria:", className="card-subtitle mb-2 text-muted mt-3"),
                html.P(row['eligiblity_criteria'], className="card-text"),
                html.A("More Information", href=row['for_more_info'], target="_blank", 
                       className="btn btn-primary mt-3")
            ])
        ], className="mb-4 scheme-card")
        cards.append(card)
    
    return html.Div([
        html.H3("Educational Schemes and Benefits", className="mb-3"),
        html.P(f"Showing {len(df)} schemes", className="text-muted mb-3"),
        html.Div(cards)
    ])

def get_filter_dropdowns(table_name):
    """Create filter dropdowns based on table columns"""
    try:
        conn = sqlite3.connect('data/USDH.db')
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        filters = []
        
        if table_name == "courses2":
            # Filters for school courses
            subjects = sorted([s for s in df['subjects'].unique() if pd.notna(s)])
            filters.append(
                dbc.Col([
                    html.Label("Filter by Subject:", style={'color': '#0ff', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="subject-filter",
                        options=[{"label": s, "value": s} for s in subjects],
                        placeholder="Select subject",
                        className="mb-2 cyber-dropdown",
                        style={'backgroundColor': '#222', 'color': '#0ff', 'borderColor': '#0ff'}
                    )
                ], width=4)
            )
            
            grades = sorted([g for g in df['grade'].unique() if pd.notna(g)])
            filters.append(
                dbc.Col([
                    html.Label("Filter by Grade:", style={'color': '#0ff', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="grade-filter",
                        options=[{"label": g, "value": g} for g in grades],
                        placeholder="Select grade",
                        className="mb-2 cyber-dropdown",
                        style={'backgroundColor': '#222', 'color': '#0ff', 'borderColor': '#0ff'}
                    )
                ], width=4)
            )
        
        elif table_name == "courses":
            # Filters for UG/PG courses
            disciplines = sorted([d for d in df['dispcipline'].unique() if pd.notna(d)])
            filters.append(
                dbc.Col([
                    html.Label("Filter by Discipline:", style={'color': '#0ff', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="discipline-filter",
                        options=[{"label": d, "value": d} for d in disciplines],
                        placeholder="Select discipline",
                        className="mb-2 cyber-dropdown",
                        style={'backgroundColor': '#222', 'color': '#0ff', 'borderColor': '#0ff'}
                    )
                ], width=6)
            )
            
            # Add website filter
            websites = sorted([w for w in df['website_name'].unique() if pd.notna(w)])
            filters.append(
                dbc.Col([
                    html.Label("Filter by Website:", style={'color': '#0ff', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="website-filter",
                        options=[{"label": w, "value": w} for w in websites],
                        placeholder="Select website",
                        className="mb-2 cyber-dropdown",
                        style={'backgroundColor': '#222', 'color': '#0ff', 'borderColor': '#0ff'}
                    )
                ], width=6)
            )
        
        elif table_name == "ebooks":
            # Filters for e-books
            subjects = sorted([s for s in df['subject'].unique() if pd.notna(s)])
            filters.append(
                dbc.Col([
                    html.Label("Filter by Subject:", style={'color': '#0ff', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="ebook-subject-filter",
                        options=[{"label": s, "value": s} for s in subjects],
                        placeholder="Select subject",
                        className="mb-2 cyber-dropdown",
                        style={'backgroundColor': '#222', 'color': '#0ff', 'borderColor': '#0ff'}
                    )
                ], width=4)
            )
            
            states = sorted([st for st in df['states'].unique() if pd.notna(st)])
            filters.append(
                dbc.Col([
                    html.Label("Filter by State:", style={'color': '#0ff', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="ebook-state-filter",
                        options=[{"label": st, "value": st} for st in states],
                        placeholder="Select state",
                        className="mb-2 cyber-dropdown",
                        style={'backgroundColor': '#222', 'color': '#0ff', 'borderColor': '#0ff'}
                    )
                ], width=4)
            )
        
        return dbc.Row(filters, className="filter-row") if filters else []
        
    except Exception as e:
        print(f"Error creating filters: {e}")
        return []

def get_chatbot_responses():
    """Get predefined chatbot responses"""
    return {
        "greetings": [
            "Hello! How can I help you today?",
            "Hi there! What would you like to know?",
            "Welcome! I'm here to assist you."
        ],
        "farewells": [
            "Goodbye! Have a great day!",
            "See you later!",
            "Take care!"
        ],
        "navigation": {
            "ebooks": "I can help you access the E-Books section. Just click the 'E-Books' button in the navigation bar.",
            "courses": "You can find UG/PG courses by clicking the 'Courses' button.",
            "school": "School courses are available under the 'School Courses' button.",
            "schemes": "Educational schemes can be found by clicking the 'Schemes' button.",
            "resume": "To create your resume, click the 'Resume Maker' button.",
            "space": "Access your personal space by clicking 'My Space'.",
            "study": "Create and manage your study plans by clicking the 'Study Plan' button."
        },
        "course_selection": {
            "intro": "Let's help you select a course! Here are some popular options:",
            "options": [
                "1. Computer Science & Engineering",
                "2. Data Science & Analytics",
                "3. Business Administration",
                "4. Digital Marketing",
                "5. Web Development",
                "6. Mobile App Development",
                "7. Artificial Intelligence",
                "8. Cybersecurity"
            ]
        },
        "hobbies": {
            "intro": "Great! Let's explore some hobbies that can enhance your skills:",
            "options": [
                "1. Programming & Coding",
                "2. Digital Art & Design",
                "3. Photography",
                "4. Writing & Blogging",
                "5. Music Production",
                "6. Video Editing",
                "7. Language Learning",
                "8. Game Development"
            ]
        },
        "roadmaps": {
            "intro": "Here are some learning roadmaps based on your interests:",
            "options": {
                "programming": [
                    "1. Start with Python basics",
                    "2. Learn data structures and algorithms",
                    "3. Choose a specialization (Web/App/AI)",
                    "4. Build projects and portfolio",
                    "5. Learn version control (Git)",
                    "6. Practice coding challenges"
                ],
                "design": [
                    "1. Learn design fundamentals",
                    "2. Master design tools (Figma/Adobe)",
                    "3. Study color theory and typography",
                    "4. Create portfolio projects",
                    "5. Learn UI/UX principles",
                    "6. Practice design systems"
                ],
                "marketing": [
                    "1. Learn marketing fundamentals",
                    "2. Master social media marketing",
                    "3. Study content creation",
                    "4. Learn SEO basics",
                    "5. Understand analytics",
                    "6. Create marketing campaigns"
                ]
            }
        },
        "help": [
            "I can help you with:\n- Navigating to different sections\n- Finding educational resources\n- Creating study plans\n- Making resumes\n- Accessing your personal space\n- Course selection\n- Hobby exploration\n- Learning roadmaps\n\nWhat would you like to know more about?",
            "Here's what I can do:\n- Guide you to various sections\n- Help you find study materials\n- Assist with study planning\n- Help with resume creation\n- Manage your personal space\n- Course guidance\n- Hobby suggestions\n- Learning paths\n\nHow can I assist you?",
            "I'm here to help you with:\n- Navigation between sections\n- Educational resources\n- Study planning\n- Resume building\n- Personal space management\n- Course selection\n- Hobby discovery\n- Learning roadmaps\n\nWhat would you like help with?"
        ],
        "unknown": [
            "I'm not sure about that. Could you please rephrase your question?",
            "I don't understand that. Could you try asking in a different way?",
            "I'm not sure how to help with that. Would you like to know about the available features?"
        ]
    }

def create_roadmap_image(course_name):
    """Create a course roadmap visualization"""
    plt.figure(figsize=(12, 8))
    
    # Split course name to get type and actual name
    course_type, actual_name = course_name.split('_', 1)
    
    try:
        if course_type == "School":
            # Get school course details
            conn = sqlite3.connect('data/USDH.db')
            df = pd.read_sql("SELECT * FROM courses2 WHERE subjects = ?", conn, params=(actual_name,))
            conn.close()
            
            if df.empty:
                return None
                
            # Define school course stages based on grade levels
            stages = [
                ("Foundation (Grades 1-5)", [
                    "Basic Concepts",
                    "Fundamental Skills",
                    "Core Topics",
                    "Basic Applications"
                ]),
                ("Intermediate (Grades 6-8)", [
                    "Advanced Topics",
                    "Problem Solving",
                    "Practical Applications",
                    "Critical Thinking"
                ]),
                ("Advanced (Grades 9-10)", [
                    "Complex Concepts",
                    "Advanced Applications",
                    "Project Work",
                    "Research Skills"
                ]),
                ("Senior Level (Grades 11-12)", [
                    "Specialized Topics",
                    "Advanced Problem Solving",
                    "Research Projects",
                    "Exam Preparation"
                ]),
                ("Mastery", [
                    "Comprehensive Review",
                    "Practice Tests",
                    "Performance Analysis",
                    "Career Guidance"
                ])
            ]
        else:
            # Get UG/PG course details
            conn = sqlite3.connect('data/USDH.db')
            df = pd.read_sql("SELECT * FROM courses WHERE course_name_ = ?", conn, params=(actual_name,))
            conn.close()
            
            if df.empty:
                return None
                
            # Define roadmap stages based on course type
            roadmap_data = {
                "Computer Science": [
                    ("Fundamentals", ["Programming Basics", "Data Structures", "Algorithms"]),
                    ("Core Concepts", ["OOP", "Database", "Networking"]),
                    ("Advanced Topics", ["Web Dev", "AI/ML", "Cloud Computing"]),
                    ("Specialization", ["Full Stack", "Data Science", "Cybersecurity"]),
                    ("Career Ready", ["Projects", "Internships", "Industry Skills"])
                ],
                "Data Science": [
                    ("Foundation", ["Statistics", "Programming", "Math"]),
                    ("Tools & Tech", ["Python", "SQL", "Data Viz"]),
                    ("Core Skills", ["Data Analysis", "ML Basics", "Big Data"]),
                    ("Advanced", ["Deep Learning", "NLP", "Computer Vision"]),
                    ("Expertise", ["Projects", "Kaggle", "Research"])
                ],
                "Digital Marketing": [
                    ("Basics", ["Marketing 101", "Digital Foundations", "Analytics"]),
                    ("Channels", ["Social Media", "Email", "SEO"]),
                    ("Strategy", ["Content Marketing", "PPC", "Brand Building"]),
                    ("Advanced", ["Marketing Tech", "Automation", "CRM"]),
                    ("Professional", ["Campaigns", "Portfolio", "Certification"])
                ]
            }
            
            # Determine course type based on name
            course_type = "Computer Science"  # Default
            if "data" in actual_name.lower() or "analytics" in actual_name.lower():
                course_type = "Data Science"
            elif "marketing" in actual_name.lower() or "business" in actual_name.lower():
                course_type = "Digital Marketing"
            
            stages = roadmap_data.get(course_type, roadmap_data["Computer Science"])
        
        # Create coordinates for the roadmap
        num_stages = len(stages)
        y_positions = np.linspace(0, 10, num_stages)
        
        # Set style with a modern dark theme
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        # Define colors
        primary_color = '#3498db'  # Blue
        secondary_color = '#2ecc71'  # Green
        accent_color = '#e74c3c'  # Red
        text_color = '#ecf0f1'  # Light gray
        
        # Add gradient background
        gradient = np.linspace(0, 1, 100).reshape(10, 10)
        ax.imshow(gradient, extent=[-2, 4, -1, 11], aspect='auto', cmap='Blues', alpha=0.1)
        
        # Plot stages with enhanced styling
        for idx, (stage, topics) in enumerate(stages):
            # Main stage node with glow effect
            ax.scatter(0, y_positions[idx], s=400, c=primary_color, zorder=5, alpha=0.8)
            ax.scatter(0, y_positions[idx], s=300, c=primary_color, zorder=6)
            
            # Stage text with shadow effect
            ax.text(0.5, y_positions[idx], stage, fontsize=14, color=text_color,
                    verticalalignment='center', fontweight='bold',
                    bbox=dict(facecolor='#2c3e50', alpha=0.7, edgecolor='none', pad=5),
                    zorder=7)
            
            # Topics for each stage with enhanced styling
            for i, topic in enumerate(topics):
                topic_x = 2
                topic_y = y_positions[idx] + (i - len(topics)/2 + 0.5) * 0.4
                
                # Topic node with gradient effect
                ax.scatter(topic_x, topic_y, s=250, c=secondary_color, alpha=0.8, zorder=5)
                ax.scatter(topic_x, topic_y, s=200, c=secondary_color, zorder=6)
                
                # Topic text with modern styling
                ax.text(topic_x + 0.5, topic_y, topic, fontsize=11, color=text_color,
                        verticalalignment='center',
                        bbox=dict(facecolor='#34495e', alpha=0.7, edgecolor='none', pad=3),
                        zorder=7)
                
                # Connect topic to stage with animated line
                ax.plot([0.3, topic_x-0.2], [y_positions[idx], topic_y],
                       c=primary_color, alpha=0.4, linestyle='--', linewidth=2)
        
        # Connect main stages with gradient lines
        for i in range(num_stages-1):
            ax.plot([0, 0], [y_positions[i], y_positions[i+1]],
                    c=primary_color, linewidth=3, alpha=0.6)
        
        # Add decorative elements
        ax.grid(True, linestyle='--', alpha=0.1)
        
        # Add decorative circles in the background
        for i in range(5):
            circle = plt.Circle((0, y_positions[i]), 0.5, color=primary_color, alpha=0.1)
            ax.add_artist(circle)
        
        # Customize appearance
        ax.set_title(f'{actual_name} Learning Roadmap', 
                     color=text_color, pad=20, fontsize=16, fontweight='bold',
                     bbox=dict(facecolor='#2c3e50', alpha=0.7, edgecolor='none', pad=10))
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Add a subtle border
        ax.add_patch(plt.Rectangle((-2, -1), 6, 12, fill=False, color=primary_color, alpha=0.3, linewidth=2))
        
        # Add decorative elements
        for i in range(3):
            x = np.random.uniform(-1.5, 3.5)
            y = np.random.uniform(0, 9)
            size = np.random.uniform(50, 150)
            ax.scatter(x, y, s=size, c=accent_color, alpha=0.1, zorder=0)
        
        # Save to base64 with high DPI and transparent background
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', 
                    facecolor=fig.get_facecolor(), transparent=True, dpi=300)
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
        
    except Exception as e:
        print(f"Error creating roadmap: {e}")
        return None

# Update the chatbot modal layout
def create_chatbot_modal():
    return dbc.Modal([
        dbc.ModalHeader([
            html.Div([
                html.Div([
                    html.I(className="fas fa-robot me-2", style={
                        'color': '#3498db',
                        'fontSize': '32px',
                        'textShadow': '0 0 10px rgba(52, 152, 219, 0.5)',
                        'animation': 'pulse 2s infinite'
                    }),
                    html.H4("USDH Assistant", className="mb-0", style={
                        'color': '#2c3e50',
                        'fontSize': '28px',
                        'fontWeight': 'bold',
                        'letterSpacing': '0.5px'
                    }),
                    html.Div([
                        html.Span("●", style={
                            'color': '#2ecc71',
                            'marginRight': '5px',
                            'animation': 'glow 1.5s ease-in-out infinite alternate'
                        }),
                        "Online"
                    ], className="status-indicator")
                ], className="d-flex align-items-center")
            ], className="d-flex align-items-center justify-content-between w-100")
        ], style={
            'backgroundColor': '#ffffff',
            'borderBottom': '2px solid #e9ecef',
            'padding': '20px 25px'
        }),
        dbc.ModalBody([
            html.Div([
                # Chat messages container
                html.Div(id="chat-messages", className="chat-messages mb-4"),
                
                # Options container
                html.Div([
                    html.Div([
                        html.H5("How can I assist you today?", className="text-center mb-4"),
                        html.Div(className="divider")
                    ]),
                    
                    # Options grid
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                [html.I(className="fas fa-route me-2"), "Course Roadmap"],
                                id="chat-roadmap-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-briefcase me-2"), "Career Roadmap"],
                                id="chat-career-roadmap-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Button(
                                [html.I(className="fas fa-lightbulb me-2"), "Career Guidance"],
                                id="chat-career-guidance-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-question-circle me-2"), "Help"],
                                id="chat-help-option",
                                className="w-100 mb-3 chat-option-btn",
                                style={
                                    'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                                    'border': 'none',
                                    'padding': '12px 20px',
                                    'borderRadius': '12px',
                                    'fontWeight': '600',
                                    'letterSpacing': '0.5px',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)'
                                }
                            )
                        ], width=6)
                    ])
                ], className="options-container")
            ])
        ], style={'backgroundColor': '#ffffff', 'padding': '25px'}),
        dbc.ModalFooter([
            dbc.Button(
                "Close Chat",
                id="close-chatbot-btn",
                className="ms-auto"
            )
        ], style={
            'backgroundColor': '#ffffff',
            'borderTop': '2px solid #e9ecef',
            'padding': '20px 25px'
        })
    ], id="chatbot-modal", is_open=False, backdrop="static", keyboard=False,
       size="lg", contentClassName="cyber-modal")

def init_course_progress_db():
    """Initialize the course progress tracking table"""
    try:
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Create course_progress table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            status TEXT NOT NULL,  -- 'ongoing' or 'completed'
            start_date TEXT,
            completion_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, course_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing course progress table: {e}")

# Call this function when the app starts
init_course_progress_db()

