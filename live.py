import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
import re

def live_layout():
    # Get unique grades from live table
    conn = sqlite3.connect('data/USDH.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT grade FROM live ORDER BY grade')
    grades = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return html.Div([
        dbc.Container([
            # Header
            html.Div([
                html.H2("Live Classes", className="text-center mb-4"),
                html.Hr(),
            ]),
            
            # Grade selection dropdown
            dbc.Row([
                dbc.Col([
                    html.Label("Select Grade:", className="mb-2"),
                    dcc.Dropdown(
                        id='grade-selector',
                        options=[{'label': f'Grade {grade}', 'value': grade} for grade in grades],
                        placeholder="Choose a grade",
                        className="mb-4"
                    ),
                ], width=6, className="mx-auto")
            ]),
            
            # Video display area
            dbc.Row([
                dbc.Col([
                    html.Div(id='video-container', className="ratio ratio-16x9 mb-4")
                ], width=12)
            ]),
            
            # Schedule section
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "View Schedule",
                        id="view-schedule-btn",
                        color="primary",
                        className="mb-3"
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(id="schedule-content"),
                            className="mb-3"
                        ),
                        id="schedule-collapse",
                        is_open=False,
                    )
                ], width=12)
            ])
        ], fluid=True, className="py-4")
    ])

def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats"""
    # For URLs like https://www.youtube.com/watch?v=VIDEO_ID
    watch_pattern = r'(?:youtube\.com\/watch\?v=)([\w-]+)'
    # For URLs like https://youtu.be/VIDEO_ID
    short_pattern = r'(?:youtu\.be\/)([\w-]+)'
    # For URLs like https://www.youtube.com/embed/VIDEO_ID
    embed_pattern = r'(?:youtube\.com\/embed\/)([\w-]+)'
    
    patterns = [watch_pattern, short_pattern, embed_pattern]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If all patterns fail, try a simpler approach
    if 'v=' in url:
        # Get the value of the v parameter
        video_id = url.split('v=')[1]
        # Remove any additional URL parameters
        if '&' in video_id:
            video_id = video_id.split('&')[0]
        return video_id
    
    # Return the last part of the URL as a fallback
    return url.split('/')[-1]

def init_live_callbacks(app):
    @app.callback(
        [Output('video-container', 'children'),
         Output('schedule-content', 'children')],
        [Input('grade-selector', 'value')]
    )
    def update_content(selected_grade):
        if not selected_grade:
            return None, None
            
        try:
            conn = sqlite3.connect('data/USDH.db')
            df = pd.read_sql_query('SELECT link, schedule FROM live WHERE grade = ?',
                                 conn, params=(selected_grade,))
            conn.close()
            
            if df.empty:
                return html.P("No content available for this grade."), None
            
            # Extract video ID using the improved function
            video_link = df.iloc[0]['link']
            video_id = extract_youtube_id(video_link)
            
            # Create embedded video player with only supported attributes
            video_player = html.Iframe(
                src=f"https://www.youtube.com/embed/{video_id}",
                style={"width": "100%", "height": "100%"},
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            )
            
            # Format schedule information as a clickable link
            schedule_url = df.iloc[0]['schedule']
            schedule_info = html.Div([
                html.H5("Class Schedule", className="mb-3"),
                html.A(
                    "Click here to view schedule",
                    href=schedule_url,
                    target="_blank",
                    className="btn btn-primary",
                    style={
                        'textDecoration': 'none',
                        'color': 'white',
                        'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                        'padding': '10px 20px',
                        'borderRadius': '5px',
                        'boxShadow': '0 2px 5px rgba(0,0,0,0.2)',
                        'transition': 'all 0.3s ease'
                    }
                )
            ])
            
            return video_player, schedule_info
            
        except Exception as e:
            print(f"Error: {e}")
            return html.P(f"Error loading content: {str(e)}"), None

    @app.callback(
        Output("schedule-collapse", "is_open"),
        [Input("view-schedule-btn", "n_clicks")],
        [State("schedule-collapse", "is_open")]
    )
    def toggle_schedule(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open