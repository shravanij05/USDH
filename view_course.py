import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time
import json
from datetime import datetime
from flask import session

def is_valid_url(url):
    """Check if the URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def clean_html_content(html_content):
    """Clean and format HTML content for display"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'iframe', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Clean up the content
        content = soup.get_text()
        content = re.sub(r'\s+', ' ', content)  # Remove extra whitespace
        content = content.strip()
        
        return content if content else "No content available."
    except Exception as e:
        print(f"Error cleaning content: {str(e)}")
        return "Error processing content."

def fetch_course_content(url):
    """Fetch course content with proper error handling"""
    if not is_valid_url(url):
        return "Invalid URL provided."
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return clean_html_content(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content: {str(e)}")
        return f"Unable to load course content. Please try opening the link in a new tab."

def view_course():
    return html.Div([
        dbc.Container([
            # Back button
            dbc.Row([
                dbc.Col([
                    html.A([
                        html.I(className="fas fa-arrow-left me-2"),
                        "Back to Courses"
                    ], href="/user",
                        className="text-decoration-none text-light mb-3 d-inline-block")
                ])
            ]),
            
            # Course content area
            dbc.Row([
                dbc.Col([
                    html.Div(id="course-content", className="course-details-container")
                ])
            ]),

            # Modal for showing action status
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Course Status")),
                dbc.ModalBody(id="course-action-message"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-course-modal", className="ms-auto", n_clicks=0)
                )
            ], id="course-action-modal", is_open=False, centered=True)
        ], fluid=True, className="py-4")
    ], className="view-course-page")

def register_callbacks(app):
    def format_youtube_url(url):
        """Convert YouTube URL to embed format"""
        if not url or not isinstance(url, str):
            return None
            
        try:
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('watch?v=')[1].split('&')[0]
                return f"https://www.youtube.com/embed/{video_id}"
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1]
                return f"https://www.youtube.com/embed/{video_id}"
            elif 'youtube.com/embed/' in url:
                return url
            return None
        except:
            return None

    @app.callback(
        Output("course-content", "children"),
        [Input("url", "pathname")]
    )
    def display_course_details(pathname):
        try:
            # Extract course type and ID from URL
            path_parts = pathname.split('/')
            course_type = path_parts[-2]  # 'course' or 'course2'
            course_id = path_parts[-1]
            
            # Connect to database and fetch course details
            conn = sqlite3.connect('data/USDH.db')
            table_name = "courses" if course_type == "course" else "courses2"
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            conn.close()
            
            # Find the course by index
            try:
                course_index = int(course_id)
                if course_index >= len(df):
                    raise ValueError("Course index out of range")
                course = df.iloc[course_index]
            except (ValueError, IndexError):
                return html.Div([
                    html.H3("Course Not Found", className="text-danger"),
                    html.P("The requested course could not be found.")
                ])
            
            if course_type == "course":
                # Format YouTube URL if available
                trailer_url = format_youtube_url(course['trailer']) if pd.notna(course['trailer']) else None
                
                # UG/PG Course layout
                course_content = html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1(course['course_name_'], className="mb-3"),
                            html.Div([
                                html.P([html.Strong("Discipline: "), course['dispcipline']], className="mb-2"),
                                html.P([html.Strong("Duration: "), course['duration']], className="mb-2"),
                                html.P([html.Strong("Level: "), course['_ug/pg']], className="mb-2"),
                                html.P(course['description'], className="mt-3"),
                            ]),
                            # Show trailer if available
                            html.Div([
                                html.H5("Course Trailer", className="mt-4 mb-3"),
                                html.Div([
                                    html.Iframe(
                                        src=trailer_url,
                                        width="100%",
                                        height="315px",
                                        style={"border": "none"},
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    ) if trailer_url else html.P("No trailer available")
                                ], style={"max-width": "560px", "margin": "0 auto"})
                            ]),
                            # Action buttons container
                            html.Div([
                                dbc.Button(
                                    "Open Course",
                                    href=course['course_link'],
                                    target="_blank",
                                    color="primary",
                                    size="lg",
                                    className="me-2"
                                ),
                            ], className="mt-4 d-flex flex-wrap gap-2")
                        ])
                    ])
                ])
                
            else:
                # School Course layout with similar buttons
                course_content = html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1(f"{course['subjects']} - {course['grade']}", className="mb-3"),
                            html.Div([
                                html.P([html.Strong("Subject: "), course['subjects']], className="mb-2"),
                                html.P([html.Strong("Grade: "), course['grade']], className="mb-2"),
                                html.P([html.Strong("Website: "), course['website_name']], className="mb-2"),
                            ]),
                            # Action buttons container
                            html.Div([
                                dbc.Button(
                                    "Open Resource",
                                    href=course['video_link'],
                                    target="_blank",
                                    color="primary",
                                    size="lg",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Add to Ongoing",
                                    id={"type": "add-ongoing", "index": course_index},
                                    color="success",
                                    size="lg",
                                    className="me-2",
                                    n_clicks=0
                                ),
                                dbc.Button(
                                    "Add to Completed",
                                    id={"type": "add-completed", "index": course_index},
                                    color="info",
                                    size="lg",
                                    n_clicks=0
                                )
                            ], className="mt-4 d-flex flex-wrap gap-2")
                        ])
                    ])
                ])
            
            return html.Div([
                # Back button
                dbc.Button(
                    [html.I(className="fas fa-arrow-left me-2"), "Back"],
                    href="/user",
                    color="secondary",
                    className="mb-4"
                ),
                course_content
            ])
            
        except Exception as e:
            print(f"Error loading course details: {str(e)}")
            return html.Div([
                html.H3("Error Loading Course", className="text-danger"),
                html.P(f"An error occurred while loading the course details: {str(e)}")
            ])

    # Course status buttons callback
    