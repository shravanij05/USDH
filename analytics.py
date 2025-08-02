# analytics.py
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash.exceptions import PreventUpdate
from flask import session
import datetime

def analytics_layout():
    # Connect to the database to get stats
    conn = sqlite3.connect('data/USDH.db')
    
    # Get counts from each table
    courses_count = pd.read_sql_query("SELECT COUNT(*) as count FROM courses", conn).iloc[0]['count']
    resources_count = pd.read_sql_query("SELECT COUNT(*) as count FROM ebooks", conn).iloc[0]['count']
    schemes_count = pd.read_sql_query("SELECT COUNT(*) as count FROM schemes", conn).iloc[0]['count']
    k12_count = pd.read_sql_query("SELECT COUNT(*) as count FROM courses2", conn).iloc[0]['count']
    
    # Get user count
    users_count = pd.read_sql_query("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
    
    # Get discipline distribution from courses
    discipline_df = pd.read_sql_query(
        "SELECT dispcipline as discipline, COUNT(*) as count FROM courses GROUP BY dispcipline", 
        conn
    )
    # Filter out empty or null values
    discipline_df = discipline_df.dropna(subset=['discipline'])
    discipline_df = discipline_df[discipline_df['discipline'] != '']
    
    # Get subject distribution from courses2
    subject_df = pd.read_sql_query(
        "SELECT subjects, COUNT(*) as count FROM courses2 GROUP BY subjects", 
        conn
    )
    # Filter out empty or null values
    subject_df = subject_df.dropna(subset=['subjects'])
    subject_df = subject_df[subject_df['subjects'] != '']
    
    # Get state distribution from ebooks
    state_df = pd.read_sql_query(
        "SELECT states, COUNT(*) as count FROM ebooks GROUP BY states", 
        conn
    )
    # Filter out empty or null values
    state_df = state_df.dropna(subset=['states'])
    state_df = state_df[state_df['states'] != '']
    
    # Get preference distribution from ebooks
    preference_df = pd.read_sql_query(
        "SELECT preference, COUNT(*) as count FROM ebooks GROUP BY preference", 
        conn
    )
    # Filter out empty or null values
    preference_df = preference_df.dropna(subset=['preference'])
    preference_df = preference_df[preference_df['preference'] != '']
    
    # Generate content distribution data
    content_distribution = pd.DataFrame({
        'Content Type': ['UG/PG Courses', 'K-12 Courses', 'E-Books', 'Scholarship Schemes'],
        'Count': [courses_count, k12_count, resources_count, schemes_count]
    })
    
    # Tables distribution data
    tables_list = [
        'users', 'certificates', 'courses', 'courses2', 'ebooks', 
        'schemes', 'resumes', 'study_plans', 'documents', 'folders'
    ]
    tables_counts = []
    
    for table in tables_list:
        try:
            count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn).iloc[0]['count']
            tables_counts.append(count)
        except:
            tables_counts.append(0)
    
    tables_distribution = pd.DataFrame({
        'Table': tables_list,
        'Record Count': tables_counts
    })
    
    # Get user activity info (certificates, resumes, documents)
    user_activity = pd.DataFrame({
        'Activity Type': ['Certificates', 'Resumes', 'Study Plans', 'Documents', 'Folders'],
        'Count': [
            pd.read_sql_query("SELECT COUNT(*) as count FROM certificates", conn).iloc[0]['count'],
            pd.read_sql_query("SELECT COUNT(*) as count FROM resumes", conn).iloc[0]['count'],
            pd.read_sql_query("SELECT COUNT(*) as count FROM study_plans", conn).iloc[0]['count'],
            pd.read_sql_query("SELECT COUNT(*) as count FROM documents", conn).iloc[0]['count'],
            pd.read_sql_query("SELECT COUNT(*) as count FROM folders", conn).iloc[0]['count']
        ]
    })
    
    conn.close()
    
    # Create visualizations from the database data
    content_fig = px.bar(
        content_distribution,
        x='Content Type',
        y='Count',
        title='Content Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel1,
        template="plotly_white"
    )
    content_fig.update_layout(
        font=dict(color='#1a73e8'),
        title_font=dict(color='#1a73e8', size=18),
        margin=dict(l=40, r=20, t=60, b=40)
    )
    
    # Discipline distribution pie chart
    discipline_fig = px.pie(
        discipline_df,
        names='discipline',
        values='count',
        title='UG/PG Courses by Discipline',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel1,
        template="plotly_white"
    )
    discipline_fig.update_layout(
        font=dict(color='#1a73e8'),
        title_font=dict(color='#1a73e8', size=18),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Subject distribution pie chart
    subject_fig = px.pie(
        subject_df,
        names='subjects',
        values='count',
        title='School Courses by Subject',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel2,
        template="plotly_white"
    )
    subject_fig.update_layout(
        font=dict(color='#1a73e8'),
        title_font=dict(color='#1a73e8', size=18),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # State distribution for ebooks
    state_fig = px.bar(
        state_df.sort_values('count', ascending=False).head(10),
        x='states',
        y='count',
        title='E-Books by State (Top 10)',
        color_discrete_sequence=['#1a73e8'],
        template="plotly_white"
    )
    state_fig.update_layout(
        font=dict(color='#1a73e8'),
        title_font=dict(color='#1a73e8', size=18),
        margin=dict(l=40, r=20, t=60, b=80)
    )
    state_fig.update_xaxes(title_text="State", tickangle=45)
    state_fig.update_yaxes(title_text="Count")
    
    # User activity bar chart
    user_activity_fig = px.bar(
        user_activity,
        x='Activity Type',
        y='Count',
        title='User Activity by Type',
        color_discrete_sequence=['#4CAF50'],
        template="plotly_white"
    )
    user_activity_fig.update_layout(
        font=dict(color='#1a73e8'),
        title_font=dict(color='#1a73e8', size=18),
        margin=dict(l=40, r=20, t=60, b=40)
    )
    
    # Preference distribution for ebooks
    preference_fig = px.pie(
        preference_df,
        names='preference',
        values='count',
        title='E-Books by Preference',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blugrn,
        template="plotly_white"
    )
    preference_fig.update_layout(
        font=dict(color='#1a73e8'),
        title_font=dict(color='#1a73e8', size=18),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Tables distribution figure
    tables_fig = px.bar(
        tables_distribution,
        x='Table',
        y='Record Count',
        title='Database Records by Table',
        color='Record Count',
        color_continuous_scale=px.colors.sequential.Blues,
        template="plotly_white"
    )
    tables_fig.update_layout(
        font=dict(color='#1a73e8'),
        title_font=dict(color='#1a73e8', size=18),
        margin=dict(l=40, r=20, t=60, b=60)
    )
    tables_fig.update_xaxes(tickangle=45)
    
    layout = html.Div([
        # Background with floating particles
        html.Div([
            html.Div(className="particle") for _ in range(10)
        ], className="particles-container"),
        
        # Educational-themed header with enhanced styling
        html.Div([
            html.H2("Analytics Dashboard", className="text-center mb-4", style={
                'color': '#1a73e8',
                'textShadow': '2px 2px 4px rgba(26,115,232,0.2)',
                'fontSize': '2.5rem',
                'fontWeight': '600',
                'letterSpacing': '0.5px'
            }),
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-arrow-left me-2"),
                    "Back to Dashboard"
                ], id="back-to-admin", className="edu-button me-2"),
                dbc.Button([
                    html.I(className="fas fa-sign-out-alt me-2"),
                    "Logout"
                ], id="logout-btn", className="edu-button btn-danger")
            ], className="d-flex justify-content-between")
        ], className="header-container mb-4"),
        
        # Stats Overview Cards with enhanced icons and animations
        html.Div([
            html.Div([
                html.Div(className="icon-circle mb-3", children=[
                    html.I(className="fas fa-book-open fa-2x", style={'color': '#1a73e8'})
                ]),
                html.H3(f"{courses_count}", className="stat-number", style={'color': '#1a73e8', 'fontSize': '2.5rem', 'fontWeight': '600'}),
                html.P("UG/PG Courses", className="stat-label", style={'color': '#1a73e8'})
            ], className="edu-stat-card"),
            
            html.Div([
                html.Div(className="icon-circle mb-3", children=[
                    html.I(className="fas fa-child fa-2x", style={'color': '#1a73e8'})
                ]),
                html.H3(f"{k12_count}", className="stat-number", style={'color': '#1a73e8', 'fontSize': '2.5rem', 'fontWeight': '600'}),
                html.P("K-12 Courses", className="stat-label", style={'color': '#1a73e8'})
            ], className="edu-stat-card"),
            
            html.Div([
                html.Div(className="icon-circle mb-3", children=[
                    html.I(className="fas fa-laptop-code fa-2x", style={'color': '#1a73e8'})
                ]),
                html.H3(f"{resources_count}", className="stat-number", style={'color': '#1a73e8', 'fontSize': '2.5rem', 'fontWeight': '600'}),
                html.P("E-Books", className="stat-label", style={'color': '#1a73e8'})
            ], className="edu-stat-card"),
            
            html.Div([
                html.Div(className="icon-circle mb-3", children=[
                    html.I(className="fas fa-graduation-cap fa-2x", style={'color': '#1a73e8'})
                ]),
                html.H3(f"{schemes_count}", className="stat-number", style={'color': '#1a73e8', 'fontSize': '2.5rem', 'fontWeight': '600'}),
                html.P("Scholarship Schemes", className="stat-label", style={'color': '#1a73e8'})
            ], className="edu-stat-card"),
            
            html.Div([
                html.Div(className="icon-circle mb-3", children=[
                    html.I(className="fas fa-users fa-2x", style={'color': '#1a73e8'})
                ]),
                html.H3(f"{users_count}", className="stat-number", style={'color': '#1a73e8', 'fontSize': '2.5rem', 'fontWeight': '600'}),
                html.P("Registered Users", className="stat-label", style={'color': '#1a73e8'})
            ], className="edu-stat-card"),
        ], className="stats-grid mb-4"),
        
        # Enhanced graph containers with loading states
        html.Div([
            html.Div([
                html.Div(className="graph-container", children=[
                    dcc.Loading(
                        id="loading-content-distribution",
                        type="circle",
                        children=dcc.Graph(
                            id='content-distribution',
                            figure=content_fig,
                            config={'displayModeBar': False},
                            className="edu-graph"
                        )
                    )
                ])
            ], className="edu-card p-0 w-100"),
        ], className="mb-4"),
        
        # Course Distribution and Subject Distribution
        html.Div([
            # Discipline Distribution
            html.Div([
                dcc.Graph(
                    id='discipline-distribution',
                    figure=discipline_fig,
                    config={'displayModeBar': False},
                    className="edu-graph"
                )
            ], className="edu-card p-0"),
            
            # Subject Distribution
            html.Div([
                dcc.Graph(
                    id='subject-distribution',
                    figure=subject_fig,
                    config={'displayModeBar': False},
                    className="edu-graph"
                )
            ], className="edu-card p-0"),
        ], className="dashboard-grid-2 mb-4"),
        
        # E-Books State Distribution
        html.Div([
            html.Div([
                dcc.Graph(
                    id='state-distribution',
                    figure=state_fig,
                    config={'displayModeBar': False},
                    className="edu-graph"
                )
            ], className="edu-card p-0 w-100"),
        ], className="mb-4"),
        
        # User Activity and Preference Distribution
        html.Div([
            # User Activity
            html.Div([
                dcc.Graph(
                    id='user-activity',
                    figure=user_activity_fig,
                    config={'displayModeBar': False},
                    className="edu-graph"
                )
            ], className="edu-card p-0"),
            
            # Preference Distribution
            html.Div([
                dcc.Graph(
                    id='preference-distribution',
                    figure=preference_fig,
                    config={'displayModeBar': False},
                    className="edu-graph"
                )
            ], className="edu-card p-0"),
        ], className="dashboard-grid-2 mb-4"),
        
        # Database Records by Table
        html.Div([
            html.Div([
                dcc.Graph(
                    id='tables-distribution',
                    figure=tables_fig,
                    config={'displayModeBar': False},
                    className="edu-graph"
                )
            ], className="edu-card p-0 w-100"),
        ], className="mb-4"),
        
        # Store for page navigation
        dcc.Store(id="analytics-redirect", data=""),
        
        # Add interval component for real-time updates
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # in milliseconds
            n_intervals=0
        )
    ], className="main-container")
    
    return layout

def register_callbacks(app):
    @app.callback(
        Output("analytics-redirect", "data"),
        [Input("back-to-admin", "n_clicks"),
         Input("logout-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def handle_analytics_navigation(back_clicks, logout_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "back-to-admin":
            role = session.get("role", "admin")
            return "/admin" if role == "admin" else "/user"
        elif button_id == "logout-btn":
            return "/logout"
            
        raise PreventUpdate
        
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        [Input("analytics-redirect", "data")],
        prevent_initial_call=True
    )
    def perform_analytics_redirect(path):
        if path:
            return path
        raise PreventUpdate