import dash
from dash import html, dcc, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import os
from flask import session, request
import uuid

# Initialize app with session management
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='assets',
    suppress_callback_exceptions=True
)
server = app.server
server.secret_key = 'USDH'  # Keep using the same secret key

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
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Login/Register Page (Main Page)
def login_layout():
    return html.Div([  
        html.Canvas(id="matrixCanvas", style={
            'position': 'absolute', 'top': 0, 'left': 0, 
            'width': '100vw', 'height': '100vh', 'zIndex': -1
        }),
        
        html.Div([  
            html.Div([
               html.Div(html.Img(src="/static/images/logo.png", className="logo"), style={'marginRight': '15px'}),

                html.H4("Unified Skill Development Hub", className="text-center mb-3", style={
                    'color': '#0ff',
                    'text-align': 'center',
                    'font-size': '1 rem',
                    'margin': '0',
                    'textShadow': '0 0 10px #0ff, 0 0 20px #0ff'
                })
            ], className="header-container"),

            dbc.Tabs([
                dbc.Tab(label="Login", tab_id="login"),
                dbc.Tab(label="Sign Up", tab_id="signup"),
            ], id="auth-tabs", active_tab="login", className="mb-3"),

            html.Div(id="auth-box"),
            
            # Notification area for messages
            html.Div(id="notification-area", className="mt-3")
        ], className="auth-container p-4 rounded"),
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
        conn = sqlite3.connect('data/users.db')
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
     Output("url", "pathname")],
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
        conn = sqlite3.connect('data/users.db')
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
        return html.Div("Analytics Dashboard Coming Soon", style={'color': '#0ff'})
    elif pathname == "/logout":
        return login_layout()
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

# Matrix background animation
app.clientside_callback(
    """  
    function() {  
        const canvas = document.getElementById('matrixCanvas');  
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');  
        const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()';  
        const fontSize = 16;  

        canvas.width = window.innerWidth;  
        canvas.height = window.innerHeight;  
        const columns = Math.floor(canvas.width / fontSize);  
        const drops = Array(columns).fill(1);  

        function resizeCanvas() {  
            if (!canvas) return;
            canvas.width = window.innerWidth;  
            canvas.height = window.innerHeight;  
        }  

        window.addEventListener('resize', resizeCanvas);  

        function draw() {  
            if (!canvas) return;
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';  
            ctx.fillRect(0, 0, canvas.width, canvas.height);  
            ctx.fillStyle = '#0ff';  
            ctx.font = `${fontSize}px monospace`;  

            drops.forEach((y, i) => {  
                const text = matrixChars[Math.floor(Math.random() * matrixChars.length)];  
                const x = i * fontSize;  
                ctx.fillText(text, x, y * fontSize);  

                if (y * fontSize > canvas.height && Math.random() > 0.975) {  
                    drops[i] = 0;  
                }  

                drops[i]++;  
            });  
        }  

        const interval = setInterval(draw, 50);
        return () => clearInterval(interval);
    }  
    """,  
    Output('matrixCanvas', 'children'),  
    [Input('matrixCanvas', 'id')]  
)

if __name__ == '__main__':  
    app.run_server(debug=True)