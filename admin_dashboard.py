from dash import html, dcc, dash_table, dash, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
from flask import session as flask_session
from login import app, login_layout
from manage_courses import manage_courses_layout
from manage_resources import manage_resources_layout
from manage_schemes import manage_schemes_layout

def admin_dashboard():
    layout = html.Div([
        dcc.Store(id='session', storage_type='session'),
        
        # Background elements
        html.Div(className="animated-background"),
        html.Div(className="moving-grid"),
        html.Div(className="floating-particles"),
        html.Div(className="edu-pattern-overlay"),
        
        # Educational background elements
        html.Div([
            # Floating educational icons
            html.I(className="fas fa-graduation-cap floating-icon", style={"top": "15%", "left": "10%"}),
            html.I(className="fas fa-book floating-icon", style={"top": "30%", "left": "25%"}),
            html.I(className="fas fa-pencil-alt floating-icon", style={"top": "20%", "right": "20%"}),
            html.I(className="fas fa-calculator floating-icon", style={"top": "60%", "left": "15%"}),
            html.I(className="fas fa-atom floating-icon", style={"top": "45%", "right": "15%"}),
            html.I(className="fas fa-microscope floating-icon", style={"top": "75%", "left": "20%"}),
            html.I(className="fas fa-flask floating-icon", style={"top": "25%", "left": "50%"}),
            html.I(className="fas fa-globe floating-icon", style={"top": "70%", "right": "25%"}),
            html.I(className="fas fa-brain floating-icon", style={"top": "40%", "left": "30%"}),
            html.I(className="fas fa-laptop-code floating-icon", style={"top": "55%", "right": "30%"}),
            # Additional educational icons
            html.I(className="fas fa-chart-line floating-icon", style={"top": "85%", "left": "40%"}),
            html.I(className="fas fa-chart-bar floating-icon", style={"top": "10%", "right": "40%"}),
            html.I(className="fas fa-chart-pie floating-icon", style={"top": "35%", "left": "70%"}),
            html.I(className="fas fa-vial floating-icon", style={"top": "65%", "right": "35%"}),
            html.I(className="fas fa-mortar-pestle floating-icon", style={"top": "45%", "left": "85%"}),
            html.I(className="fas fa-dna floating-icon", style={"top": "25%", "left": "75%"}),
            html.I(className="fas fa-square-root-alt floating-icon", style={"top": "55%", "left": "45%"}),
            html.I(className="fas fa-infinity floating-icon", style={"top": "15%", "right": "15%"}),
            html.I(className="fas fa-superscript floating-icon", style={"top": "75%", "right": "45%"}),
            html.I(className="fas fa-subscript floating-icon", style={"top": "85%", "right": "55%"}),
            
            # Glowing orbs
            html.Div(className="glow-orb", style={"top": "20%", "left": "15%"}),
            html.Div(className="glow-orb", style={"top": "70%", "right": "20%"}),
            html.Div(className="glow-orb", style={"top": "40%", "left": "60%"}),
            html.Div(className="glow-orb", style={"top": "30%", "right": "30%"}),
            html.Div(className="glow-orb", style={"top": "80%", "left": "30%"}),
            
            # Number particles
            html.Span("1", className="number-particle", style={"top": "25%", "left": "10%"}),
            html.Span("2", className="number-particle", style={"top": "15%", "right": "25%"}),
            html.Span("3", className="number-particle", style={"top": "65%", "left": "25%"}),
            html.Span("4", className="number-particle", style={"top": "35%", "right": "15%"}),
            html.Span("5", className="number-particle", style={"top": "55%", "left": "20%"}),
            html.Span("π", className="number-particle", style={"top": "75%", "right": "10%"}),
            html.Span("∞", className="number-particle", style={"top": "45%", "left": "15%"}),
            html.Span("∑", className="number-particle", style={"top": "85%", "right": "20%"}),
            html.Span("∫", className="number-particle", style={"top": "25%", "right": "35%"}),
            html.Span("√", className="number-particle", style={"top": "65%", "right": "25%"}),
            
            # Formula particles
            html.Span("E=mc²", className="formula-particle", style={"top": "20%", "left": "5%"}),
            html.Span("a²+b²=c²", className="formula-particle", style={"top": "60%", "right": "5%"}),
            html.Span("F=ma", className="formula-particle", style={"top": "35%", "left": "70%"}),
            html.Span("eiπ+1=0", className="formula-particle", style={"top": "80%", "right": "30%"}),
            html.Span("PV=nRT", className="formula-particle", style={"top": "45%", "left": "40%"}),
            html.Span("H₂O", className="formula-particle", style={"top": "75%", "left": "60%"}),
            html.Span("CO₂", className="formula-particle", style={"top": "15%", "right": "45%"}),
            html.Span("H₂SO₄", className="formula-particle", style={"top": "55%", "right": "15%"}),
            
            # Binary particles
            html.Span("10011101", className="binary-particle", style={"top": "30%", "right": "40%"}),
            html.Span("01010101", className="binary-particle", style={"top": "70%", "left": "40%"}),
            html.Span("11001010", className="binary-particle", style={"top": "50%", "right": "20%"}),
            html.Span("00110011", className="binary-particle", style={"top": "20%", "left": "80%"}),
            html.Span("10101010", className="binary-particle", style={"top": "80%", "right": "35%"}),
        ], className="education-bg"),

        # Header with Logo and Profile
        html.Div([
            html.Div([
                html.Img(src="/static/images/logo.png", className="logo"),
                html.Div([
                    html.H4("Unified Skill Development Hub", className="text-center mb-3"),
                    html.P([
                        "Admin Dashboard ", 
                        html.Span("•", style={"margin": "0 5px"}),
                        html.Span(id="admin-name", className="admin-name-display")
                    ], className="dashboard-subtitle")
                ])
            ]),
            
            # Profile section with notifications
            html.Div([
                # Profile trigger
                html.Div([
                    html.I(className="fas fa-user-circle"),
                    html.Span(id="admin-username", style={"display": "none"})
                ], id="profile-trigger", className="profile-trigger", n_clicks=0)
            ], className="profile-container"),
        ], className="header-container"),

        # Welcome banner
        html.Div([
            html.H3("Welcome to your Admin Dashboard", className="welcome-title"),
            html.P("Manage your educational platform from a central location", className="welcome-subtitle"),
        ], className="welcome-banner"),

        # Dashboard Cards Container
        html.Div(id="page-content", children=[
            html.Div([
                # Card 1: Course Management
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-book-open"),
                            html.Span("Essential", className="feature-badge")
                        ], className="card-icon-container"),
                        html.H4("Course Management", className="card-title"),
                        html.P([
                            "Create, edit and organize courses for UG/PG and schools. ",
                            html.Br(),
                            "Add instructors, study materials, and set eligibility criteria."
                        ]),
                        html.Div([
                            dbc.Button([
                                "Manage Courses", html.I(className="fas fa-arrow-right ms-2")
                            ], href="/manage-courses", className="cyber-button")
                        ], className="card-footer")
                    ], className="card-content")
                ], className="cyber-card"),
                
                # Card 2: E-Resources
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-laptop-code"),
                            html.Span("Digital", className="feature-badge blue")
                        ], className="card-icon-container"),
                        html.H4("E-Resources", className="card-title"),
                        html.P([
                            "Upload and organize digital learning materials. ",
                            html.Br(),
                            "Manage videos, eBooks, research papers, and interactive content."
                        ]),
                        html.Div([
                            dbc.Button([
                                "Manage Resources", html.I(className="fas fa-arrow-right ms-2")
                            ], href="/manage-resources", className="cyber-button")
                        ], className="card-footer")
                    ], className="card-content")
                ], className="cyber-card"),
                
                # Card 3: Educational Schemes
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-graduation-cap"),
                            html.Span("Programs", className="feature-badge green")
                        ], className="card-icon-container"),
                        html.H4("Educational Schemes", className="card-title"),
                        html.P([
                            "Manage scholarships and educational programs. ",
                            html.Br(),
                            "Configure eligibility requirements and application processes."
                        ]),
                        html.Div([
                            dbc.Button([
                                "Manage Schemes", html.I(className="fas fa-arrow-right ms-2")
                            ], href="/manage-schemes", className="cyber-button")
                        ], className="card-footer")
                    ], className="card-content")
                ], className="cyber-card"),
                
                # Card 4: Analytics
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-line"),
                            html.Span("Insights", className="feature-badge purple")
                        ], className="card-icon-container"),
                        html.H4("Analytics", className="card-title"),
                        html.P([
                            "Access detailed insights and usage statistics. ",
                            html.Br(),
                            "Monitor engagement metrics and generate performance reports."
                        ]),
                        html.Div([
                            dbc.Button([
                                "View Analytics", html.I(className="fas fa-arrow-right ms-2")
                            ], href="/analytics", className="cyber-button")
                        ], className="card-footer")
                    ], className="card-content")
                ], className="cyber-card")
            ], className="dashboard-grid")
        ], className="main-container"),

        # Quick Actions Section
        html.Div([
            html.H4("Quick Actions", className="quick-actions-title"),
            html.Div([
                html.A([
                    html.I(className="fas fa-plus-circle"),
                    html.Span("Add New Course")
                ], href="/manage-courses?action=new", className="quick-action-btn"),
                
                html.A([
                    html.I(className="fas fa-upload"),
                    html.Span("Upload Resource")
                ], href="/manage-resources?action=new", className="quick-action-btn"),
                
                html.A([
                    html.I(className="fas fa-sign-out-alt"),
                    html.Span("Logout")
                ], href="/logout", className="quick-action-btn"),
            ], className="quick-actions-container")
        ], className="quick-actions-section"),

        # Admin Profile Modal
        dbc.Modal([
            dbc.ModalHeader([
                html.I(className="fas fa-user-circle me-2"),
                html.Span("Admin Profile")
            ]),
            dbc.ModalBody([
                # Update Profile Form
                html.Div([
                    html.H5("Update Profile", className="update-profile-header"),
                    
                    # Hidden fields to store current values
                    html.Div([
                        html.Span(id="current-admin-username", className="hidden-field"),
                        html.Span(id="current-admin-email", className="hidden-field"),
                        html.Span(id="current-admin-role", className="hidden-field"),
                        html.Span(id="current-admin-id", className="hidden-field")
                    ]),
                    
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Username", className="form-label"),
                                dbc.Input(id="admin-profile-username", type="text", className="cyber-input mb-3", 
                                        placeholder="Enter new username (or leave unchanged)")
                            ], width=12),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Email", className="form-label"),
                                dbc.Input(id="admin-profile-email", type="email", className="cyber-input mb-3",
                                        placeholder="Enter new email (or leave unchanged)")
                            ], width=12),
                        ]),
                        html.Hr(className="form-divider"),
                        html.P("Password can be updated below (optional):", className="password-update-text"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Current Password", className="form-label"),
                                dbc.Input(id="admin-profile-current-password", type="password", className="cyber-input mb-3",
                                        placeholder="Required for any changes")
                            ], width=12),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("New Password", className="form-label"),
                                dbc.Input(id="admin-profile-new-password", type="password", className="cyber-input mb-3",
                                        placeholder="Leave blank to keep current password")
                            ], width=12),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Confirm New Password", className="form-label"),
                                dbc.Input(id="admin-profile-confirm-password", type="password", className="cyber-input mb-3",
                                        placeholder="Confirm new password")
                            ], width=12),
                        ]),
                        html.Div(id="admin-profile-update-status", className="mt-3")
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Update Profile", id="update-admin-profile-btn", className="cyber-button"),
                dbc.Button("Close", id="close-admin-profile-btn", className="cyber-button ms-2")
            ])
        ], id="admin-profile-modal", className="cyber-modal"),
        
        # Notifications Modal
        dbc.Modal([
            dbc.ModalHeader("Notifications"),
            dbc.ModalBody([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-bell notification-icon-blue"),
                        html.Div([
                            html.H6("New User Registration", className="notification-title"),
                            html.P("A new student has registered for UG courses.", className="notification-text"),
                            html.Span("2 hours ago", className="notification-time")
                        ], className="notification-content")
                    ], className="notification-item"),
                    
                    html.Div([
                        html.I(className="fas fa-exclamation-circle notification-icon-orange"),
                        html.Div([
                            html.H6("System Update Required", className="notification-title"),
                            html.P("New version available for the portal.", className="notification-text"),
                            html.Span("1 day ago", className="notification-time")
                        ], className="notification-content")
                    ], className="notification-item"),
                    
                    html.Div([
                        html.I(className="fas fa-check-circle notification-icon-green"),
                        html.Div([
                            html.H6("Backup Completed", className="notification-title"),
                            html.P("Database backup completed successfully.", className="notification-text"),
                            html.Span("2 days ago", className="notification-time")
                        ], className="notification-content")
                    ], className="notification-item")
                ], className="notifications-container")
            ]),
            dbc.ModalFooter([
                dbc.Button("Mark All as Read", className="cyber-button"),
                dbc.Button("Close", id="close-notifications-btn", className="cyber-button ms-2", n_clicks=0)
            ])
        ], id="notifications-modal", className="cyber-modal")
    ])
    
    return layout

# If this file is the main app entry point, add this code:
if __name__ == '__main__':
    app = dash.Dash(__name__, 
                   external_stylesheets=[
                       '/assets/admin.css',
                       dbc.themes.BOOTSTRAP,
                       'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'
                   ],
                   suppress_callback_exceptions=True)
    
    app.layout = admin_dashboard()
    
    # Add your callbacks here
    
    app.run_server(debug=True)

# Register callbacks for admin dashboard
def register_admin_callbacks(app):
    # Toggle admin profile modal
    @app.callback(
        Output("admin-profile-modal", "is_open"),
        [Input("profile-trigger", "n_clicks"),
         Input("close-admin-profile-btn", "n_clicks"),
         Input("update-admin-profile-btn", "n_clicks")],
        [State("admin-profile-modal", "is_open")]
    )
    def toggle_admin_profile_modal(profile_clicks, close_clicks, update_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if button_id in ["profile-trigger"]:
                return True
            elif button_id in ["close-admin-profile-btn", "update-admin-profile-btn"]:
                return False
            return is_open
    
    # Toggle notifications modal
    @app.callback(
        Output("notifications-modal", "is_open"),
        [Input("notification-icon", "n_clicks"),
         Input("close-notifications-btn", "n_clicks")],
        [State("notifications-modal", "is_open")]
    )
    def toggle_notifications_modal(notification_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if button_id == "notification-icon":
                return True
            elif button_id == "close-notifications-btn":
                return False
            return is_open
            
    # Update admin name display
    @app.callback(
        Output("admin-name", "children"),
        [Input("session", "data")]
    )
    def update_admin_name(session_data):
        if not session_data:
            return "Admin"
        
        username = session_data.get("username", "Admin")
        return username
    
    # Load admin profile data
    @app.callback(
        [Output("current-admin-username", "children"),
         Output("current-admin-email", "children"),
         Output("current-admin-role", "children"),
         Output("current-admin-id", "children"),
         Output("admin-profile-username", "value"),
         Output("admin-profile-email", "value"),
         Output("admin-username", "children")],
        [Input("admin-profile-modal", "is_open")]
    )
    def load_admin_profile(is_open):
        if not is_open:
            return "", "", "", "", "", "", ""
        
        # Get admin ID from session
        admin_id = flask_session.get("admin_id")
        if not admin_id:
            return "Not logged in", "", "", "", "", "", "Admin"
        
        try:
            # Connect to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Fetch admin details
            cursor.execute('''
                SELECT id, username, email, role FROM users
                WHERE id = ? AND role = 'admin'
            ''', (admin_id,))
            
            admin = cursor.fetchone()
            conn.close()
            
            if admin:
                admin_id, username, email, role = admin
                return username, email, role, str(admin_id), username, email, username
            else:
                return "User not found", "", "", "", "", "", "Admin"
                
        except Exception as e:
            print(f"Error loading admin profile: {str(e)}")
            return "Error", "", "", "", "", "", "Admin"
    
    # Update admin profile
    @app.callback(
        Output("admin-profile-update-status", "children"),
        [Input("update-admin-profile-btn", "n_clicks")],
        [State("admin-profile-username", "value"),
         State("admin-profile-email", "value"),
         State("admin-profile-current-password", "value"),
         State("admin-profile-new-password", "value"),
         State("admin-profile-confirm-password", "value"),
         State("current-admin-id", "children")]
    )
    def update_admin_profile(n_clicks, new_username, new_email, current_password, 
                           new_password, confirm_password, admin_id):
        if not n_clicks:
            return ""
        
        # Check if admin is logged in
        if not admin_id:
            return html.Div("Not logged in. Please log in again.", style={"color": "red"})
        
        # Verify current password is provided
        if not current_password:
            return html.Div("Current password is required to make changes.", style={"color": "red"})
        
        try:
            # Connect to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Verify current password
            cursor.execute('SELECT password FROM users WHERE id = ?', (admin_id,))
            stored_password = cursor.fetchone()
            
            if not stored_password or stored_password[0] != current_password:
                conn.close()
                return html.Div("Current password is incorrect", style={"color": "red"})
            
            # Get current values
            cursor.execute('SELECT username, email FROM users WHERE id = ?', (admin_id,))
            current_data = cursor.fetchone()
            current_username, current_email = current_data if current_data else ("", "")
            
            # Prepare updates
            updates = []
            params = []
            status_messages = []
            
            # Username update
            if new_username and new_username != current_username:
                # Check if username already exists
                cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', 
                              (new_username, admin_id))
                if cursor.fetchone():
                    status_messages.append("Username already exists. Please choose another.")
                else:
                    updates.append("username = ?")
                    params.append(new_username)
                    status_messages.append("Username changed successfully!")
                    # Update session
                    flask_session["username"] = new_username
            
            # Email update
            if new_email and new_email != current_email:
                # Basic email validation
                import re
                email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                if not email_pattern.match(new_email):
                    status_messages.append("Please enter a valid email address.")
                else:
                    # Check if email already exists
                    cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', 
                                 (new_email, admin_id))
                    if cursor.fetchone():
                        status_messages.append("Email already in use. Please use a different email.")
                    else:
                        updates.append("email = ?")
                        params.append(new_email)
                        status_messages.append("Email changed successfully!")
                        # Update session if needed
                        if "email" in flask_session:
                            flask_session["email"] = new_email
            
            # Password update
            if new_password:
                if len(new_password) < 6:
                    status_messages.append("New password must be at least 6 characters long.")
                elif new_password != confirm_password:
                    status_messages.append("New passwords do not match.")
                else:
                    updates.append("password = ?")
                    params.append(new_password)
                    status_messages.append("Password changed successfully!")
            
            # Execute update if there are changes
            if updates and not any("already exists" in msg or "valid" in msg or "match" in msg for msg in status_messages):
                query = "UPDATE users SET " + ", ".join(updates) + " WHERE id = ?"
                params.append(admin_id)
                cursor.execute(query, params)
                conn.commit()
                
                result = html.Div([
                    html.P(msg, style={"color": "green" if "successfully" in msg else "red"})
                    for msg in status_messages
                ])
            else:
                # Only error messages or no changes
                if not updates:
                    result = html.Div("No changes to update.", style={"color": "blue"})
                else:
                    result = html.Div([
                        html.P(msg, style={"color": "red"})
                        for msg in status_messages if "successfully" not in msg
                    ])
            
            conn.close()
            return result
            
        except Exception as e:
            print(f"Error updating admin profile: {str(e)}")
            return html.Div(f"Error updating profile: {str(e)}", style={"color": "red"})