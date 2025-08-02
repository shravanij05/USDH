import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
from flask import session
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import os
import json
from jinja2 import Template
import base64
import jinja2
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def resume_maker():
    """
    Resume maker application layout
    """
    # Check if user is logged in
    if 'user_id' not in session:
        return html.Div([
            html.H3("Please log in to use the Resume Maker"),
            html.A("Go to Login", href="/", className="btn btn-primary")
        ])
    
    return html.Div([
        html.H2("Resume Maker", className="mb-4"),
        dbc.Button("Back to Dashboard", href="/user", color="secondary", className="mb-3"),
        
        # Personal Information
        html.Div([
            html.H4("Personal Information", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Full Name"),
                    dbc.Input(id="full-name", type="text", placeholder="Enter your full name", className="mb-3"),
                ], width=6),
                dbc.Col([
                    html.Label("Email"),
                    dbc.Input(id="email", type="email", placeholder="Enter your email", className="mb-3"),
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Phone"),
                    dbc.Input(id="phone", type="text", placeholder="Enter your phone number", className="mb-3"),
                ], width=6),
                dbc.Col([
                    html.Label("Location"),
                    dbc.Input(id="location", type="text", placeholder="City, State", className="mb-3"),
                ], width=6),
            ]),
            dbc.Input(id="profile-summary", type="text", placeholder="Brief professional summary", className="mb-3"),
        ], className="mb-4"),
        
        # Education
        html.Div([
            html.H4("Education", className="mb-3"),
            html.Div(id="education-container"),
            dbc.Button("Add Education", id="add-education", color="primary", className="mt-2"),
        ], className="mb-4"),
        
        # Experience
        html.Div([
            html.H4("Experience", className="mb-3"),
            html.Div(id="experience-container"),
            dbc.Button("Add Experience", id="add-experience", color="primary", className="mt-2"),
        ], className="mb-4"),
        
        # Skills
        html.Div([
            html.H4("Skills", className="mb-3"),
            dbc.Input(id="skills", type="text", placeholder="Enter skills separated by commas", className="mb-3"),
        ], className="mb-4"),
        
        # Certifications
        html.Div([
            html.H4("Certifications", className="mb-3"),
            html.Div(id="certification-container"),
            dbc.Button("Add Certification", id="add-certification", color="primary", className="mt-2"),
        ], className="mb-4"),
        
        # User's Saved Certifications
        html.Div([
            html.H4("Your Saved Certifications", className="mb-3"),
            html.Div(id="saved-certifications-container", className="mb-3"),
        ], className="mb-4"),
        
        # Template Selection
        html.Div([
            html.H4("Choose Template", className="mb-3"),
            dbc.RadioItems(
                id="template-selection",
                options=[
                    {"label": "Professional", "value": "professional"},
                    {"label": "Modern", "value": "modern"},
                    {"label": "Creative", "value": "creative"},
                ],
                value="professional",
                inline=True,
                className="mb-3",
            ),
        ], className="mb-4"),
        
        # Generate Button
        dbc.Button("Generate Resume", id="generate-resume-btn", color="success", className="mb-4"),
        
        # Result Display
        html.Div(id="resume-output", className="mb-4"),
        
        # Download History
        html.Div([
            html.H4("Download History", className="mb-3"),
            html.Div(id="download-history", className="download-history"),
        ], className="mb-4"),
        
        # Hidden components
        dcc.Download(id="resume-download"),
        dcc.Store(id="resume-data-store"),
    ], className="container py-4")

def register_callbacks(app):
    # Load user's saved certifications on page load
    @app.callback(
        Output("saved-certifications-container", "children"),
        [Input("url", "pathname")]
    )
    def load_saved_certifications(pathname):
        if pathname != "/resume-maker":
            return dash.no_update
        
        # Check if user is logged in
        if 'user_id' not in session:
            return html.Div("Please log in to view your certifications")
        
        user_id = session['user_id']
        
        try:
            # Connect to database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # First check if certificates table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='certificates'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
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
                conn.commit()
                
            # Try to query certificates with expected columns
            try:
                cursor.execute("SELECT id, name, organization, issue_date FROM certificates WHERE user_id = ?", (user_id,))
                certifications = cursor.fetchall()
            except sqlite3.OperationalError:
                # Fall back to older schema if needed
                try:
                    cursor.execute("SELECT id, course_name, completion_date FROM certificates WHERE user_id = ?", (user_id,))
                    certifications = [(cert_id, course_name, "Unknown organization", completion_date) for cert_id, course_name, completion_date in cursor.fetchall()]
                except sqlite3.OperationalError:
                    # If both fail, table might exist but with different columns
                    return html.Div("Certificate data format is not compatible. Please check database schema.")
            
            conn.close()
            
            if not certifications:
                return html.Div("No certifications found. Complete courses to earn certifications.")
            
            # Create list of user's certifications with "Add to Resume" buttons
            certification_items = []
            for cert_id, name, organization, issue_date in certifications:
                certification_items.append(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5(name, className="card-title"),
                            html.P(f"{organization} - {issue_date}", className="card-text"),
                            dbc.Button(
                                "Add to Resume", 
                                id={"type": "add-saved-cert", "index": cert_id},
                                color="primary",
                                size="sm",
                                className="mt-2"
                            )
                        ]),
                        className="mb-2"
                    )
                )
            
            return html.Div(certification_items)
            
        except Exception as e:
            print(f"Error loading certifications: {str(e)}")
            return html.Div(f"Error loading certifications: {str(e)}")
    
    # Callback to add a saved certificate to the resume
    @app.callback(
        Output("certification-container", "children", allow_duplicate=True),
        [Input({"type": "add-saved-cert", "index": dash.ALL}, "n_clicks")],
        [State("certification-container", "children")],
        prevent_initial_call=True
    )
    def add_saved_certification_to_resume(n_clicks, existing_certifications):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        
        # Get the button ID that was clicked
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        cert_id = button_id['index']
        
        try:
            # Get certificate details from the database
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Try with new schema first
            try:
                cursor.execute("SELECT name, issue_date FROM certificates WHERE id = ?", (cert_id,))
                cert_data = cursor.fetchone()
            except sqlite3.OperationalError:
                # Fall back to old schema
                cursor.execute("SELECT course_name, completion_date FROM certificates WHERE id = ?", (cert_id,))
                cert_data = cursor.fetchone()
            
            conn.close()
            
            if not cert_data:
                return dash.no_update
            
            cert_name, cert_date = cert_data
            
            # Initialize existing_certifications if it's None
            if existing_certifications is None:
                existing_certifications = []
            
            # Add the new certification card
            current_index = len(existing_certifications)
            new_cert_card = create_certification_card(current_index)
            
            # Create a complete new card with the certificate data directly embedded
            try:
                # Create a new card with values pre-populated
                return existing_certifications + [
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Certificate Name"),
                                    dbc.Input(
                                        id={"type": "cert-name", "index": current_index}, 
                                        type="text", 
                                        placeholder="Enter certificate name", 
                                        className="mb-2",
                                        value=cert_name
                                    ),
                                ], width=6),
                                dbc.Col([
                                    html.Label("Issuing Date"),
                                    dbc.Input(
                                        id={"type": "cert-date", "index": current_index}, 
                                        type="text", 
                                        placeholder="Enter issuing date", 
                                        className="mb-2",
                                        value=cert_date
                                    ),
                                ], width=6),
                            ], className="mb-3"),
                            dbc.Button(
                                "Remove", 
                                id={"type": "remove-cert", "index": current_index},
                                color="danger",
                                size="sm",
                                className="mt-1"
                            ),
                        ]),
                        className="mb-3",
                    )
                ]
            except Exception as e:
                print(f"Error creating certification card: {str(e)}")
                return existing_certifications + [new_cert_card]
            
        except Exception as e:
            print(f"Error adding saved certification: {str(e)}")
            return dash.no_update
    
    # Callback to add education entry - FIXED
    @app.callback(
        Output("education-container", "children"),
        [Input("add-education", "n_clicks")],
        [State("education-container", "children")],
        prevent_initial_call=True
    )
    def add_education(n_clicks, existing_children):
        if not n_clicks:
            return dash.no_update
        
        # Get the current index for the new card
        current_index = len(existing_children) if existing_children else 0
        new_education = create_education_card(current_index)
        
        if existing_children:
            return existing_children + [new_education]
        return [new_education]
    
    # Callback to remove education entry
    @app.callback(
        Output("education-container", "children", allow_duplicate=True),
        [Input({"type": "remove-edu", "index": dash.ALL}, "n_clicks")],
        [State("education-container", "children")],
        prevent_initial_call=True
    )
    def remove_education(n_clicks, children):
        if not dash.callback_context.triggered or not any(n_clicks):
            return dash.no_update
        
        ctx = dash.callback_context
        try:
            # Find which button was clicked
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            button_dict = json.loads(button_id)
            index_to_remove = button_dict["index"]
            
            print(f"Removing education at index: {index_to_remove}")
            
            # If children is None or empty, nothing to remove
            if not children or len(children) == 0:
                return dash.no_update
            
            # Find the card with the matching remove button ID and remove it
            new_children = []
            for i, child in enumerate(children):
                # Skip the card with the matching index
                if i != index_to_remove:
                    # Update the remove button index to match its new position if needed
                    new_children.append(child)
            
            # If we have no children left, return an empty list instead of None
            if not new_children:
                return []
            
            return new_children
        except Exception as e:
            print(f"Error removing education: {str(e)}")
            return dash.no_update
    
    # Callback to add experience entry - FIXED
    @app.callback(
        Output("experience-container", "children"),
        [Input("add-experience", "n_clicks")],
        [State("experience-container", "children")],
        prevent_initial_call=True
    )
    def add_experience(n_clicks, existing_children):
        if not n_clicks:
            return dash.no_update
        
        # Get the current index for the new card
        current_index = len(existing_children) if existing_children else 0
        new_experience = create_experience_card(current_index)
        
        if existing_children:
            return existing_children + [new_experience]
        return [new_experience]
    
    # Callback to remove experience entry
    @app.callback(
        Output("experience-container", "children", allow_duplicate=True),
        [Input({"type": "remove-exp", "index": dash.ALL}, "n_clicks")],
        [State("experience-container", "children")],
        prevent_initial_call=True
    )
    def remove_experience(n_clicks, children):
        if not dash.callback_context.triggered or not any(n_clicks):
            return dash.no_update
        
        ctx = dash.callback_context
        try:
            # Find which button was clicked
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            button_dict = json.loads(button_id)
            index_to_remove = button_dict["index"]
            
            print(f"Removing experience at index: {index_to_remove}")
            
            # If children is None or empty, nothing to remove
            if not children or len(children) == 0:
                return dash.no_update
            
            # Find the card with the matching remove button ID and remove it
            new_children = []
            for i, child in enumerate(children):
                # Skip the card with the matching index
                if i != index_to_remove:
                    # Update the remove button index to match its new position if needed
                    new_children.append(child)
            
            # If we have no children left, return an empty list instead of None
            if not new_children:
                return []
            
            return new_children
        except Exception as e:
            print(f"Error removing experience: {str(e)}")
            return dash.no_update
    
    # Callback to add certification entry - FIXED
    @app.callback(
        Output("certification-container", "children"),
        [Input("add-certification", "n_clicks")],
        [State("certification-container", "children")],
        prevent_initial_call=True
    )
    def add_certification(n_clicks, existing_children):
        if not n_clicks:
            return dash.no_update
        
        # Get the current index for the new card
        current_index = len(existing_children) if existing_children else 0
        new_certification = create_certification_card(current_index)
        
        if existing_children:
            return existing_children + [new_certification]
        return [new_certification]
    
    # Callback to remove certification entry
    @app.callback(
        Output("certification-container", "children", allow_duplicate=True),
        [Input({"type": "remove-cert", "index": dash.ALL}, "n_clicks")],
        [State("certification-container", "children")],
        prevent_initial_call=True
    )
    def remove_certification(n_clicks, children):
        if not dash.callback_context.triggered or not any(n_clicks):
            return dash.no_update
        
        ctx = dash.callback_context
        try:
            # Find which button was clicked
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            button_dict = json.loads(button_id)
            index_to_remove = button_dict["index"]
            
            print(f"Removing certification at index: {index_to_remove}")
            
            # If children is None or empty, nothing to remove
            if not children or len(children) == 0:
                return dash.no_update
            
            # Find the card with the matching remove button ID and remove it
            new_children = []
            for i, child in enumerate(children):
                # Skip the card with the matching index
                if i != index_to_remove:
                    # Update the remove button index to match its new position if needed
                    new_children.append(child)
            
            # If we have no children left, return an empty list instead of None
            if not new_children:
                return []
            
            return new_children
        except Exception as e:
            print(f"Error removing certification: {str(e)}")
            return dash.no_update
        
    # Callback to generate resume
    @app.callback(
        [Output("resume-output", "children"),
         Output("resume-download", "data"),
         Output("download-history", "children")],
        [Input("generate-resume-btn", "n_clicks")],
        [State("full-name", "value"),
         State("email", "value"),
         State("phone", "value"),
         State("location", "value"),
         State("profile-summary", "value"),
         State("education-container", "children"),
         State("experience-container", "children"),
         State("certification-container", "children"),
         State("skills", "value"),
         State("template-selection", "value")],
        prevent_initial_call=True
    )
    def generate_resume(n_clicks, full_name, email, phone, location, summary, education, experience, certifications, skills, template):
        if not n_clicks:
            return dash.no_update, dash.no_update, dash.no_update
        
        # If user is not logged in, don't generate resume
        if 'user_id' not in session:
            return html.Div("Please log in to generate a resume"), dash.no_update, dash.no_update
        
        # Get user ID
        user_id = session['user_id']
        
        # Debug info
        print(f"Generating resume for user: {user_id}")
        print(f"Using template: {template}")
        
        try:
            # Basic validation
            if not full_name:
                full_name = "Your Name"
            if not email:
                email = "your.email@example.com"
            if not phone:
                phone = ""
            if not location:
                location = ""
            if not summary:
                summary = ""
            
            # Skills processing
            skill_list = []
            if skills:
                skill_list = [skill.strip() for skill in skills.split(",") if skill.strip()]
            
            # Process education data - FIXED
            education_data = []
            try:
                if education:
                    for edu_idx, edu in enumerate(education):
                        try:
                            # Extract values directly without using traverse_tree
                            edu_card_body = edu.get('props', {}).get('children', {})
                            
                            # Extract data from the rows in the card
                            rows = edu_card_body.get('props', {}).get('children', [])
                            institution = ""
                            degree = ""
                            start_date = ""
                            end_date = ""
                            
                            # If rows are present, try to extract values from the expected structure
                            if rows and isinstance(rows, list) and len(rows) >= 2:
                                # First row has institution and degree
                                first_row = rows[0]
                                cols = first_row.get('props', {}).get('children', [])
                                if cols and isinstance(cols, list) and len(cols) >= 2:
                                    # Get institution
                                    institution_input = cols[0].get('props', {}).get('children', [])[1]
                                    institution = institution_input.get('props', {}).get('value', f"Institution {edu_idx + 1}")
                                    
                                    # Get degree
                                    degree_input = cols[1].get('props', {}).get('children', [])[1]
                                    degree = degree_input.get('props', {}).get('value', f"Degree {edu_idx + 1}")
                                
                                # Second row has start and end dates
                                second_row = rows[1]
                                cols = second_row.get('props', {}).get('children', [])
                                if cols and isinstance(cols, list) and len(cols) >= 2:
                                    # Get start date
                                    start_input = cols[0].get('props', {}).get('children', [])[1]
                                    start_date = start_input.get('props', {}).get('value', "")
                                    
                                    # Get end date
                                    end_input = cols[1].get('props', {}).get('children', [])[1]
                                    end_date = end_input.get('props', {}).get('value', "")
                            
                            # Use fallback values if extraction fails
                            if not institution:
                                institution = f"Institution {edu_idx + 1}"
                            if not degree:
                                degree = f"Degree {edu_idx + 1}"
                            
                            edu_data = {
                                "institution": institution,
                                "degree": degree,
                                "start_date": start_date,
                                "end_date": end_date,
                            }
                            education_data.append(edu_data)
                            
                        except Exception as e:
                            print(f"Error processing education entry: {str(e)}")
                            # Add a placeholder entry
                            education_data.append({
                                "institution": f"Institution {len(education_data) + 1}",
                                "degree": f"Degree {len(education_data) + 1}",
                                "start_date": "",
                                "end_date": "",
                            })
            except Exception as e:
                print(f"Error processing education data: {str(e)}")
                education_data = [{"institution": "Your Institution", "degree": "Your Degree", "start_date": "", "end_date": ""}]
            
            # Process experience data - FIXED
            experience_data = []
            try:
                if experience:
                    for exp_idx, exp in enumerate(experience):
                        try:
                            # Extract values directly without using traverse_tree
                            exp_card_body = exp.get('props', {}).get('children', {})
                            
                            # Extract data from the rows in the card
                            rows = exp_card_body.get('props', {}).get('children', [])
                            company = ""
                            position = ""
                            start_date = ""
                            end_date = ""
                            description = ""
                            
                            # If rows are present, try to extract values from the expected structure
                            if rows and isinstance(rows, list) and len(rows) >= 3:
                                # First row has company and position
                                first_row = rows[0]
                                cols = first_row.get('props', {}).get('children', [])
                                if cols and isinstance(cols, list) and len(cols) >= 2:
                                    # Get company
                                    company_input = cols[0].get('props', {}).get('children', [])[1]
                                    company = company_input.get('props', {}).get('value', f"Company {exp_idx + 1}")
                                    
                                    # Get position
                                    position_input = cols[1].get('props', {}).get('children', [])[1]
                                    position = position_input.get('props', {}).get('value', f"Position {exp_idx + 1}")
                                
                                # Second row has start and end dates
                                second_row = rows[1]
                                cols = second_row.get('props', {}).get('children', [])
                                if cols and isinstance(cols, list) and len(cols) >= 2:
                                    # Get start date
                                    start_input = cols[0].get('props', {}).get('children', [])[1]
                                    start_date = start_input.get('props', {}).get('value', "")
                                    
                                    # Get end date
                                    end_input = cols[1].get('props', {}).get('children', [])[1]
                                    end_date = end_input.get('props', {}).get('value', "")
                                
                                # Third row has description
                                third_row = rows[2]
                                cols = third_row.get('props', {}).get('children', [])
                                if cols and isinstance(cols, list) and len(cols) >= 1:
                                    # Get description
                                    desc_input = cols[0].get('props', {}).get('children', [])[1]
                                    description = desc_input.get('props', {}).get('value', "")
                            
                            # Use fallback values if extraction fails
                            if not company:
                                company = f"Company {exp_idx + 1}"
                            if not position:
                                position = f"Position {exp_idx + 1}"
                            
                            exp_data = {
                                "company": company,
                                "position": position,
                                "start_date": start_date,
                                "end_date": end_date,
                                "description": description,
                            }
                            experience_data.append(exp_data)
                            
                        except Exception as e:
                            print(f"Error processing experience entry: {str(e)}")
                            experience_data.append({
                                "company": f"Company {len(experience_data) + 1}",
                                "position": f"Position {len(experience_data) + 1}",
                                "start_date": "",
                                "end_date": "",
                                "description": "",
                            })
            except Exception as e:
                print(f"Error processing experience data: {str(e)}")
                experience_data = [{"company": "Your Company", "position": "Your Position", "start_date": "", "end_date": "", "description": ""}]
            
            # Process certification data - FIXED
            certification_data = []
            try:
                if certifications:
                    for cert_idx, cert in enumerate(certifications):
                        try:
                            # Extract values directly without using traverse_tree
                            cert_card_body = cert.get('props', {}).get('children', {})
                            
                            # Extract data from the rows in the card
                            rows = cert_card_body.get('props', {}).get('children', [])
                            name = ""
                            date = ""
                            
                            # If rows are present, try to extract values from the expected structure
                            if rows and isinstance(rows, list) and len(rows) >= 1:
                                # First row has name and date
                                first_row = rows[0]
                                cols = first_row.get('props', {}).get('children', [])
                                if cols and isinstance(cols, list) and len(cols) >= 2:
                                    # Get name
                                    name_input = cols[0].get('props', {}).get('children', [])[1]
                                    name = name_input.get('props', {}).get('value', f"Certificate {cert_idx + 1}")
                                    
                                    # Get date
                                    date_input = cols[1].get('props', {}).get('children', [])[1]
                                    date = date_input.get('props', {}).get('value', "")
                            
                            # Use fallback values if extraction fails
                            if not name:
                                name = f"Certificate {cert_idx + 1}"
                            
                            cert_data = {
                                "name": name,
                                "date": date,
                            }
                            certification_data.append(cert_data)
                            
                        except Exception as e:
                            print(f"Error processing certification entry: {str(e)}")
                            certification_data.append({
                                "name": f"Certificate {len(certification_data) + 1}",
                                "date": "",
                            })
            except Exception as e:
                print(f"Error processing certification data: {str(e)}")
                certification_data = []
            
            # Resume data
            resume_data = {
                "personal_info": {
                    "name": full_name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "summary": summary,
                },
                "education": education_data,
                "experience": experience_data,
                "skills": skill_list,
                "certifications": certification_data,
                "template": template,
            }
            
            # Get template based on selection
            template_path = f"templates/{template}_template.html"
            
            # Check if template file exists
            if not os.path.exists(template_path):
                # Use default template if selected one doesn't exist
                template_path = "templates/professional_template.html"
            
            # Generate HTML from template
            try:
                with open(template_path, 'r') as f:
                    template_content = f.read()
                    
                # Add template identifier class to body
                template_content = template_content.replace('<body>', f'<body class="{template}-template">')
                    
                # Render template with Jinja2 - rename template variable to avoid collision
                jinja_template = jinja2.Template(template_content)
                rendered_html = jinja_template.render(**resume_data)
                
                # Inject style to ensure template styles are applied in preview
                style_tag = '''
                    <style>
                        iframe {
                            width: 100% !important;
                            height: 800px !important;
                            border: 1px solid #ddd;
                        }
                        @media print {
                            body {
                                width: 100% !important;
                                margin: 0 !important;
                                padding: 0 !important;
                            }
                        }
                    </style>
                '''
                rendered_html = rendered_html.replace('</head>', f'{style_tag}</head>')
                
                # Save HTML to temporary file
                tmp_html_path = f"tmp/resume_{user_id}_{int(time.time())}.html"
                os.makedirs(os.path.dirname(tmp_html_path), exist_ok=True)
                
                with open(tmp_html_path, 'w') as f:
                    f.write(rendered_html)
                
                # Try to generate PDF
                pdf_success = False
                pdf_path = tmp_html_path.replace(".html", ".pdf")
                rendered_pdf = None
                
                try:
                    # PDF generation using reportlab with enhanced styling
                    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                    styles = getSampleStyleSheet()
                    
                    # Create custom styles based on selected template
                    if template == "professional":
                        # Professional template styles
                        title_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Title'],
                            fontSize=24,
                            spaceAfter=20,
                            alignment=1,  # Center alignment
                            fontName='Helvetica-Bold'
                        )
                        heading_style = ParagraphStyle(
                            'CustomHeading',
                            parent=styles['Heading2'],
                            fontSize=14,
                            spaceBefore=15,
                            spaceAfter=10,
                            textColor=colors.black,
                            borderWidth=1,
                            borderPadding=5,
                            borderColor=colors.black,
                            fontName='Helvetica-Bold'
                        )
                        normal_style = ParagraphStyle(
                            'CustomNormal',
                            parent=styles['Normal'],
                            fontSize=10,
                            textColor=colors.black,
                            fontName='Helvetica'
                        )
                        italic_style = ParagraphStyle(
                            'CustomItalic',
                            parent=styles['Italic'],
                            fontSize=10,
                            textColor=colors.gray,
                            fontName='Helvetica-Oblique'
                        )
                    elif template == "modern":
                        # Modern template styles with enhanced visual elements
                        title_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Title'],
                            fontSize=28,
                            spaceAfter=25,
                            alignment=1,
                            fontName='Helvetica-Bold',
                            textColor=colors.HexColor('#2b6cb0'),  # Matching the preview blue
                            leading=35
                        )
                        
                        heading_style = ParagraphStyle(
                            'CustomHeading',
                            parent=styles['Heading2'],
                            fontSize=16,
                            spaceBefore=20,
                            spaceAfter=12,
                            textColor=colors.HexColor('#2b6cb0'),
                            leftIndent=0,
                            fontName='Helvetica-Bold',
                            leading=20,
                            borderWidth=0,
                            borderPadding=0
                        )
                        
                        normal_style = ParagraphStyle(
                            'CustomNormal',
                            parent=styles['Normal'],
                            fontSize=11,
                            textColor=colors.HexColor('#2d3748'),  # Darker gray for better readability
                            fontName='Helvetica',
                            leading=16,
                            spaceBefore=4
                        )
                        
                        italic_style = ParagraphStyle(
                            'CustomItalic',
                            parent=styles['Italic'],
                            fontSize=11,
                            textColor=colors.HexColor('#718096'),  # Modern gray
                            fontName='Helvetica-Oblique',
                            leading=16
                        )
                        
                        contact_style = ParagraphStyle(
                            'ContactInfo',
                            parent=styles['Normal'],
                            fontSize=12,
                            textColor=colors.HexColor('#4a5568'),
                            fontName='Helvetica',
                            alignment=1,  # Center alignment
                            leading=18
                        )
                        
                        # Additional styles for modern layout
                        section_style = ParagraphStyle(
                            'SectionStyle',
                            parent=styles['Normal'],
                            fontSize=11,
                            textColor=colors.HexColor('#2d3748'),
                            fontName='Helvetica',
                            leading=16,
                            leftIndent=10,
                            spaceBefore=6,
                            spaceAfter=6
                        )
                    else:  # creative
                        # Creative template styles
                        title_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Title'],
                            fontSize=24,
                            spaceAfter=20,
                            alignment=1,
                            fontName='Helvetica-Bold',
                            textColor=colors.HexColor('#ff6b6b')
                        )
                        heading_style = ParagraphStyle(
                            'CustomHeading',
                            parent=styles['Heading2'],
                            fontSize=16,
                            spaceBefore=15,
                            spaceAfter=10,
                            textColor=colors.HexColor('#ff6b6b'),
                            fontName='Helvetica-Bold'
                        )
                        normal_style = ParagraphStyle(
                            'CustomNormal',
                            parent=styles['Normal'],
                            fontSize=10,
                            textColor=colors.black,
                            fontName='Helvetica'
                        )
                        italic_style = ParagraphStyle(
                            'CustomItalic',
                            parent=styles['Italic'],
                            fontSize=10,
                            textColor=colors.HexColor('#95a5a6'),
                            fontName='Helvetica-Oblique'
                        )
                    
                    # Build content with enhanced modern template layout
                    elements = []
                    
                    if template == "modern":
                        # Add some top margin
                        elements.append(Spacer(1, 30))
                        
                        # Header with blue background simulation
                        elements.append(Paragraph(resume_data["personal_info"]["name"], title_style))
                        contact_info = f"{resume_data['personal_info']['email']} | {resume_data['personal_info']['phone']} | {resume_data['personal_info']['location']}"
                        elements.append(Paragraph(contact_info, contact_style))
                        elements.append(Spacer(1, 25))
                        
                        # Summary section with modern styling
                        if resume_data["personal_info"]["summary"]:
                            elements.append(Paragraph("Professional Summary", heading_style))
                            elements.append(Paragraph(resume_data["personal_info"]["summary"], section_style))
                            elements.append(Spacer(1, 15))
                        
                        # Education section with enhanced layout
                        if resume_data["education"]:
                            elements.append(Paragraph("Education", heading_style))
                            for edu in resume_data["education"]:
                                edu_table_data = [
                                    [Paragraph(f"<b>{edu['institution']}</b>", section_style)],
                                    [Paragraph(f"{edu['degree']}", section_style)],
                                    [Paragraph(f"{edu['start_date']} - {edu['end_date']}", italic_style)]
                                ]
                                edu_table = Table(edu_table_data, colWidths=[450])
                                edu_table.setStyle(TableStyle([
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                                ]))
                                elements.append(edu_table)
                                elements.append(Spacer(1, 10))
                        
                        # Experience section with enhanced layout
                        if resume_data["experience"]:
                            elements.append(Paragraph("Work Experience", heading_style))
                            for exp in resume_data["experience"]:
                                exp_table_data = [
                                    [Paragraph(f"<b>{exp['company']}</b>", section_style)],
                                    [Paragraph(f"{exp['position']}", section_style)],
                                    [Paragraph(f"{exp['start_date']} - {exp['end_date']}", italic_style)]
                                ]
                                if exp["description"]:
                                    exp_table_data.append([Paragraph(exp["description"], section_style)])
                                
                                exp_table = Table(exp_table_data, colWidths=[450])
                                exp_table.setStyle(TableStyle([
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                                ]))
                                elements.append(exp_table)
                                elements.append(Spacer(1, 15))
                        
                        # Skills section with grid layout
                        if resume_data["skills"]:
                            elements.append(Paragraph("Skills", heading_style))
                            skill_data = []
                            row = []
                            for i, skill in enumerate(resume_data["skills"], 1):
                                skill_text = f'<para backColor="#ebf4ff" textColor="#2b6cb0">{skill}</para>'
                                row.append(Paragraph(skill_text, section_style))
                                if i % 3 == 0 or i == len(resume_data["skills"]):
                                    while len(row) < 3:
                                        row.append("")
                                    skill_data.append(row)
                                    row = []
                            if row:
                                while len(row) < 3:
                                    row.append("")
                                skill_data.append(row)
                            
                            if skill_data:
                                skill_table = Table(skill_data, colWidths=[150] * 3, rowHeights=25)
                                skill_table.setStyle(TableStyle([
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                ]))
                                elements.append(skill_table)
                            elements.append(Spacer(1, 15))
                        
                        # Certifications section with enhanced layout
                        if resume_data["certifications"]:
                            elements.append(Paragraph("Certifications", heading_style))
                            for cert in resume_data["certifications"]:
                                cert_table_data = [
                                    [Paragraph(f"<b>{cert['name']}</b>", section_style)],
                                    [Paragraph(cert["date"], italic_style) if cert["date"] else ""]
                                ]
                                cert_table = Table(cert_table_data, colWidths=[450])
                                cert_table.setStyle(TableStyle([
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                                ]))
                                elements.append(cert_table)
                                elements.append(Spacer(1, 8))
                    else:
                        # Original content building for other templates
                        elements.append(Paragraph(resume_data["personal_info"]["name"], title_style))
                        contact_info = f"{resume_data['personal_info']['email']} | {resume_data['personal_info']['phone']} | {resume_data['personal_info']['location']}"
                        elements.append(Paragraph(contact_info, normal_style))
                        elements.append(Spacer(1, 20))
                        
                        # Summary section
                        if resume_data["personal_info"]["summary"]:
                            elements.append(Paragraph("Professional Summary", heading_style))
                            elements.append(Paragraph(resume_data["personal_info"]["summary"], normal_style))
                            elements.append(Spacer(1, 15))
                        
                        # Education section
                        if resume_data["education"]:
                            elements.append(Paragraph("Education", heading_style))
                            for edu in resume_data["education"]:
                                elements.append(Paragraph(f"<b>{edu['institution']}</b>", normal_style))
                                elements.append(Paragraph(f"<b>{edu['degree']}</b>", normal_style))
                                date_range = f"{edu['start_date']} - {edu['end_date']}"
                                elements.append(Paragraph(date_range, italic_style))
                                elements.append(Spacer(1, 10))
                        
                        # Experience section
                        if resume_data["experience"]:
                            elements.append(Paragraph("Work Experience", heading_style))
                            for exp in resume_data["experience"]:
                                elements.append(Paragraph(f"<b>{exp['company']}</b>", normal_style))
                                elements.append(Paragraph(f"<b>{exp['position']}</b>", normal_style))
                                date_range = f"{exp['start_date']} - {exp['end_date']}"
                                elements.append(Paragraph(date_range, italic_style))
                                if exp["description"]:
                                    elements.append(Spacer(1, 5))
                                    elements.append(Paragraph(exp["description"], normal_style))
                                elements.append(Spacer(1, 10))
                        
                        # Skills section
                        if resume_data["skills"]:
                            elements.append(Paragraph("Skills", heading_style))
                            skills_text = ", ".join(resume_data["skills"])
                            elements.append(Paragraph(skills_text, normal_style))
                            elements.append(Spacer(1, 15))
                        
                        # Certifications section
                        if resume_data["certifications"]:
                            elements.append(Paragraph("Certifications", heading_style))
                            for cert in resume_data["certifications"]:
                                elements.append(Paragraph(f"<b>{cert['name']}</b>", normal_style))
                                if cert["date"]:
                                    elements.append(Paragraph(cert["date"], italic_style))
                                elements.append(Spacer(1, 8))
                    
                    # Build the PDF
                    doc.build(elements)
                    
                    # Read PDF as base64
                    with open(pdf_path, 'rb') as f:
                        rendered_pdf = base64.b64encode(f.read()).decode('utf-8')
                    
                    # Save to download history - use USDH.db instead of courses.db
                    conn = sqlite3.connect('data/USDH.db')
                    cursor = conn.cursor()
                    
                    # Create table if it doesn't exist
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS resume_downloads (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            template TEXT,
                            created_at TEXT,
                            file_path TEXT
                        )
                    ''')
                    
                    cursor.execute('''
                        INSERT INTO resume_downloads (user_id, template, created_at, file_path)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, template, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pdf_path))
                    
                    conn.commit()
                    conn.close()
                    
                    pdf_success = True
                    
                except Exception as pdf_err:
                    print(f"Error generating PDF with reportlab: {str(pdf_err)}")
                    # PDF generation failed, we'll use HTML preview instead
                
                # Get updated download history
                download_history = get_download_history(user_id)
                
                # Prepare output
                if pdf_success:
                    # Show HTML preview with PDF download option
                    with open(tmp_html_path, 'r') as f:
                        html_content = f.read()
                    
                    return html.Div([
                        html.Div("Resume generated successfully!", className="alert alert-success"),
                        html.Div([
                            dbc.Button(
                                "Download PDF", 
                                id="download-pdf-btn",
                                color="primary",
                                className="mb-3",
                                href=f"data:application/pdf;base64,{rendered_pdf}"
                            ),
                        ]),
                        html.Iframe(srcDoc=html_content, width="100%", height="800px", style={
                            "border": "1px solid #ddd",
                            "border-radius": "4px",
                            "background": "white"
                        }),
                    ]), dcc.send_file(pdf_path), download_history
                else:
                    # Fallback to HTML preview
                    with open(tmp_html_path, 'r') as f:
                        html_content = f.read()
                    
                    return html.Div([
                        html.Div([
                            html.P("Unable to generate PDF due to missing reportlab dependency."),
                            html.P([
                                "To enable PDF generation, please install reportlab: ",
                                html.A("pip install reportlab", href="https://pypi.org/project/reportlab/", target="_blank")
                            ]),
                            html.P("For now, you can view the HTML preview below:"),
                        ], className="alert alert-warning"),
                        html.Iframe(srcDoc=html_content, width="100%", height="800px", style={
                            "border": "1px solid #ddd",
                            "border-radius": "4px",
                            "background": "white"
                        }),
                    ]), dash.no_update, download_history
                
            except Exception as e:
                print(f"Error rendering template: {str(e)}")
                return html.Div(f"Error generating resume: {str(e)}", style={"color": "red"}), dash.no_update, dash.no_update
            
        except Exception as e:
            print(f"Error processing resume data: {str(e)}")
            return html.Div(f"Error generating resume: {str(e)}", style={"color": "red"}), dash.no_update, dash.no_update

def get_download_history(user_id):
    """Get user's resume download history"""
    try:
        # Connect to database
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                template TEXT,
                created_at TEXT,
                file_path TEXT
            )
        ''')
        
        # Get last 5 resumes
        cursor.execute('''
            SELECT id, template, created_at
            FROM resume_downloads
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        ''', (user_id,))
        
        downloads = cursor.fetchall()
        conn.close()
        
        if not downloads:
            return html.Div("No download history yet")
        
        # Create download history cards
        history_items = []
        for download_id, template_name, created_at in downloads:
            history_items.append(
                dbc.Card(
                    dbc.CardBody([
                        html.H5(f"Resume ({template_name.title()})", className="mb-1"),
                        html.P(f"Created: {created_at}", className="text-muted small"),
                        html.A("Download", href=f"/download-resume/{download_id}", className="btn btn-sm btn-primary mt-2"),
                    ]),
                    className="mb-2 download-history-card"
                )
            )
        
        return html.Div(history_items)
        
    except Exception as e:
        print(f"Error getting download history: {str(e)}")
        return html.Div("Error loading history", style={"color": "red"})

def create_education_card(index):
    """Create a new education card with proper button ID and ensuring inputs work properly"""
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Institution"),
                    dbc.Input(id={"type": "edu-institution", "index": index}, type="text", placeholder="Enter institution name", className="mb-2"),
                ], width=6),
                dbc.Col([
                    html.Label("Degree"),
                    dbc.Input(id={"type": "edu-degree", "index": index}, type="text", placeholder="Enter degree name", className="mb-2"),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Start Date"),
                    dbc.Input(id={"type": "edu-start", "index": index}, type="text", placeholder="Enter start date", className="mb-2"),
                ], width=6),
                dbc.Col([
                    html.Label("End Date"),
                    dbc.Input(id={"type": "edu-end", "index": index}, type="text", placeholder="Enter end date", className="mb-2"),
                ], width=6),
            ], className="mb-3"),
            dbc.Button(
                "Remove", 
                id={"type": "remove-edu", "index": index},
                color="danger", 
                size="sm",
                className="mt-1"
            ),
        ]),
        className="mb-3",
    )

def create_experience_card(index):
    """Create a new experience card with proper button ID and ensuring inputs work properly"""
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Company"),
                    dbc.Input(id={"type": "exp-company", "index": index}, type="text", placeholder="Enter company name", className="mb-2"),
                ], width=6),
                dbc.Col([
                    html.Label("Position"),
                    dbc.Input(id={"type": "exp-position", "index": index}, type="text", placeholder="Enter position", className="mb-2"),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Start Date"),
                    dbc.Input(id={"type": "exp-start", "index": index}, type="text", placeholder="Enter start date", className="mb-2"),
                ], width=6),
                dbc.Col([
                    html.Label("End Date"),
                    dbc.Input(id={"type": "exp-end", "index": index}, type="text", placeholder="Enter end date", className="mb-2"),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Responsibilities"),
                    dbc.Textarea(id={"type": "exp-desc", "index": index}, placeholder="Enter job responsibilities", rows=3, className="mb-2"),
                ], width=12),
            ], className="mb-3"),
            dbc.Button(
                "Remove", 
                id={"type": "remove-exp", "index": index},
                color="danger",
                size="sm",
                className="mt-1"
            ),
        ]),
        className="mb-3",
    )

def create_certification_card(index):
    """Create a new certification card with proper button ID and ensuring inputs work properly"""
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Certificate Name"),
                    dbc.Input(id={"type": "cert-name", "index": index}, type="text", placeholder="Enter certificate name", className="mb-2"),
                ], width=6),
                dbc.Col([
                    html.Label("Issuing Date"),
                    dbc.Input(id={"type": "cert-date", "index": index}, type="text", placeholder="Enter issuing date", className="mb-2"),
                ], width=6),
                ], className="mb-3"),
            dbc.Button(
                "Remove", 
                id={"type": "remove-cert", "index": index},
                color="danger",
                size="sm",
                className="mt-1"
            ),
        ]),
        className="mb-3",
    )

# Create required directories and files
def create_required_files():
    """Create required directories and files for the resume maker"""
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('tmp', exist_ok=True)
    
    # Create professional template
    professional_template = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 20px; }
        .section-title { border-bottom: 2px solid #333; margin-bottom: 10px; }
        .experience-item { margin-bottom: 15px; }
        .date { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ personal_info.name }}</h1>
        <p>{{ personal_info.email }} | {{ personal_info.phone }} | {{ personal_info.location }}</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Professional Summary</h2>
        <p>{{ personal_info.summary }}</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Education</h2>
        {% for edu in education %}
        <div class="experience-item">
            <h3>{{ edu.institution }}</h3>
            <p>{{ edu.degree }}</p>
            <p class="date">{{ edu.start_date }} - {{ edu.end_date }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2 class="section-title">Work Experience</h2>
        {% for exp in experience %}
        <div class="experience-item">
            <h3>{{ exp.company }}</h3>
            <p>{{ exp.position }}</p>
            <p class="date">{{ exp.start_date }} - {{ exp.end_date }}</p>
            <p>{{ exp.description }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2 class="section-title">Skills</h2>
        <p>{{ skills|join(", ") }}</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Certifications</h2>
        {% for cert in certifications %}
        <div class="experience-item">
            <h3>{{ cert.name }}</h3>
            <p class="date">Date: {{ cert.date }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>"""

    # Create modern template
    modern_template = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; margin: 40px; }
        .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .section { margin-bottom: 25px; }
        .section-title { color: #2c3e50; border-left: 4px solid #3498db; padding-left: 10px; margin-bottom: 15px; }
        .experience-item { margin-bottom: 20px; }
        .date { color: #7f8c8d; font-size: 0.9em; }
        .skills-container { display: flex; flex-wrap: wrap; gap: 10px; }
        .skill-tag { background-color: #e1f0fa; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ personal_info.name }}</h1>
        <p>{{ personal_info.email }} | {{ personal_info.phone }} | {{ personal_info.location }}</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Professional Summary</h2>
        <p>{{ personal_info.summary }}</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Education</h2>
        {% for edu in education %}
        <div class="experience-item">
            <h3>{{ edu.institution }}</h3>
            <p>{{ edu.degree }}</p>
            <p class="date">{{ edu.start_date }} - {{ edu.end_date }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2 class="section-title">Work Experience</h2>
        {% for exp in experience %}
        <div class="experience-item">
            <h3>{{ exp.company }}</h3>
            <p>{{ exp.position }}</p>
            <p class="date">{{ exp.start_date }} - {{ exp.end_date }}</p>
            <p>{{ exp.description }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2 class="section-title">Skills</h2>
        <div class="skills-container">
            {% for skill in skills %}
            <span class="skill-tag">{{ skill }}</span>
            {% endfor %}
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Certifications</h2>
        {% for cert in certifications %}
        <div class="experience-item">
            <h3>{{ cert.name }}</h3>
            <p class="date">Date: {{ cert.date }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>"""

    # Create creative template
    creative_template = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Helvetica Neue', sans-serif; line-height: 1.6; margin: 40px; }
        .header { text-align: center; margin-bottom: 40px; position: relative; }
        .header::after { content: ''; display: block; width: 100px; height: 3px; background: linear-gradient(to right, #ff6b6b, #4ecdc4); margin: 20px auto; }
        .section { margin-bottom: 30px; }
        .section-title { color: #ff6b6b; font-size: 1.5em; margin-bottom: 15px; }
        .experience-item { margin-bottom: 25px; padding-left: 20px; border-left: 2px solid #4ecdc4; }
        .date { color: #95a5a6; font-size: 0.9em; }
        .skills-container { display: flex; flex-wrap: wrap; gap: 10px; }
        .skill-tag { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ personal_info.name }}</h1>
        <p>{{ personal_info.email }} | {{ personal_info.phone }} | {{ personal_info.location }}</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Professional Summary</h2>
        <p>{{ personal_info.summary }}</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Education</h2>
        {% for edu in education %}
        <div class="experience-item">
            <h3>{{ edu.institution }}</h3>
            <p>{{ edu.degree }}</p>
            <p class="date">{{ edu.start_date }} - {{ edu.end_date }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2 class="section-title">Work Experience</h2>
        {% for exp in experience %}
        <div class="experience-item">
            <h3>{{ exp.company }}</h3>
            <p>{{ exp.position }}</p>
            <p class="date">{{ exp.start_date }} - {{ exp.end_date }}</p>
            <p>{{ exp.description }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2 class="section-title">Skills</h2>
        <div class="skills-container">
            {% for skill in skills %}
            <span class="skill-tag">{{ skill }}</span>
            {% endfor %}
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Certifications</h2>
        {% for cert in certifications %}
        <div class="experience-item">
            <h3>{{ cert.name }}</h3>
            <p class="date">Date: {{ cert.date }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>"""

    # Write template files
    with open('templates/professional_template.html', 'w') as f:
        f.write(professional_template)
    
    with open('templates/modern_template.html', 'w') as f:
        f.write(modern_template)
    
    with open('templates/creative_template.html', 'w') as f:
        f.write(creative_template)
    
    print("Created required files for resume maker")

# Create required files on import
create_required_files()