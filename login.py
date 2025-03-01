import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
from datetime import datetime
import os
from urllib.parse import quote
from flask import redirect

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server  # Expose the server for redirects

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create the table with correct column names
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  email TEXT,
                  password TEXT,
                  role TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Login/Signup Layout
auth_layout = html.Div([
    html.Canvas(id="matrixCanvas", style={
        'position': 'absolute', 'top': 0, 'left': 0, 
        'width': '100vw', 'height': '100vh', 'zIndex': -1
    }),
    
    html.Div([  
        html.Div([
           html.Div(html.Img(src="static/images/logo.png", className="logo"), style={'marginRight': '15px'}),

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
        html.Div(id='output-message')
    ], className="auth-container p-4 rounded"),
], className="main-bg")

# Main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),  # Changed refresh to True to allow for actual redirects
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return auth_layout
    # For other paths, we'll use Flask redirects instead of Dash layouts
    return html.Div("Redirecting...")

@app.callback(
    Output("auth-box", "children"),
    [Input("auth-tabs", "active_tab")]
)
def switch_auth_form(active_tab):
    if active_tab == "signup":
        return html.Div([
            html.H4("Sign Up", className="text-center mb-3", style={'color': '#0ff'}),
            dcc.Input(id='signup-username', placeholder="Username", type="text", className="cyber-input form-control mb-2"),
            dcc.Input(id='signup-email', placeholder="Email", type="email", className="cyber-input form-control mb-2"),
            dcc.Input(id='signup-password', placeholder="Password", type="password", className="cyber-input form-control mb-2"),
            dcc.Input(id='signup-confirm', placeholder="Confirm Password", type="password", className="cyber-input form-control mb-2"),
            
            dcc.Dropdown(
                id='signup-role',
                options=[
                    {'label': 'User', 'value': 'user'},
                    {'label': 'Admin', 'value': 'admin'}
                ],
                placeholder="Select Role",
                className="cyber-dropdown form-control mb-3"
            ),
            
            html.Button("Register", id='signup-button', className="cyber-button btn w-100 mt-3")
        ])

    return html.Div([
        html.H4("Log In", className="text-center mb-3", style={'color': '#0ff'}),
        dcc.Input(id='login-username', placeholder="Username", type="text", className="cyber-input form-control mb-2"),
        dcc.Input(id='login-password', placeholder="Password", type="password", className="cyber-input form-control mb-2"),
        
        dcc.Dropdown(
            id='login-role',
            options=[
                {'label': 'User', 'value': 'user'},
                {'label': 'Admin', 'value': 'admin'}
            ],
            placeholder="Select Role",
            className="cyber-dropdown form-control mb-3"
        ),
        
        html.Button("Login", id='login-button', className="cyber-button btn w-100 mt-3")
    ])

# Add Flask routes for external redirects
@server.route('/admin-dashboard')
def admin_redirect():
    return redirect('/admin_dashboard.py')  # Redirects to separate admin dashboard file

@server.route('/user-dashboard')
def user_redirect():
    return redirect('/user_dashboard.py')  # Redirects to separate user dashboard file

@app.callback(
    [Output('url', 'pathname'),
     Output('output-message', 'children')],
    [Input('signup-button', 'n_clicks')],
    [State('signup-username', 'value'),
     State('signup-email', 'value'),
     State('signup-password', 'value'),
     State('signup-confirm', 'value'),
     State('signup-role', 'value')]
)
def handle_signup(n_clicks, username, email, password, confirm, role):
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    if not all([username, email, password, confirm, role]):
        return dash.no_update, html.Div('All fields are required', style={'color': 'red'})
    
    if password != confirm:
        return dash.no_update, html.Div('Passwords do not match', style={'color': 'red'})
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                 (username, email, password, role))
        conn.commit()
        return f'/{role}-dashboard', html.Div('Registration successful!', style={'color': 'green'})
    except sqlite3.IntegrityError:
        return dash.no_update, html.Div('Username already exists', style={'color': 'red'})
    finally:
        conn.close()

@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('output-message', 'children', allow_duplicate=True)],
    [Input('login-button', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value'),
     State('login-role', 'value')],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password, role):
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    if not all([username, password, role]):
        return dash.no_update, html.Div('All fields are required', style={'color': 'red'})
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?",
             (username, password, role))
    user = c.fetchone()
    conn.close()
    
    if user:
        return f'/{role}-dashboard', html.Div('Login successful!', style={'color': 'green'})
    else:
        return dash.no_update, html.Div('Invalid credentials', style={'color': 'red'})

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>USDH</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #000;
                font-family: 'Orbitron', sans-serif;
                color: #0ff;
            }
            
            .main-bg {
                position: relative;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: transparent;
            }
            
            .auth-container {
                width: 400px;
                max-width: 90%;
                text-align: center;
                background: rgba(0, 10, 20, 0.8);
                border-radius: 15px;
                box-shadow: 0 0 20px #0ff,
                           inset 0 0 20px #0ff;
                border: 2px solid #0ff;
                z-index: 1;
                backdrop-filter: blur(10px);
                animation: container-glow 2s infinite alternate;
            }
            
            @keyframes container-glow {
                from {
                    box-shadow: 0 0 20px #0ff,
                               inset 0 0 20px #0ff;
                }
                to {
                    box-shadow: 0 0 30px #0ff,
                               inset 0 0 30px #0ff;
                }
            }

            .header-container {
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
                padding: 10px;
                background: rgba(0, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid #0ff;
            }

            .logo {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                border: 2px solid #0ff;
                box-shadow: 0 0 10px #0ff;
                animation: logo-pulse 2s infinite alternate;
            }
            
            @keyframes logo-pulse {
                from { transform: scale(1); }
                to { transform: scale(1.1); }
            }
            
            .cyber-input {
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
                width: 100%;
                background: rgba(0, 20, 30, 0.8) !important;
                border: 1px solid #0ff !important;
                color: #0ff !important;
                transition: all 0.3s ease;
                animation: input-glow 2s infinite alternate;
            }
            
            @keyframes input-glow {
                from { box-shadow: 0 0 5px #0ff; }
                to { box-shadow: 0 0 15px #0ff; }
            }
            
            .cyber-input:focus {
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.7);
                background: rgba(0, 20, 30, 0.9) !important;
                outline: none;
                transform: scale(1.02);
            }
            
            .cyber-input::placeholder {
                color: rgba(0, 255, 255, 0.7);
            }

            /* Enhanced Dropdown Styling */
            .cyber-dropdown {
                background: rgba(0, 0, 0, 0.95) !important;
                border: 2px solid #000 !important;
                color: #0ff !important;
            }

            .cyber-dropdown .Select-control {
                background: rgba(0, 0, 0, 0.95) !important;
                border: 2px solid #000 !important;
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
                transition: all 0.3s ease;
            }

            .cyber-dropdown .Select-menu-outer {
                background: rgba(0, 0, 0, 0.95) !important;
                border: 2px solid #000 !important;
                color: #0ff !important;
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
            }

            .cyber-dropdown .Select-option {
                background: rgba(0, 0, 0, 0.95) !important;
                color: #0ff !important;
                padding: 10px;
            }

            .cyber-dropdown .Select-option:hover {
                background: rgba(0, 255, 255, 0.2) !important;
                cursor: pointer;
            }

            .cyber-dropdown .Select-value-label {
                color: #0ff !important;
            }

            .cyber-dropdown .Select-placeholder {
                color: #0ff !important;
            }

            /* Button styling with constant glow */
            .cyber-button {
                background: rgba(0, 20, 30, 0.8);
                color: #0ff;
                border: 2px solid #0ff;
                padding: 10px 20px;
                font-size: 1.1em;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 2px;
                position: relative;
                overflow: hidden;
                animation: button-glow 2s infinite alternate;
            }
            
            @keyframes button-glow {
                from {
                    box-shadow: 0 0 5px #0ff,
                               inset 0 0 5px #0ff;
                }
                to {
                    box-shadow: 0 0 15px #0ff,
                               inset 0 0 10px #0ff;
                }
            }
            
            .cyber-button:hover {
                background-color: #0ff;
                color: #000;
                box-shadow: 0 0 20px #0ff;
                transform: scale(1.05);
            }
            
            .cyber-button:active {
                background-color: #0ff;
                color: #000;
                box-shadow: 0 0 30px #0ff;
                transform: scale(0.98);
            }

            .nav-tabs {
                border-bottom: 1px solid #0ff;
            }
            
            .nav-tabs .nav-link {
                color: #0ff;
                background: rgba(0, 20, 30, 0.6);
                border: 1px solid #0ff;
                margin-right: 5px;
                transition: all 0.3s ease;
            }
            
            .nav-tabs .nav-link:hover {
                background: rgba(0, 255, 255, 0.2);
                border: 1px solid #0ff;
                color: #fff;
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
            }
            
            .nav-tabs .nav-link.active {
                background: rgba(0, 255, 255, 0.2);
                color: #fff;
                border: 1px solid #0ff;
                font-weight: bold;
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
            }

            /* Remove any white backgrounds */
            * {
                background-color: transparent;
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

# Matrix background animation
app.clientside_callback(
    """  
    function() {  
        const canvas = document.getElementById('matrixCanvas');  
        const ctx = canvas.getContext('2d');  
        const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()';  
        const fontSize = 16;  

        canvas.width = window.innerWidth;  
        canvas.height = window.innerHeight;  
        const columns = Math.floor(canvas.width / fontSize);  
        const drops = Array(columns).fill(1);  

        function resizeCanvas() {  
            canvas.width = window.innerWidth;  
            canvas.height = window.innerHeight;  
        }  

        window.addEventListener('resize', resizeCanvas);  

        function draw() {  
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

        setInterval(draw, 50);  
    }  
    """,  
    Output('matrixCanvas', 'children'),  
    [Input('matrixCanvas', 'id')]  
)

if __name__ == '__main__':  
    app.run_server(debug=True)