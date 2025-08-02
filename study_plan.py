import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
from flask import session as flask_session
import os
import datetime
import json

def study_plan():
    """
    Study Plan Generator page layout
    """
    # Check if user is logged in using both Flask session and Dash store
    user_id = flask_session.get('user_id')
    if not user_id:
        return html.Div([
            html.H3("Please log in to access Study Plan Generator", className="text-center mb-4"),
            html.A("Go to Login", href="/", className="btn btn-primary")
        ], className="text-center")
    
    # Load existing study plans
    initial_plans = get_study_plans_list(user_id)
    
    return html.Div([
        # Header
        html.Div([
            html.H2("Study Plan Generator", className="mb-4"),
            dbc.Button("Back to Dashboard", href="/user", color="secondary", className="mb-3"),
        ], className="mb-4"),
        
        # Main Content
        dbc.Row([
            # Left Column - Study Plan Creation
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Create New Study Plan", className="mb-0"),
                        dbc.Button(
                            "Generate Plan",
                            id="generate-plan-btn",
                            color="primary",
                            className="float-end"
                        )
                    ], className="d-flex justify-content-between align-items-center"),
                    dbc.CardBody([
                        dbc.Form([
                            # Subject Selection
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Subject"),
                                    dbc.Input(
                                        id="subject-input",
                                        type="text",
                                        placeholder="Enter subject (e.g., Mathematics, Physics)",
                                        className="mb-3"
                                    )
                                ], width=12)
                            ]),
                            
                            # Topic Selection
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Topics (comma-separated)"),
                                    dbc.Textarea(
                                        id="topics-input",
                                        placeholder="Enter topics separated by commas (e.g., Algebra, Calculus, Geometry)",
                                        className="mb-3",
                                        rows=3
                                    )
                                ], width=12)
                            ]),
                            
                            # Study Duration
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Study Duration (days)"),
                                    dbc.Input(
                                        type="number",
                                        id="duration-input",
                                        min=1,
                                        max=365,
                                        value=30,
                                        className="mb-3"
                                    )
                                ], width=12)
                            ]),
                            
                            # Daily Study Hours
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Daily Study Hours"),
                                    dbc.Input(
                                        type="number",
                                        id="hours-input",
                                        min=1,
                                        max=12,
                                        value=2,
                                        className="mb-3"
                                    )
                                ], width=12)
                            ]),
                            
                            # Study Preferences
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Study Preferences"),
                                    dbc.Checklist(
                                        id="preferences-checklist",
                                        options=[
                                            {"label": "Morning Study", "value": "morning"},
                                            {"label": "Evening Study", "value": "evening"},
                                            {"label": "Night Study", "value": "night"},
                                            {"label": "Include Breaks", "value": "breaks"},
                                            {"label": "Include Practice Tests", "value": "practice"},
                                        ],
                                        value=["morning", "breaks"],
                                        className="mb-3"
                                    )
                                ], width=12)
                            ]),
                            
                            # Additional Notes
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Additional Notes"),
                                    dbc.Textarea(
                                        id="notes-textarea",
                                        placeholder="Enter any additional notes or requirements",
                                        className="mb-3"
                                    )
                                ], width=12)
                            ])
                        ])
                    ])
                ], className="mb-4")
            ], width=6),
            
            # Right Column - Generated Plans
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Your Study Plans", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(initial_plans, id="study-plans-list", className="mt-3")
                    ])
                ])
            ], width=6)
        ]),
        
        # Study Plan Modal
        dbc.Modal([
            dbc.ModalHeader([
                html.Div([
                    html.I(className="fas fa-calendar-alt me-2"),
                    html.H4("Generated Study Plan", className="mb-0")
                ])
            ]),
            dbc.ModalBody([
                html.Div(id="generated-plan-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Save Plan", id="save-plan-btn", color="primary"),
                dbc.Button("Close", id="close-plan-modal", color="secondary")
            ])
        ], id="plan-modal", is_open=False, size="lg"),
        
        # Hidden components
        dcc.Store(id="study-plans-store"),
    ], className="study-plan-container p-4")

def register_callbacks(app):
    # Update topics based on selected subject
    @app.callback(
        Output("topics-dropdown", "options"),
        [Input("subject-dropdown", "value")],
        prevent_initial_call=True
    )
    def update_topics(subject):
        if not subject:
            return []
            
        # Define topics for each subject
        topics = {
            "math": [
                {"label": "Algebra", "value": "algebra"},
                {"label": "Calculus", "value": "calculus"},
                {"label": "Geometry", "value": "geometry"},
                {"label": "Statistics", "value": "statistics"},
                {"label": "Trigonometry", "value": "trigonometry"}
            ],
            "physics": [
                {"label": "Mechanics", "value": "mechanics"},
                {"label": "Thermodynamics", "value": "thermodynamics"},
                {"label": "Electromagnetism", "value": "electromagnetism"},
                {"label": "Optics", "value": "optics"},
                {"label": "Quantum Physics", "value": "quantum"}
            ],
            "chemistry": [
                {"label": "Atomic Structure", "value": "atomic"},
                {"label": "Chemical Bonding", "value": "bonding"},
                {"label": "Reactions", "value": "reactions"},
                {"label": "Thermodynamics", "value": "thermo"},
                {"label": "Organic Chemistry", "value": "organic"}
            ],
            "biology": [
                {"label": "Cell Biology", "value": "cell"},
                {"label": "Genetics", "value": "genetics"},
                {"label": "Ecology", "value": "ecology"},
                {"label": "Evolution", "value": "evolution"},
                {"label": "Human Body", "value": "human"}
            ],
            "cs": [
                {"label": "Programming", "value": "programming"},
                {"label": "Data Structures", "value": "data_structures"},
                {"label": "Algorithms", "value": "algorithms"},
                {"label": "Database", "value": "database"},
                {"label": "Networking", "value": "networking"}
            ],
            "english": [
                {"label": "Grammar", "value": "grammar"},
                {"label": "Writing", "value": "writing"},
                {"label": "Reading", "value": "reading"},
                {"label": "Speaking", "value": "speaking"},
                {"label": "Vocabulary", "value": "vocabulary"}
            ],
            "history": [
                {"label": "Ancient History", "value": "ancient"},
                {"label": "Medieval History", "value": "medieval"},
                {"label": "Modern History", "value": "modern"},
                {"label": "World Wars", "value": "wars"},
                {"label": "Cultural History", "value": "cultural"}
            ],
            "geography": [
                {"label": "Physical Geography", "value": "physical"},
                {"label": "Human Geography", "value": "human"},
                {"label": "Climate", "value": "climate"},
                {"label": "Maps", "value": "maps"},
                {"label": "Resources", "value": "resources"}
            ]
        }
        
        return topics.get(subject, [])

    # Generate study plan
    @app.callback(
        [Output("plan-modal", "is_open"),
         Output("generated-plan-content", "children")],
        [Input("generate-plan-btn", "n_clicks")],
        [State("subject-input", "value"),
         State("topics-input", "value"),
         State("duration-input", "value"),
         State("hours-input", "value"),
         State("preferences-checklist", "value"),
         State("notes-textarea", "value")],
        prevent_initial_call=True
    )
    def generate_study_plan(n_clicks, subject, topics, duration, hours, preferences, notes):
        if not n_clicks:
            return False, None
            
        if not all([subject, topics, duration, hours]):
            return False, html.Div("Please fill in all required fields", style={"color": "red"})
            
        try:
            # Process topics from comma-separated string
            topics_list = [topic.strip() for topic in topics.split(',') if topic.strip()]
            if not topics_list:
                return False, html.Div("Please enter at least one topic", style={"color": "red"})
            
            # Define time slots based on preferences
            time_slots = {
                "morning": ["06:00-08:00", "08:00-10:00", "10:00-12:00"],
                "evening": ["14:00-16:00", "16:00-18:00"],
                "night": ["19:00-21:00", "21:00-23:00"]
            }
            
            available_slots = []
            for pref in preferences:
                if pref in time_slots:
                    available_slots.extend(time_slots[pref])
            
            if not available_slots:
                available_slots = time_slots["morning"]  # Default to morning if no preferences
                
            # Generate weekly schedule
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekly_schedule = []
            topics_cycle = topics_list.copy()
            
            # Calculate sessions per day
            daily_sessions = min(hours, len(available_slots))
            
            for day in days:
                day_schedule = []
                used_slots = available_slots[:daily_sessions]
                
                for slot in used_slots:
                    if "practice" in preferences and len(day_schedule) == 0:  # Add practice test in first slot
                        current_topic = f"Practice Test - {topics_cycle[0]}"
                    else:
                        current_topic = topics_cycle[0]
                        topics_cycle = topics_cycle[1:] + [topics_cycle[0]]  # Rotate topics
                    
                    session = {
                        "time": slot,
                        "topic": current_topic,
                        "duration": "2 hours"
                    }
                    
                    if "breaks" in preferences:
                        session["break"] = "15 minutes break after session"
                        
                    day_schedule.append(session)
                
                weekly_schedule.append({
                    "day": day,
                    "sessions": day_schedule
                })
            
            # Create a structured timetable display
            plan_content = html.Div([
                html.H5(f"{subject.title()} Weekly Study Schedule", className="mb-4"),
                html.Div([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6(day["day"], className="mb-0 fw-bold"),
                            className="bg-primary text-white"
                        ),
                        dbc.CardBody([
                            html.Table([
                                html.Thead([
                                    html.Tr([
                                        html.Th("Time", className="w-25"),
                                        html.Th("Topic", className="w-50"),
                                        html.Th("Notes", className="w-25")
                                    ])
                                ], className="table-dark"),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(session["time"], className="text-nowrap"),
                                        html.Td([
                                            html.Strong(session["topic"]),
                                            html.Br(),
                                            html.Small(session.get("break", ""), className="text-muted")
                                        ]),
                                        html.Td(session["duration"])
                                    ]) for session in day["sessions"]
                                ])
                            ], className="table table-bordered table-hover")
                        ])
                    ], className="mb-4 shadow-sm") for day in weekly_schedule
                ]),
                html.Div([
                    html.H6("Study Plan Notes:", className="mt-4 mb-3"),
                    html.Ul([
                        html.Li(f"Total duration: {duration} days"),
                        html.Li(f"Daily study hours: {hours} hours"),
                        html.Li(f"Topics rotation: {', '.join(topics_list)}"),
                        html.Li("Includes practice tests" if "practice" in preferences else ""),
                        html.Li("Regular breaks included" if "breaks" in preferences else ""),
                        html.Li(f"Additional notes: {notes}" if notes else "")
                    ], className="list-unstyled")
                ], className="mt-4 bg-light p-3 rounded")
            ])
            
            return True, plan_content
            
        except Exception as e:
            print(f"Error generating study plan: {str(e)}")
            return False, html.Div(f"Error generating study plan: {str(e)}", style={"color": "red"})

    # Save study plan
    @app.callback(
        [Output("study-plans-list", "children"),
         Output("plan-modal", "is_open", allow_duplicate=True)],
        [Input("save-plan-btn", "n_clicks")],
        [State("subject-input", "value"),
         State("topics-input", "value"),
         State("duration-input", "value"),
         State("hours-input", "value"),
         State("preferences-checklist", "value"),
         State("notes-textarea", "value"),
         State("generated-plan-content", "children")],
        prevent_initial_call=True
    )
    def save_study_plan(n_clicks, subject, topics, duration, hours, preferences, notes, plan_content):
        if not n_clicks:
            return dash.no_update, dash.no_update
            
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return html.Div("Session expired"), False
                
            # Process topics from comma-separated string
            topics_list = [topic.strip() for topic in topics.split(',') if topic.strip()]
            if not topics_list:
                return html.Div("Please enter at least one topic", style={"color": "red"}), False
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Create study plans table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    subject TEXT,
                    topics TEXT,
                    duration INTEGER,
                    hours_per_day INTEGER,
                    preferences TEXT,
                    notes TEXT,
                    created_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Insert the study plan
            cursor.execute('''
                INSERT INTO study_plans (
                    user_id, subject, topics, duration, hours_per_day,
                    preferences, notes, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                subject,
                json.dumps(topics_list),
                duration,
                hours,
                json.dumps(preferences),
                notes,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            
            # Refresh study plans list
            plans_list = get_study_plans_list(user_id)
            return plans_list, False
            
        except Exception as e:
            print(f"Error saving study plan: {str(e)}")
            return html.Div(f"Error saving study plan: {str(e)}", style={"color": "red"}), False

    # Close plan modal
    @app.callback(
        Output("plan-modal", "is_open", allow_duplicate=True),
        [Input("close-plan-modal", "n_clicks")],
        [State("plan-modal", "is_open")],
        prevent_initial_call=True
    )
    def close_plan_modal(n_clicks, is_open):
        if n_clicks:
            return False
        return is_open

    # View Plan callback
    @app.callback(
        [Output("plan-modal", "is_open", allow_duplicate=True),
         Output("generated-plan-content", "children", allow_duplicate=True)],
        [Input({"type": "view-plan", "index": dash.ALL}, "n_clicks")],
        [State("study-plans-store", "data")],
        prevent_initial_call=True
    )
    def view_study_plan(n_clicks, plans_data):
        if not n_clicks or not plans_data:
            return False, None
            
        ctx = dash.callback_context
        if not ctx.triggered:
            return False, None
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        plan_id = json.loads(button_id)["index"]
        
        # Find the plan in the data
        plan = next((p for p in plans_data if p["id"] == plan_id), None)
        if not plan:
            return False, html.Div("Plan not found", style={"color": "red"})
            
        # Create the schedule display
        schedule = []
        current_date = datetime.datetime.strptime(plan["created_date"], "%Y-%m-%d %H:%M:%S")
        
        for i in range(plan["duration"]):
            day_schedule = []
            day_hours = 0
            
            while day_hours < plan["hours_per_day"]:
                for topic in plan["topics"]:
                    if day_hours >= plan["hours_per_day"]:
                        break
                        
                    # Add study session
                    session_duration = min(2, plan["hours_per_day"] - day_hours)
                    end_hour = day_hours + session_duration
                    day_schedule.append({
                        "topic": topic,
                        "duration": session_duration,
                        "time": f"{format_time(day_hours)} - {format_time(end_hour)}"
                    })
                    day_hours += session_duration
                    
                    # Add break if preferred
                    if "breaks" in plan["preferences"] and day_hours < plan["hours_per_day"]:
                        break_end = day_hours + 0.5
                        day_schedule.append({
                            "topic": "Break",
                            "duration": 0.5,
                            "time": f"{format_time(day_hours)} - {format_time(break_end)}"
                        })
                        day_hours += 0.5
            
            schedule.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "sessions": day_schedule
            })
            current_date += datetime.timedelta(days=1)
        
        # Create the plan display
        plan_content = html.Div([
            html.H5(f"{plan['subject']} Study Schedule", className="mb-4"),
            html.Div([
                dbc.Card([
                    dbc.CardHeader(day["date"]),
                    dbc.CardBody([
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Time"),
                                    html.Th("Topic"),
                                    html.Th("Duration")
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(session["time"]),
                                    html.Td(session["topic"]),
                                    html.Td(f"{session['duration']} hours")
                                ]) for session in day["sessions"]
                            ])
                        ], className="table table-bordered")
                    ])
                ], className="mb-3") for day in schedule
            ])
        ])
        
        return True, plan_content

    # Delete Plan callback
    @app.callback(
        [Output("study-plans-list", "children", allow_duplicate=True),
         Output("study-plans-store", "data", allow_duplicate=True)],
        [Input({"type": "delete-plan", "index": dash.ALL}, "n_clicks")],
        [State("study-plans-store", "data")],
        prevent_initial_call=True
    )
    def delete_study_plan(n_clicks, plans_data):
        if not n_clicks or not plans_data:
            return dash.no_update, dash.no_update
            
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        plan_id = json.loads(button_id)["index"]
        
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return html.Div("Session expired"), None
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Delete the study plan
            cursor.execute("DELETE FROM study_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
            conn.commit()
            conn.close()
            
            # Refresh study plans list
            plans_list = get_study_plans_list(user_id)
            return plans_list, None
            
        except Exception as e:
            print(f"Error deleting study plan: {str(e)}")
            return html.Div(f"Error deleting study plan: {str(e)}", style={"color": "red"}), None

    # Update study plans store when plans list changes
    @app.callback(
        Output("study-plans-store", "data"),
        [Input("study-plans-list", "children")],
        prevent_initial_call=True
    )
    def update_study_plans_store(plans_list):
        if not plans_list or isinstance(plans_list, str):
            return None
            
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return None
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Get study plans
            cursor.execute('''
                SELECT id, subject, topics, duration, hours_per_day,
                       preferences, notes, created_date
                FROM study_plans
                WHERE user_id = ?
                ORDER BY created_date DESC
            ''', (user_id,))
            
            plans = cursor.fetchall()
            conn.close()
            
            if not plans:
                return None
                
            # Convert plans to list of dictionaries
            plans_data = []
            for plan_id, subject, topics, duration, hours, preferences, notes, created_date in plans:
                plans_data.append({
                    "id": plan_id,
                    "subject": subject,
                    "topics": json.loads(topics),
                    "duration": duration,
                    "hours_per_day": hours,
                    "preferences": json.loads(preferences),
                    "notes": notes,
                    "created_date": created_date
                })
            
            return plans_data
            
        except Exception as e:
            print(f"Error updating study plans store: {str(e)}")
            return None

def get_study_plans_list(user_id):
    """Get user's study plans list"""
    try:
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Get study plans
        cursor.execute('''
            SELECT id, subject, topics, duration, hours_per_day,
                   preferences, notes, created_date
            FROM study_plans
            WHERE user_id = ?
            ORDER BY created_date DESC
        ''', (user_id,))
        
        plans = cursor.fetchall()
        conn.close()
        
        if not plans:
            return html.Div("No study plans created yet")
            
        plans_list = []
        for plan_id, subject, topics, duration, hours, preferences, notes, created_date in plans:
            topics_list = json.loads(topics)
            preferences_list = json.loads(preferences)
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-book me-2"),
                            html.H5(f"{subject.title()} Study Plan", className="mb-0 d-inline")
                        ]),
                        dbc.Button(
                            html.I(className="fas fa-trash-alt"),
                            id={"type": "delete-plan", "index": plan_id},
                            color="danger",
                            className="float-end",
                            size="sm"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody([
                    html.P([
                        html.Strong("Topics: "),
                        ", ".join(topics_list)
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Duration: "),
                        f"{duration} days"
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Hours per day: "),
                        str(hours)
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Created: "),
                        created_date
                    ], className="mb-2"),
                    dbc.Button(
                        "View Plan",
                        id={"type": "view-plan", "index": plan_id},
                        color="primary",
                        className="btn-sm"
                    )
                ])
            ], className="mb-3")
            plans_list.append(card)
            
        return html.Div(plans_list)
        
    except Exception as e:
        print(f"Error getting study plans list: {str(e)}")
        return html.Div("Error loading study plans", style={"color": "red"})

def format_time(hour):
    """Convert 24-hour format to 12-hour format with AM/PM"""
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour-12}:00 PM"