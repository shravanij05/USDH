from dash import html, dcc, dash_table, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
from dash import no_update

def manage_courses_layout():
    # Connect to the database
    conn = sqlite3.connect('data/USDH.db')
    # Get UG/PG courses
    ug_pg_courses_df = pd.read_sql_query("SELECT * FROM courses", conn)
    # Get 1-12th courses
    school_courses_df = pd.read_sql_query("SELECT * FROM courses2", conn)
    conn.close()
    
    return html.Div([
        # Main Background
        html.Div([
            # Pattern Overlay
            html.Div(className="edu-pattern-overlay"),
            
            # Glowing Orbs
            html.Div([
                html.Div(className="glow-orb", style={"top": "15%", "left": "10%"}),
                html.Div(className="glow-orb", style={"top": "50%", "left": "80%"}),
                html.Div(className="glow-orb", style={"top": "75%", "left": "30%"}),
            ]),
            
            # Floating educational icons with specific positioning
            html.I(className="fas fa-graduation-cap floating-icon", style={"top": "10%", "left": "5%", "font-size": "2.5rem"}),
            html.I(className="fas fa-book floating-icon", style={"top": "25%", "left": "90%", "font-size": "2rem"}),
            html.I(className="fas fa-pencil-alt floating-icon", style={"top": "40%", "left": "15%", "font-size": "1.8rem"}),
            html.I(className="fas fa-calculator floating-icon", style={"top": "60%", "left": "85%", "font-size": "2.2rem"}),
            html.I(className="fas fa-atom floating-icon", style={"top": "80%", "left": "10%", "font-size": "2.3rem"}),
            html.I(className="fas fa-microscope floating-icon", style={"top": "15%", "left": "75%", "font-size": "2.1rem"}),
            html.I(className="fas fa-flask floating-icon", style={"top": "70%", "left": "60%", "font-size": "1.9rem"}),
            html.I(className="fas fa-dna floating-icon", style={"top": "30%", "left": "40%", "font-size": "2.4rem"}),
            html.I(className="fas fa-brain floating-icon", style={"top": "85%", "left": "80%", "font-size": "2rem"}),
            html.I(className="fas fa-lightbulb floating-icon", style={"top": "45%", "left": "5%", "font-size": "2.2rem"}),
        ], className="education-bg"),
        
        # Content Container - to create proper layout with side padding
        html.Div([
            # Top navigation bar with back and logout buttons
            html.Div([
                html.Button([
                    html.I(className="fas fa-arrow-left me-2"),
                    "Back to Dashboard"
                ], id="back-to-dashboard", className="back-button", n_clicks=0),
                
                html.Button([
                    html.I(className="fas fa-sign-out-alt me-2"),
                    "Logout"
                ], id="logout-button", className="logout-button", n_clicks=0)
            ], className="top-nav"),
            
            # Page header with title and statistics
            html.Div([
                html.Div([
                    html.H2("Course Management", className="mb-2"),
                    html.P("Manage your educational courses across all levels")
                ], className="header-title"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-graduation-cap mb-3", style={"font-size": "2rem", "color": "#1a237e"}),
                            html.H3(f"{len(ug_pg_courses_df)}", className="stat-number"),
                            html.P("UG/PG Courses", className="stat-label")
                        ])
                    ], className="stat-card"),
                    
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-school mb-3", style={"font-size": "2rem", "color": "#1a237e"}),
                            html.H3(f"{len(school_courses_df)}", className="stat-number"),
                            html.P("School Courses", className="stat-label")
                        ])
                    ], className="stat-card")
                ], className="stats-container")
            ], className="page-header"),
            
            # Tabs for different course types
            dbc.Tabs([
                # UG/PG Courses Tab
                dbc.Tab(label="UG/PG Courses", tab_id="ug-pg-tab", children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H4("UG/PG Courses List"),
                                html.P("Manage undergraduate and postgraduate courses")
                            ], className="tab-title"),
                            
                            dbc.Button([
                                html.I(className="fas fa-plus me-2"), 
                                "Add New Course"
                            ], id="add-ug-pg-course-btn", className="add-button", n_clicks=0)
                        ], className="tab-header"),
                        
                        # Course data table
                        html.Div([
                            dash_table.DataTable(
                                id='ug-pg-courses-table',
                                columns=[
                                    {"name": col, "id": col} for col in ug_pg_courses_df.columns
                                ],
                                data=ug_pg_courses_df.to_dict('records'),
                                page_size=10,
                                filter_action="native",
                                sort_action="native",
                                style_table={
                                    'borderRadius': '15px',
                                    'overflow': 'hidden',
                                    'border': '1px solid rgba(26, 35, 126, 0.1)',
                                },
                                style_header={
                                    'backgroundColor': '#1a237e',
                                    'color': 'white',
                                    'fontWeight': 'bold',
                                    'textAlign': 'left',
                                    'padding': '15px',
                                    'fontSize': '14px',
                                },
                                style_cell={
                                    'backgroundColor': 'white',
                                    'color': '#5a5c69',
                                    'border': '1px solid #f8f9fc',
                                    'padding': '15px',
                                    'textAlign': 'left',
                                    'fontFamily': '"Nunito", sans-serif',
                                    'fontSize': '14px',
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f8f9fc'
                                    },
                                    {
                                        'if': {'state': 'selected'},
                                        'backgroundColor': '#eaecf4',
                                        'border': '1px solid #1a237e'
                                    }
                                ],
                                row_selectable="single",
                                selected_rows=[],
                                page_current=0,
                                css=[{"selector": ".dash-spreadsheet tr", "rule": "cursor: pointer"}]
                            )
                        ], className="table-container"),
                        
                        # Action buttons
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-edit me-2"), 
                                "Edit Selected"
                            ], id="edit-ug-pg-course-btn", className="edit-button", n_clicks=0),
                            
                            dbc.Button([
                                html.I(className="fas fa-trash-alt me-2"), 
                                "Delete Selected"
                            ], id="delete-ug-pg-course-btn", className="delete-button", n_clicks=0)
                        ], className="d-flex justify-content-end gap-3 mt-4")
                    ], className="tab-content")
                ]),
                
                # School Courses (1-12th) Tab
                dbc.Tab(label="School Courses (1-12th)", tab_id="school-tab", children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H4("School Courses List"),
                                html.P("Manage grades 1-12 courses")
                            ], className="tab-title"),
                            
                            dbc.Button([
                                html.I(className="fas fa-plus me-2"), 
                                "Add New Course"
                            ], id="add-school-course-btn", className="add-button", n_clicks=0)
                        ], className="tab-header"),
                        
                        # Course data table
                        html.Div([
                            dash_table.DataTable(
                                id='school-courses-table',
                                columns=[
                                    {"name": col, "id": col} for col in school_courses_df.columns
                                ],
                                data=school_courses_df.to_dict('records'),
                                page_size=10,
                                filter_action="native",
                                sort_action="native",
                                style_table={
                                    'borderRadius': '15px',
                                    'overflow': 'hidden',
                                    'border': '1px solid rgba(26, 35, 126, 0.1)',
                                },
                                style_header={
                                    'backgroundColor': '#1a237e',
                                    'color': 'white',
                                    'fontWeight': 'bold',
                                    'textAlign': 'left',
                                    'padding': '15px',
                                    'fontSize': '14px',
                                },
                                style_cell={
                                    'backgroundColor': 'white',
                                    'color': '#5a5c69',
                                    'border': '1px solid #f8f9fc',
                                    'padding': '15px',
                                    'textAlign': 'left',
                                    'fontFamily': '"Nunito", sans-serif',
                                    'fontSize': '14px',
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f8f9fc'
                                    },
                                    {
                                        'if': {'state': 'selected'},
                                        'backgroundColor': '#eaecf4',
                                        'border': '1px solid #1a237e'
                                    }
                                ],
                                row_selectable="single",
                                selected_rows=[],
                                page_current=0,
                                css=[{"selector": ".dash-spreadsheet tr", "rule": "cursor: pointer"}]
                            )
                        ], className="table-container"),
                        
                        # Action buttons
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-edit me-2"), 
                                "Edit Selected"
                            ], id="edit-school-course-btn", className="edit-button", n_clicks=0),
                            
                            dbc.Button([
                                html.I(className="fas fa-trash-alt me-2"), 
                                "Delete Selected"
                            ], id="delete-school-course-btn", className="delete-button", n_clicks=0)
                        ], className="d-flex justify-content-end gap-3 mt-4")
                    ], className="tab-content")
                ]),
            ], id="courses-tabs", active_tab="ug-pg-tab", className="mb-4"),
            
            # Course Modal
            dbc.Modal([
                dbc.ModalHeader([html.H5("Course Details", className="modal-title")]),
                dbc.ModalBody([
                    dbc.Form([
                        html.Div([
                            html.Label("Course Type", className="form-label"),
                            dbc.Select(
                                id="course-type-select",
                                options=[
                                    {"label": "UG/PG Course", "value": "ug-pg"},
                                    {"label": "School Course", "value": "school"}
                                ],
                                className="form-control"
                            )
                        ], className="form-group"),
                        
                        # Core course fields - always shown
                        html.Div([
                            html.Label("Course Name", className="form-label"),
                            dbc.Input(id="course-name-input", placeholder="Enter course name", type="text", className="form-control mb-3"),
                            
                            html.Label("Description", className="form-label"),
                            dbc.Textarea(id="course-description-input", placeholder="Enter course description", className="form-control mb-3", style={"height": "120px"}),
                        ], className="form-group"),
                        
                        # Dynamic fields based on course type
                        html.Div(id="dynamic-course-fields"),
                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Button("Save", id="save-course-btn", className="add-button", n_clicks=0),
                    dbc.Button("Cancel", id="cancel-course-btn", className="delete-button", n_clicks=0),
                ])
            ], id="course-modal", className="course-modal", is_open=False, size="lg"),
            
            # Course deletion confirmation modal
            dbc.Modal([
                dbc.ModalHeader([html.H5("Confirm Deletion", className="modal-title text-danger")]),
                dbc.ModalBody([
                    html.P("Are you sure you want to delete this course? This action cannot be undone."),
                    html.Div(id="course-to-delete-info", className="mt-3 mb-2 p-3 border border-danger rounded")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-delete-btn", className="edit-button", n_clicks=0),
                    dbc.Button("Delete", id="confirm-delete-btn", className="delete-button", n_clicks=0),
                ])
            ], id="delete-confirmation-modal", className="course-modal", is_open=False),
            
            # Notification area
            html.Div(id="course-notification", className="mt-3"),
            
            # Store component to track active tab
            dcc.Store(id="active-course-tab", data="ug-pg-tab"),
            
            # URL for navigation
            dcc.Location(id="url-courses", refresh=True)
        ], className="container-fluid py-4 px-4", style={"maxWidth": "1400px", "margin": "0 auto"})
    ], style={"position": "relative", "minHeight": "100vh", "background": "linear-gradient(135deg, #1a237e, #0d47a1)"})