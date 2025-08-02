import dash
from dash import html, dcc, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import os
from dash.exceptions import PreventUpdate
from flask import session, request, send_file, redirect, url_for
import uuid
import pandas as pd

# Initialize app with session management
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'
    ],
    assets_folder='assets',
    suppress_callback_exceptions=True
)
server = app.server
server.secret_key = 'USDH'  # Keep using the same secret key

# Add custom index string to include additional CSS files
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>USDH</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="/assets/login.css">
        <link rel="stylesheet" href="/assets/admin.css">
        <link rel="stylesheet" href="/assets/manage_courses.css">
        <link rel="stylesheet" href="/assets/manage_resources.css">
        <link rel="stylesheet" href="/assets/manage_schemes.css">
        <link rel="stylesheet" href="/assets/analytics.css">
        <link rel="stylesheet" href="/assets/user_dashboard.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <link rel="stylesheet" href="https://unicons.iconscout.com/release/v2.1.9/css/unicons.css">
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

# Import all modules after app initialization
from user_dashboard import user_dashboard, register_callbacks as register_user_dashboard_callbacks
from view_course import register_callbacks as register_view_course_callbacks
from resume_maker import resume_maker, register_callbacks as register_resume_callbacks
from my_space import my_space, register_callbacks as register_my_space_callbacks
from study_plan import study_plan, register_callbacks as register_study_plan_callbacks
from analytics import analytics_layout, register_callbacks as register_analytics_callbacks
from live import live_layout, init_live_callbacks

# Register all callbacks once
register_user_dashboard_callbacks(app)
register_view_course_callbacks(app)
register_resume_callbacks(app)
register_my_space_callbacks(app)
register_study_plan_callbacks(app)
register_analytics_callbacks(app)
# After initializing your app
init_live_callbacks(app)


# Ensure the database directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize database
def init_db():
    conn = sqlite3.connect('data/USDH.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Create resumes table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        data TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Login/Register Page (Main Page)
def login_layout():
    return html.Div([  
        # Background Elements
        html.Div([
            # Pattern Overlay
            html.Div(className="pattern-overlay"),
            
            # Glowing Orbs
            html.Div([
                html.Div(className="glow-orb"),
                html.Div(className="glow-orb"),
                html.Div(className="glow-orb")
            ]),
            
            # Floating Education Icons
            html.Div([
                html.I(className="fas fa-graduation-cap floating-icon"),
                html.I(className="fas fa-book floating-icon"),
                html.I(className="fas fa-chalkboard-teacher floating-icon"),
                html.I(className="fas fa-microscope floating-icon"),
                html.I(className="fas fa-atom floating-icon"),
                html.I(className="fas fa-flask floating-icon"),
                html.I(className="fas fa-calculator floating-icon"),
                html.I(className="fas fa-pencil-alt floating-icon"),
                html.I(className="fas fa-laptop floating-icon"),
                html.I(className="fas fa-brain floating-icon")
            ], className="education-bg"),
        ]),
        
        # Main Content
        html.Div([
            # Left side - Login Box
            html.Div([
                html.Div([
                    html.Div(html.Img(src="/static/images/logo.png", className="logo"), style={'marginRight': '15px'}),
                    html.H4("Unified Skill Development Hub", className="text-center mb-3", style={
                        'color': '#0d47a1',
                        'text-align': 'center',
                        'font-size': '1.4rem',
                        'margin': '0',
                        'font-weight': '600',
                        'letterSpacing': '0.5px'
                    })
                ], className="header-container"),

                # Toggle Switch with Text
                html.Div([
                    dcc.Input(
                        type="checkbox",
                        id="reg-log",
                        className="checkbox",
                        style={'display': 'none'}
                    ),
                    html.Label([
                        html.Span("LOG IN", className="login-text"),
                        html.Span("SIGN UP", className="signup-text")
                    ], htmlFor="reg-log"),
                    
                    html.Div(className="card-3d-wrap mx-auto", children=[
                        html.Div(className="card-3d-wrapper", children=[
                            # Login Card (Front)
                            html.Div(className="card-front", children=[
                                html.Div(className="center-wrap", children=[
                                    html.Div(className="section text-center", children=[
                                        dcc.Input(id="login-username", placeholder="Username", type="text", className="form-style"),
                                        html.I(className="input-icon uil uil-user"),
                                        dcc.Input(id="login-password", placeholder="Password", type="password", className="form-style mt-4"),
                                        html.I(className="input-icon uil uil-lock-alt"),
                                        dcc.Dropdown(
                                            id='login-role',
                                            options=[
                                                {'label': 'User', 'value': 'user'},
                                                {'label': 'Admin', 'value': 'admin'}
                                            ],
                                            placeholder="Select Role",
                                            className="form-style mt-4"
                                        ),
                                        html.Button("LOGIN", id="login-button", className="btn mt-4")
                                    ])
                                ])
                            ]),
                            
                            # Signup Card (Back)
                            html.Div(className="card-back", children=[
                                html.Div(className="center-wrap", children=[
                                    html.Div(className="section text-center", children=[
                                        dcc.Input(id="signup-username", placeholder="Username", type="text", className="form-style"),
                                        html.I(className="input-icon uil uil-user"),
                                        dcc.Input(id="signup-email", placeholder="Email", type="email", className="form-style mt-4"),
                                        html.I(className="input-icon uil uil-at"),
                                        dcc.Input(id="signup-password", placeholder="Password", type="password", className="form-style mt-4"),
                                        html.I(className="input-icon uil uil-lock-alt"),
                                        dcc.Input(id="signup-confirm-password", placeholder="Confirm Password", type="password", className="form-style mt-4"),
                                        html.I(className="input-icon uil uil-lock-alt"),
                                        dcc.Dropdown(
                                            id='signup-role',
                                            options=[
                                                {'label': 'User', 'value': 'user'},
                                                {'label': 'Admin', 'value': 'admin'}
                                            ],
                                            placeholder="Select Role",
                                            className="form-style mt-4"
                                        ),
                                        html.Button("REGISTER", id="register-button", className="btn mt-4")
                                    ])
                                ])
                            ])
                        ])
                    ])
                ], className="section"),
                
                # Notification area for messages
                html.Div(id="notification-area", className="mt-3")
            ], className="auth-container p-4 rounded"),

            # Right side - Tagline
            html.Div([
                html.Div([
                    html.H1("A Step Towards", className="tagline-title"),
                    html.H1("A Skilled Nation", className="tagline-title"),
                    html.Div([
                        html.P("Login to explore", className="tagline-text"),
                        html.P("government-backed courses,", className="tagline-text"),
                        html.P("schemes, and skill development", className="tagline-text"),
                        html.P("resources.", className="tagline-text")
                    ], className="tagline-description")
                ], className="tagline-container")
            ], className="tagline-section")
        ], className="login-page-container")
    ], className="main-bg")

# App layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    # We'll still use dcc.Store, but we'll now synchronize it with Flask's session
    dcc.Store(id='session-store', storage_type='session')
])

# Callback for switching between login and signup forms
@app.callback(
    Output("auth-box", "children"),
    Input("auth-tabs", "active_tab")
)
def switch_auth_form(active_tab):
    if active_tab == "signup":
        return html.Div([
            html.H4("Sign Up", className="text-center mb-3", style={'color': '#0ff'}),
            dcc.Input(id="signup-username", placeholder="Username", type="text", className="cyber-input form-control mb-2"),
            dcc.Input(id="signup-email", placeholder="Email", type="email", className="cyber-input form-control mb-2"),
            dcc.Input(id="signup-password", placeholder="Password", type="password", className="cyber-input form-control mb-2"),
            dcc.Input(id="signup-confirm-password", placeholder="Confirm Password", type="password", className="cyber-input form-control mb-2"),
            
            dcc.Dropdown(
                id='signup-role',
                options=[
                    {'label': 'User', 'value': 'user'},
                    {'label': 'Admin', 'value': 'admin'}
                ],
                placeholder="Select Role",
                className="cyber-dropdown form-control mb-3"
            ),
            
            html.Button("Register", id="register-button", className="cyber-button btn w-100 mt-3")
        ])

    return html.Div([
        html.H4("Log In", className="text-center mb-3", style={'color': '#0ff'}),
        dcc.Input(id="login-username", placeholder="Username", type="text", className="cyber-input form-control mb-2"),
        dcc.Input(id="login-password", placeholder="Password", type="password", className="cyber-input form-control mb-2"),
        
        dcc.Dropdown(
            id='login-role',
            options=[
                {'label': 'User', 'value': 'user'},
                {'label': 'Admin', 'value': 'admin'}
            ],
            placeholder="Select Role",
            className="cyber-dropdown form-control mb-3"
        ),
        
        html.Button("Login", id="login-button", className="cyber-button btn w-100 mt-3")
    ])

# Sign Up Callback
@app.callback(
    [Output("notification-area", "children"),
     Output("session-store", "data")],
    [Input("register-button", "n_clicks")],
    [State("signup-username", "value"),
     State("signup-email", "value"),
     State("signup-password", "value"),
     State("signup-confirm-password", "value"),
     State("signup-role", "value"),
     State("session-store", "data")]
)
def register_user(n_clicks, username, email, password, confirm_password, role, session_data):
    if not n_clicks:
        return html.Div(), session_data or {}
    
    if not all([username, email, password, confirm_password, role]):
        return html.Div("All fields are required", style={"color": "red"}), session_data or {}
    
    if password != confirm_password:
        return html.Div("Passwords do not match", style={"color": "red"}), session_data or {}
    
    try:
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        user = cursor.fetchone()
        
        if user:
            return html.Div("Username or email already exists", style={"color": "red"}), session_data or {}
        
        # Insert new user
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                      (username, email, password, role))
        conn.commit()
        conn.close()
        
        # Update session data
        new_session_data = {
            'username': username,
            'role': role,
            'logged_in': True
        }
        
        # Update Flask session
        for key, value in new_session_data.items():
            session[key] = value
        
        return html.Div("Registration successful! Please log in.", style={"color": "green"}), new_session_data
    
    except Exception as e:
        return html.Div(f"An error occurred: {str(e)}", style={"color": "red"}), session_data or {}

# Login Callback - Now synchronizing Flask session with Dash store
@app.callback(
    [Output("notification-area", "children", allow_duplicate=True),
     Output("session-store", "data", allow_duplicate=True),
     Output("url", "pathname", allow_duplicate=True)],
    [Input("login-button", "n_clicks")],
    [State("login-username", "value"),
     State("login-password", "value"),
     State("login-role", "value"),
     State("session-store", "data")],
    prevent_initial_call=True
)
def login_user(n_clicks, username, password, role, session_data):
    if not n_clicks:
        return no_update, no_update, no_update
        
    try:
        # Validate login credentials
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", 
                      (username, password, role))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Prepare session data
            new_session_data = {
                'logged_in': True,
                'username': username,
                'role': role,
                'user_id': user[0]
            }
            
            # Update Flask session
            for key, value in new_session_data.items():
                session[key] = value
            
            # Redirect based on role
            redirect_path = "/admin" if role == "admin" else "/user"
            return (
                html.Div("Login successful!", style={"color": "green"}),
                new_session_data,  # Update Dash store
                redirect_path
            )
        else:
            return (
                html.Div("Invalid credentials!", style={"color": "red"}),
                session_data or {},
                "/"
            )
    except Exception as e:
        return html.Div(f"An error occurred: {str(e)}", style={"color": "red"}), session_data or {}, "/"

# Initialize session - sync Flask session to Dash store on page load
@app.callback(
    Output("session-store", "data", allow_duplicate=True),
    Input("url", "pathname"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def sync_session_on_navigation(pathname, current_data):
    # If Flask session has data, synchronize it with Dash store
    if 'logged_in' in session and session['logged_in']:
        return {
            'logged_in': session['logged_in'],
            'username': session.get('username', ''),
            'role': session.get('role', ''),
            'user_id': session.get('user_id', '')
        }
    # Return current data or empty dict if no session
    return current_data or {}

# URL Routing Callback
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
    [State("session-store", "data")]
)
def display_page(pathname, session_data):
    # Check Flask session first
    if 'logged_in' in session and session['logged_in']:
        # Use Flask session data
        username = session.get('username', 'User')
        role = session.get('role', '')
    elif session_data and session_data.get('logged_in'):
        # Fall back to Dash store if Flask session is empty
        username = session_data.get('username', 'User')
        role = session_data.get('role', '')
    else:
        # Not logged in
        return login_layout()
    
    # Import dashboards
    from user_dashboard import user_dashboard
    from admin_dashboard import admin_dashboard
    from manage_courses import manage_courses_layout
    from manage_resources import manage_resources_layout
    from manage_schemes import manage_schemes_layout
    from analytics import analytics_layout
    from view_course import view_course
    from study_plan import study_plan
    
    # Admin dashboard routes
    if pathname == "/user" and (role == 'user' or session.get('role') == 'user'):
        return user_dashboard()
    elif pathname == "/admin" and (role == 'admin' or session.get('role') == 'admin'):
        return admin_dashboard()
    elif pathname == "/manage-courses" and (role == 'admin' or session.get('role') == 'admin'):
        return manage_courses_layout()
    elif pathname == "/manage-resources" and (role == 'admin' or session.get('role') == 'admin'):
        return manage_resources_layout()
    elif pathname == "/manage-schemes" and (role == 'admin' or session.get('role') == 'admin'):
        return manage_schemes_layout()
    elif pathname == "/analytics" and (role == 'admin' or session.get('role') == 'admin'):
        return analytics_layout()
    elif pathname.startswith("/course/") and (role == 'user' or session.get('role') == 'user'):
        return view_course()
    elif pathname.startswith("/course2/") and (role == 'user' or session.get('role') == 'user'):
        return view_course()
    elif pathname == "/logout":
        return login_layout()
    elif pathname == '/resume-maker':
        return resume_maker()
    elif pathname == '/my-space':
        return my_space()
    elif pathname == '/study-plan':
        return study_plan()
    elif pathname == '/live':
        return live_layout()
    else:
        return login_layout()

# Improved logout callback
@app.callback(
    [Output("session-store", "clear_data"),
     Output("url", "pathname", allow_duplicate=True)],
    [Input("url", "pathname")],
    prevent_initial_call=True
)
def logout(pathname):
    if pathname == "/logout":
        # Clear Flask session
        session.clear()
        # Clear Dash store and redirect to login
        return True, "/"
    return False, no_update

@app.callback(
          Output("course-modal", "is_open"),
     [Input("add-ug-pg-course-btn", "n_clicks"),
      Input("add-school-course-btn", "n_clicks"),
      Input("edit-ug-pg-course-btn", "n_clicks"),
      Input("edit-school-course-btn", "n_clicks"),
      Input("save-course-btn", "n_clicks"),
      Input("cancel-course-btn", "n_clicks")],
     [State("course-modal", "is_open")]
 )
def toggle_course_modal(add_ug_pg, add_school, edit_ug_pg, edit_school, save, cancel, is_open):
     ctx = callback_context
     if not ctx.triggered:
         return is_open
     else:
         button_id = ctx.triggered[0]["prop_id"].split(".")[0]
         if button_id in ["add-ug-pg-course-btn", "add-school-course-btn", "edit-ug-pg-course-btn", "edit-school-course-btn"]:
             return True
         elif button_id in ["save-course-btn", "cancel-course-btn"]:
             return False
         return is_open
@app.callback(
    Output("admin-username", "children"),
    [Input("session", "data")]
)
def display_username(session_data):
    if session_data and 'username' in session_data:
        return session_data['username']
    from flask import session
    if 'username' in session:
        return session['username']
    return "Admin"

# Callback to toggle the admin profile modal
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
        if button_id == "profile-trigger":
            return True
        elif button_id in ["close-admin-profile-btn", "update-admin-profile-btn"]:
            return False
    return is_open
@app.callback(
    Output("active-course-tab", "data"),
    Input("courses-tabs", "active_tab")
)
def update_active_tab(active_tab):
    return active_tab

# Filter UG/PG courses
@app.callback(
    Output("ug-pg-courses-table", "data"),
    Input("search-ug-pg-courses", "value")
)
def filter_ug_pg_courses(search_value):
    if search_value is None or search_value == "":
        # Return all data
        conn = sqlite3.connect('data/USDH.db')
        df = pd.read_sql_query("SELECT * FROM courses", conn)
        conn.close()
        return df.to_dict('records')
    else:
        # Return filtered data
        conn = sqlite3.connect('data/USDH.db')
        search_term = f"%{search_value}%"
        query = """
        SELECT * FROM courses 
        WHERE course_name LIKE ? 
        OR description LIKE ?
        """
        df = pd.read_sql_query(query, conn, params=(search_term, search_term))
        conn.close()
        return df.to_dict('records')

# Filter School courses
@app.callback(
    Output("school-courses-table", "data"),
    Input("search-school-courses", "value")
)
def filter_school_courses(search_value):
    if search_value is None or search_value == "":
        # Return all data
        conn = sqlite3.connect('data/USDH.db')
        df = pd.read_sql_query("SELECT * FROM Courses2", conn)
        conn.close()
        return df.to_dict('records')
    else:
        # Return filtered data
        conn = sqlite3.connect('data/USDH.db')
        search_term = f"%{search_value}%"
        query = """
        SELECT * FROM Courses2 
        WHERE course_name LIKE ? 
        OR description LIKE ?
        """
        df = pd.read_sql_query(query, conn, params=(search_term, search_term))
        conn.close()
        return df.to_dict('records')

# Populate dynamic fields based on course type
@app.callback(
    Output("dynamic-course-fields", "children"),
    Input("course-type-select", "value")
)
def update_dynamic_fields(course_type):
    if course_type == "ug_pg":
        return html.Div([
            dbc.Input(id="course-university-input", placeholder="University/Institute", type="text", className="cyber-input mb-3"),
            dbc.Input(id="course-duration-input", placeholder="Duration", type="text", className="cyber-input mb-3"),
            dbc.Input(id="course-category-input", placeholder="Category", type="text", className="cyber-input mb-3"),
        ])
    elif course_type == "school":
        return html.Div([
            dbc.Select(
                id="course-grade-select",
                options=[{"label": f"Grade {i}", "value": str(i)} for i in range(1, 13)],
                placeholder="Select Grade",
                className="cyber-input mb-3"
            ),
            dbc.Input(id="course-subject-input", placeholder="Subject", type="text", className="cyber-input mb-3"),
            dbc.Input(id="course-board-input", placeholder="Board", type="text", className="cyber-input mb-3"),
        ])
    return html.Div()
# Handle Back to Dashboard button
@app.callback(
    Output("url-courses", "pathname"),
    [Input("back-to-dashboard", "n_clicks"),
     Input("logout-button", "n_clicks")],
    [State("session-store", "data")]
)
def navigate_from_courses(back_clicks, logout_clicks, session_data):
    ctx = callback_context
    if not ctx.triggered:
        return no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "back-to-dashboard":
        role = session_data.get("role", "user")
        return "/admin" if role == "admin" else "/user"
    
    elif button_id == "logout-button":
        return "/logout"
    
    return no_update
@app.callback(
     Output("resource-modal", "is_open"),
     [Input("add-resource-btn", "n_clicks"),
      Input("edit-resource-btn", "n_clicks"),
      Input("save-resource-btn", "n_clicks"),
      Input("cancel-resource-btn", "n_clicks")],
     [State("resource-modal", "is_open")]
 )
def toggle_resource_modal(add, edit, save, cancel, is_open):
     ctx = callback_context
     if not ctx.triggered:
         return is_open
     else:
         button_id = ctx.triggered[0]["prop_id"].split(".")[0]
         if button_id in ["add-resource-btn", "edit-resource-btn"]:
             return True
         elif button_id in ["save-resource-btn", "cancel-resource-btn"]:
             return False
         return is_open
@app.callback(
    Output("filtered-resources", "data"),
    [Input("search-resources", "value"),
     Input("resource-preference-filter", "value"),
     Input("resource-state-filter", "value")]
)
def filter_resources(search_term, preference, state):
    # Connect to database
    conn = sqlite3.connect('data/USDH.db')
    # Get resources data
    resources_df = pd.read_sql_query("SELECT * FROM ebooks", conn)
    conn.close()
    
    # Filter by search term
    if search_term and search_term != "":
        filter_condition = (
            resources_df['website'].str.contains(search_term, case=False, na=False) |
            resources_df['preference'].str.contains(search_term, case=False, na=False) |
            resources_df['subject'].str.contains(search_term, case=False, na=False) |
            resources_df['states'].str.contains(search_term, case=False, na=False)
        )
        resources_df = resources_df[filter_condition]
    
    # Filter by preference
    if preference and preference != "all":
        resources_df = resources_df[resources_df['preference'] == preference]
    
    # Filter by state
    if state and state != "all":
        resources_df = resources_df[resources_df['states'] == state]
    
    return resources_df.to_dict('records')

@app.callback(
    Output("resources-table", "data"),
    [Input("filtered-resources", "data")]
)
def update_table(filtered_data):
    # Convert links to markdown format for clickability
    data = pd.DataFrame(filtered_data)
    if not data.empty and 'link' in data.columns:
        data['link'] = data['link'].apply(lambda x: f"[Link]({x})" if pd.notna(x) else "")
    
    return data.to_dict('records')

@app.callback(
    Output("resource-detail-modal", "is_open"),
    [Input("view-resource-btn", "n_clicks"),
     Input("close-resource-detail-btn", "n_clicks")],
    [State("resource-detail-modal", "is_open"),
     State("resources-table", "selected_rows"),
     State("filtered-resources", "data")]
)
def toggle_resource_detail_modal(view_clicks, close_clicks, is_open, selected_rows, filtered_data):
    ctx = callback_context
    if not ctx.triggered:
        return is_open
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "view-resource-btn" and selected_rows:
        return True
    elif button_id == "close-resource-detail-btn":
        return False
    
    return is_open

@app.callback(
    [Output("resource-detail-title", "children"),
     Output("resource-detail-body", "children")],
    [Input("view-resource-btn", "n_clicks")],
    [State("resources-table", "selected_rows"),
     State("filtered-resources", "data")]
)
def update_resource_detail_modal(view_clicks, selected_rows, filtered_data):
    if not selected_rows:
        raise PreventUpdate
    
    selected_row = filtered_data[selected_rows[0]]
    
    title = selected_row.get('website', 'Resource Details')
    
    body = html.Div([
        html.H5("Resource Information", className="mb-3", style={'color': '#0ff'}),
        html.P([html.Strong("Website: "), selected_row.get('website', 'N/A')]),
        html.P([html.Strong("Preference: "), selected_row.get('preference', 'N/A')]),
        html.P([html.Strong("Subject: "), selected_row.get('subject', 'N/A') if selected_row.get('subject') else 'N/A']),
        html.P([html.Strong("State: "), selected_row.get('states', 'N/A')]),
        html.P([
            html.Strong("Link: "), 
            html.A("Open Resource", href=selected_row.get('link', '#'), target="_blank", className="cyber-link")
        ]),
        html.Hr(),
        html.Div([
            html.H6("Preview", className="mb-2", style={'color': '#0ff'}),
            html.Iframe(
                src=selected_row.get('link', ''),
                style={'width': '100%', 'height': '300px', 'border': '1px solid #0ff'}
            )
        ], id="resource-preview") if selected_row.get('link') else []
    ])
    
    return title, body

@app.callback(
    [Output("resource-website-input", "value"),
     Output("resource-preference-input", "value"),
     Output("resource-subject-input", "value"),
     Output("resource-state-input", "value"),
     Output("resource-link-input", "value")],
    [Input("edit-resource-btn", "n_clicks"),
     Input("add-resource-btn", "n_clicks")],
    [State("resources-table", "selected_rows"),
     State("filtered-resources", "data")]
)
def populate_resource_modal(edit_clicks, add_clicks, selected_rows, filtered_data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "edit-resource-btn" and selected_rows:
        selected_row = filtered_data[selected_rows[0]]
        return (
            selected_row.get('website', ''),
            selected_row.get('preference', ''),
            selected_row.get('subject', ''),
            selected_row.get('states', ''),
            selected_row.get('link', '')
        )
    else:
        # For add new resource
        return '', '', '', '', ''

@app.callback(
    [Output("resource-notification", "children"),
     Output("filtered-resources", "data", allow_duplicate=True)],
    [Input("save-resource-btn", "n_clicks")],
    [State("resource-website-input", "value"),
     State("resource-preference-input", "value"),
     State("resource-subject-input", "value"),
     State("resource-state-input", "value"),
     State("resource-link-input", "value"),
     State("resources-table", "selected_rows"),
     State("filtered-resources", "data")],
    prevent_initial_call=True
)
def save_resource(save_clicks, website, preference, subject, state, link, selected_rows, filtered_data):
    if not save_clicks:
        raise PreventUpdate
    
    if not website or not preference or not state or not link:
        return dbc.Alert("Please fill all required fields", color="danger"), filtered_data
    
    try:
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Check if editing existing or adding new
        is_edit = selected_rows and len(selected_rows) > 0
        
        if is_edit:
            selected_row = filtered_data[selected_rows[0]]
            # Update existing resource
            query = """
            UPDATE ebooks 
            SET website = ?, preference = ?, subject = ?, states = ?, link = ?
            WHERE rowid = (
                SELECT rowid FROM ebooks 
                WHERE website = ? AND preference = ? AND states = ? AND link = ?
                LIMIT 1
            )
            """
            cursor.execute(query, (
                website, preference, subject, state, link,
                selected_row.get('website'), selected_row.get('preference'), 
                selected_row.get('states'), selected_row.get('link')
            ))
            message = "Resource updated successfully!"
        else:
            # Add new resource
            query = "INSERT INTO ebooks (website, preference, subject, states, link) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (website, preference, subject, state, link))
            message = "New resource added successfully!"
        
        conn.commit()
        
        # Refresh data
        resources_df = pd.read_sql_query("SELECT * FROM ebooks", conn)
        conn.close()
        
        return dbc.Alert(message, color="success", dismissable=True), resources_df.to_dict('records')
    
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True), filtered_data

@app.callback(
    [Output("resource-notification", "children", allow_duplicate=True),
     Output("filtered-resources", "data", allow_duplicate=True)],
    [Input("delete-resource-btn", "n_clicks")],
    [State("resources-table", "selected_rows"),
     State("filtered-resources", "data")],
    prevent_initial_call=True
)
def delete_resource(delete_clicks, selected_rows, filtered_data):
    if not delete_clicks or not selected_rows:
        raise PreventUpdate
    
    try:
        selected_row = filtered_data[selected_rows[0]]
        
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Delete the resource
        query = """
        DELETE FROM ebooks 
        WHERE rowid = (
            SELECT rowid FROM ebooks 
            WHERE website = ? AND preference = ? AND states = ? AND link = ?
            LIMIT 1
        )
        """
        cursor.execute(query, (
            selected_row.get('website'), selected_row.get('preference'), 
            selected_row.get('states'), selected_row.get('link')
        ))
        
        conn.commit()
        
        # Refresh data
        resources_df = pd.read_sql_query("SELECT * FROM ebooks", conn)
        conn.close()
        
        return dbc.Alert("Resource deleted successfully!", color="success", dismissable=True), resources_df.to_dict('records')
    
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True), filtered_data
@app.callback(
    [Output("admin-profile-username", "value"),
     Output("admin-profile-email", "value"),
     Output("current-admin-username", "children"),
     Output("current-admin-email", "children"),
     Output("current-admin-role", "children"),
     Output("current-admin-id", "children")],
    [Input("admin-profile-modal", "is_open")],
    [State("session-store", "data")]
)
def populate_admin_profile(is_open, session_data):
    if not is_open or not session_data:
        return "", "", "", "", "", ""
    
    try:
        from flask import session as flask_session
        user_id = session_data.get('user_id') or flask_session.get('user_id')
        
        if not user_id:
            return "", "", "", "", "", ""
        
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, email, role, id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return user[0], user[1], user[0], user[1], user[2], str(user[3])
        else:
            return "", "", "", "", "", ""
    except Exception as e:
        print(f"Error loading admin profile: {str(e)}")
        return "", "", "", "", "", ""

# Modified callback to update admin profile
@app.callback(
    Output("admin-profile-update-status", "children"),
    [Input("update-admin-profile-btn", "n_clicks")],
    [State("admin-profile-username", "value"),
     State("admin-profile-email", "value"),
     State("admin-profile-current-password", "value"),
     State("admin-profile-new-password", "value"),
     State("admin-profile-confirm-password", "value"),
     State("session-store", "data"),
     State("current-admin-username", "children"),
     State("current-admin-email", "children")]
)
def update_admin_profile(n_clicks, username, email, current_password, new_password, confirm_password, 
                          session_data, current_username, current_email):
    if not n_clicks:
        return ""
    
    try:
        from flask import session as flask_session
        user_id = session_data.get('user_id') or flask_session.get('user_id')
        
        if not user_id:
            return html.Div("Session expired. Please log in again.", style={"color": "red"})
        
        # Check if any changes are being made
        is_username_changed = username and username != current_username
        is_email_changed = email and email != current_email
        is_password_changed = new_password and len(new_password) > 0
        
        # If nothing is being changed, inform the user
        if not (is_username_changed or is_email_changed or is_password_changed):
            return html.Div("No changes detected. Profile remains the same.", style={"color": "blue"})
        
        # Password verification is only needed when changing password or critical info
        needs_password_verification = is_password_changed or is_username_changed or is_email_changed
        
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Verify current password if needed
        if needs_password_verification:
            if not current_password:
                conn.close()
                return html.Div("Current password is required to make these changes", style={"color": "red"})
                
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            stored_password = cursor.fetchone()
            
            if not stored_password or stored_password[0] != current_password:
                conn.close()
                return html.Div("Current password is incorrect", style={"color": "red"})
        
        # Handle password update
        if is_password_changed:
            if not confirm_password:
                conn.close()
                return html.Div("Please confirm your new password", style={"color": "red"})
                
            if new_password != confirm_password:
                conn.close()
                return html.Div("New passwords do not match", style={"color": "red"})
        
        # For email change, validate email format
        if is_email_changed:
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(email):
                conn.close()
                return html.Div("Please enter a valid email address", style={"color": "red"})
                
            # Check if email is already in use by another user
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                conn.close()
                return html.Div("Email already in use by another user", style={"color": "red"})
        
        # Prepare the SQL update based on what's changed
        update_fields = []
        params = []
        
        if is_username_changed:
            update_fields.append("username = ?")
            params.append(username)
        
        if is_email_changed:
            update_fields.append("email = ?")
            params.append(email)
        
        if is_password_changed:
            update_fields.append("password = ?")
            params.append(new_password)
        
        # Only perform update if there are changes
        if update_fields:
            sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            params.append(user_id)
            cursor.execute(sql, params)
            conn.commit()
            
            # Update session with new username if it changed
            if is_username_changed:
                if flask_session.get('username'):
                    flask_session['username'] = username
                if session_data.get('username'):
                    session_data['username'] = username
                    
            # Update session with new email if it changed
            if is_email_changed:
                if flask_session.get('email'):
                    flask_session['email'] = email
                if session_data.get('email'):
                    session_data['email'] = email
        
        conn.close()
        
        # Create success messages for each change
        success_messages = []
        if is_username_changed:
            success_messages.append(html.P("Username changed successfully!", style={"color": "green"}))
        if is_email_changed:
            success_messages.append(html.P("Email changed successfully!", style={"color": "green"}))
        if is_password_changed:
            success_messages.append(html.P("Password changed successfully!", style={"color": "green"}))
            
        return html.Div(success_messages)
    except Exception as e:
        return html.Div(f"An error occurred: {str(e)}", style={"color": "red"})
    
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>USDH</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
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

@server.route('/download-resume/<int:resume_id>')
def download_resume(resume_id):
    from flask import send_file, redirect, url_for
    
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('/'))
        
    user_id = session['user_id']
    
    try:
        # Get the resume file path from database
        conn = sqlite3.connect('courses.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path 
            FROM resume_downloads 
            WHERE id = ? AND user_id = ?
        ''', (resume_id, user_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return "Resume not found", 404
        
        file_path = result[0]
        
        # Check if file exists
        if not os.path.exists(file_path):
            return "Resume file not found", 404
        
        # Send the file
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"resume_{resume_id}.pdf"
        )
        
    except Exception as e:
        print(f"Error downloading resume: {e}")
        return f"Error downloading resume: {str(e)}", 500

if __name__ == '__main__':
    app.run(
        debug=True,
        dev_tools_ui=False,  # This disables the UI components of dev tools
        dev_tools_props_check=False
    )