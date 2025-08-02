import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
from flask import session as flask_session
import os
import base64
import datetime
import json

def my_space():
    """
    My Space page layout with document and study material management
    """
    # Check if user is logged in - check both Flask session and Dash store
    if not flask_session.get('user_id'):
        return html.Div([
            html.H3("Please log in to access My Space"),
            html.A("Go to Login", href="/", className="btn btn-primary")
        ])
    
    return html.Div([
        # Header
        html.Div([
            html.H2("My Space", className="mb-4"),
            dbc.Button("Back to Dashboard", href="/user", color="secondary", className="mb-3"),
        ], className="mb-4"),
        
        # Study Materials Section
        dbc.Card([
            dbc.CardHeader([
                html.H4("Study Materials", className="mb-0"),
                html.Div([
                    dbc.Button(
                        html.I(className="fas fa-folder-plus me-2"),
                        id="add-folder-btn",
                        color="info",
                        className="me-2",
                        title="Upload Folder"
                    ),
                    dbc.Button(
                        "Add Study Material",
                        id="add-study-material-btn",
                        color="primary"
                    )
                ], className="float-end")
            ], className="d-flex justify-content-between align-items-center"),
            dbc.CardBody([
                # Folder Upload Modal
                dbc.Modal([
                    dbc.ModalHeader("Upload Folder"),
                    dbc.ModalBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Folder Name"),
                                    dbc.Input(id="folder-name", type="text", placeholder="Enter folder name", className="mb-3"),
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Description"),
                                    dbc.Textarea(id="folder-description", placeholder="Enter folder description", className="mb-3"),
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Select Folder"),
                                    dcc.Upload(
                                        id='folder-upload',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select a Folder')
                                        ]),
                                        style={
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px 0'
                                        },
                                        multiple=True
                                    ),
                                    html.Div(id='folder-upload-output', className="mt-2")
                                ], width=12),
                            ]),
                        ])
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Upload", id="upload-folder-btn", color="primary"),
                        dbc.Button("Cancel", id="cancel-folder-btn", color="secondary")
                    ])
                ], id="folder-upload-modal", is_open=False),
                
                # Study Material Upload Modal
                dbc.Modal([
                    dbc.ModalHeader("Upload Study Material"),
                    dbc.ModalBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Material Name"),
                                    dbc.Input(id="material-name", type="text", placeholder="Enter material name", className="mb-3"),
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Description"),
                                    dbc.Textarea(id="material-description", placeholder="Enter material description", className="mb-3"),
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Upload File"),
                                    dcc.Upload(
                                        id='material-upload',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select a File')
                                        ]),
                                        style={
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px 0'
                                        },
                                        multiple=False
                                    ),
                                    html.Div(id='material-upload-output', className="mt-2")
                                ], width=12),
                            ]),
                        ])
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Upload", id="upload-material-btn", color="primary"),
                        dbc.Button("Cancel", id="cancel-material-btn", color="secondary")
                    ])
                ], id="material-upload-modal", is_open=False),
                
                # Study Materials List
                html.Div(id="study-materials-list", className="mt-3")
            ])
        ], className="mb-4"),

        # Documents Section
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4("My Documents", className="mb-0"),
                    dbc.Button(
                        "Show Documents",
                        id="show-documents-btn",
                        color="primary",
                        className="ms-3"
                    )
                ], className="d-flex align-items-center"),
                dbc.Button(
                    "Add Document",
                    id="add-document-btn",
                    color="primary",
                    className="float-end"
                )
            ], className="d-flex justify-content-between align-items-center"),
            dbc.CardBody([
                # Password Verification Section
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Enter your password to view documents:", className="mb-2"),
                            dbc.Input(
                                id="documents-password",
                                type="password",
                                placeholder="Enter your password",
                                className="mb-2"
                            ),
                            dbc.Button(
                                "Verify Password",
                                id="verify-password-btn",
                                color="primary",
                                className="mb-3"
                            ),
                            html.Div(id="password-error", className="text-danger mb-3", style={"display": "none"})
                        ], width=12)
                    ])
                ], id="password-section", style={"display": "block"}),
                
                # Document Upload Modal
                dbc.Modal([
                    dbc.ModalHeader("Upload Document"),
                    dbc.ModalBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Document Name"),
                                    dbc.Input(id="document-name", type="text", placeholder="Enter document name", className="mb-3"),
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Description"),
                                    dbc.Textarea(id="document-description", placeholder="Enter document description", className="mb-3"),
                                ], width=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Upload File"),
                                    dcc.Upload(
                                        id='document-upload',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select a File')
                                        ]),
                                        style={
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px 0'
                                        },
                                        multiple=False
                                    ),
                                    html.Div(id='document-upload-output', className="mt-2")
                                ], width=12),
                            ]),
                        ])
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Upload", id="upload-document-btn", color="primary"),
                        dbc.Button("Cancel", id="cancel-document-btn", color="secondary")
                    ])
                ], id="document-upload-modal", is_open=False),
                
                # Documents List (Initially Hidden)
                html.Div(id="documents-list", className="mt-3", style={"display": "none"})
            ])
        ]),
        
        # Folder Contents Modal
        dbc.Modal(
            id="folder-contents-modal",
            size="lg",
            is_open=False
        ),
        
        # Hidden components
        dcc.Store(id="documents-store"),
        dcc.Store(id="materials-store"),
    ], className="my-space-container p-4")

def register_callbacks(app):
    # Toggle document upload modal
    @app.callback(
        Output("document-upload-modal", "is_open"),
        [Input("add-document-btn", "n_clicks"),
         Input("cancel-document-btn", "n_clicks")],
        [State("document-upload-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_document_modal(add_clicks, cancel_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "add-document-btn":
            return True
        elif trigger_id == "cancel-document-btn":
            return False
        return is_open

    # Handle document file upload preview
    @app.callback(
        Output("document-upload-output", "children"),
        [Input("document-upload", "contents")],
        [State("document-upload", "filename")],
        prevent_initial_call=True
    )
    def handle_document_upload(contents, filename):
        if contents is None:
            return ""
            
        if filename is None:
            return html.Div("No file selected", style={"color": "red"})
            
        return html.Div(f"Selected file: {filename}", style={"color": "green"})

    # Toggle folder upload modal
    @app.callback(
        Output("folder-upload-modal", "is_open"),
        [Input("add-folder-btn", "n_clicks"),
         Input("cancel-folder-btn", "n_clicks")],
        [State("folder-upload-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_folder_modal(add_clicks, cancel_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "add-folder-btn":
            return True
        elif trigger_id == "cancel-folder-btn":
            return False
        return is_open

    # Handle folder upload preview
    @app.callback(
        Output("folder-upload-output", "children"),
        [Input("folder-upload", "contents")],
        [State("folder-upload", "filename")],
        prevent_initial_call=True
    )
    def handle_folder_upload(contents, filenames):
        if contents is None:
            return ""
            
        if not filenames:
            return html.Div("No files selected", style={"color": "red"})
            
        return html.Div([
            html.P(f"Selected {len(filenames)} files:", className="mb-2"),
            html.Ul([html.Li(filename) for filename in filenames], className="list-unstyled")
        ], style={"color": "green"})

    # Study Material Modal Toggle
    @app.callback(
        Output("material-upload-modal", "is_open"),
        [Input("add-study-material-btn", "n_clicks"),
         Input("cancel-material-btn", "n_clicks")],
        [State("material-upload-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_material_modal(add_clicks, cancel_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "add-study-material-btn":
            return True
        elif trigger_id == "cancel-material-btn":
            return False
        return is_open

    # Handle study material file upload preview
    @app.callback(
        Output("material-upload-output", "children", allow_duplicate=True),
        [Input("material-upload", "contents")],
        [State("material-upload", "filename")],
        prevent_initial_call=True
    )
    def handle_material_upload(contents, filename):
        if contents is None:
            return ""
            
        if filename is None:
            return html.Div("No file selected", style={"color": "red"})
            
        return html.Div(f"Selected file: {filename}", style={"color": "green"})

    # Password verification callback
    @app.callback(
        [Output("password-section", "style"),
         Output("documents-list", "style"),
         Output("password-error", "style"),
         Output("password-error", "children")],
        [Input("verify-password-btn", "n_clicks")],
        [State("documents-password", "value")],
        prevent_initial_call=True
    )
    def verify_password(n_clicks, password):
        if not n_clicks:
            return {"display": "block"}, {"display": "none"}, {"display": "none"}, ""
            
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return {"display": "block"}, {"display": "none"}, {"display": "block"}, "Session expired"
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Get user's password from database
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == password:
                return {"display": "none"}, {"display": "block"}, {"display": "none"}, ""
            else:
                return {"display": "block"}, {"display": "none"}, {"display": "block"}, "Incorrect password"
                
        except Exception as e:
            print(f"Error verifying password: {str(e)}")
            return {"display": "block"}, {"display": "none"}, {"display": "block"}, "Error verifying password"

    # Show/Hide Documents callback
    @app.callback(
        [Output("documents-list", "style", allow_duplicate=True),
         Output("show-documents-btn", "children"),
         Output("password-section", "style", allow_duplicate=True)],
        [Input("show-documents-btn", "n_clicks")],
        [State("documents-list", "style")],
        prevent_initial_call=True
    )
    def toggle_documents(n_clicks, current_style):
        if current_style is None:
            current_style = {"display": "none"}
            
        if current_style.get("display") == "none":
            return {"display": "none"}, "Show Documents", {"display": "block"}
        else:
            return {"display": "none"}, "Show Documents", {"display": "block"}

    # Initial content loading callback
    @app.callback(
        [Output("documents-list", "children"),
         Output("study-materials-list", "children")],
        [Input("url", "pathname")],
        prevent_initial_call=False
    )
    def load_initial_content(pathname):
        if pathname != "/my-space":
            return [], []
            
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return html.Div("Session expired"), html.Div("Session expired")
                
            documents_list = get_documents_list(user_id)
            materials_list = get_study_materials_list(user_id)
            return documents_list, materials_list
            
        except Exception as e:
            print(f"Error loading initial content: {str(e)}")
            return html.Div("Error loading content"), html.Div("Error loading content")

    # Combined callback for handling all updates (documents, study materials, and folders)
    @app.callback(
        [Output("documents-list", "children", allow_duplicate=True),
         Output("document-upload-modal", "is_open", allow_duplicate=True),
         Output("document-upload-output", "children", allow_duplicate=True),
         Output("study-materials-list", "children", allow_duplicate=True),
         Output("material-upload-modal", "is_open", allow_duplicate=True),
         Output("material-upload-output", "children", allow_duplicate=True),
         Output("folder-upload-modal", "is_open", allow_duplicate=True),
         Output("folder-upload-output", "children", allow_duplicate=True)],
        [Input("upload-document-btn", "n_clicks"),
         Input("upload-material-btn", "n_clicks"),
         Input("upload-folder-btn", "n_clicks")],
        [State("document-name", "value"),
         State("document-description", "value"),
         State("document-upload", "contents"),
         State("document-upload", "filename"),
         State("material-name", "value"),
         State("material-description", "value"),
         State("material-upload", "contents"),
         State("material-upload", "filename"),
         State("folder-name", "value"),
         State("folder-description", "value"),
         State("folder-upload", "contents"),
         State("folder-upload", "filename")],
        prevent_initial_call=True
    )
    def handle_all_updates(doc_upload_clicks, mat_upload_clicks, folder_upload_clicks,
                          doc_name, doc_description, doc_contents, doc_filename,
                          mat_name, mat_description, mat_contents, mat_filename,
                          folder_name, folder_description, folder_contents, folder_filenames):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return html.Div("Session expired"), False, "", html.Div("Session expired"), False, "", False, "Session expired. Please log in again."
                
            # Handle document upload
            if trigger_id == "upload-document-btn" and doc_upload_clicks:
                if not all([doc_name, doc_contents, doc_filename]):
                    return dash.no_update, False, "Please fill in all required fields", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
                    
                try:
                    # Create documents directory if it doesn't exist
                    doc_dir = os.path.join("static", "documents", str(user_id))
                    os.makedirs(doc_dir, exist_ok=True)
                    
                    # Save document file
                    content_type, content_string = doc_contents.split(',')
                    decoded = base64.b64decode(content_string)
                    
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = os.path.splitext(doc_filename)[1].lower()
                    new_filename = f"{timestamp}{file_extension}"
                    filepath = os.path.join(doc_dir, new_filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(decoded)
                        
                    # Save to database
                    conn = sqlite3.connect('data/USDH.db')
                    cursor = conn.cursor()
                    
                    # Create documents table if it doesn't exist
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS documents (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            name TEXT,
                            description TEXT,
                            file_path TEXT,
                            upload_date TEXT,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')
                    
                    # Insert the new document
                    cursor.execute('''
                        INSERT INTO documents (user_id, name, description, file_path, upload_date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, doc_name, doc_description, new_filename, 
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    
                    conn.commit()
                    conn.close()
                    
                    # Get updated documents list
                    documents_list = get_documents_list(user_id)
                    materials_list = get_study_materials_list(user_id)
                    return documents_list, False, "Document uploaded successfully!", materials_list, False, "", False, ""
                    
                except Exception as e:
                    print(f"Error uploading document: {str(e)}")
                    return dash.no_update, False, f"Error uploading document: {str(e)}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

            # Handle study material upload
            elif trigger_id == "upload-material-btn" and mat_upload_clicks:
                if not all([mat_name, mat_contents, mat_filename]):
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, False, "Please fill in all required fields", dash.no_update, dash.no_update
                    
                try:
                    # Create study materials directory if it doesn't exist
                    mat_dir = os.path.join("static", "study_materials", str(user_id))
                    os.makedirs(mat_dir, exist_ok=True)
                    
                    # Save material file
                    content_type, content_string = mat_contents.split(',')
                    decoded = base64.b64decode(content_string)
                    
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = os.path.splitext(mat_filename)[1].lower()
                    new_filename = f"{timestamp}{file_extension}"
                    filepath = os.path.join(mat_dir, new_filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(decoded)
                        
                    # Save to database
                    conn = sqlite3.connect('data/USDH.db')
                    cursor = conn.cursor()
                    
                    # First, check if the study materials table exists
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='study_materials'
                    """)
                    if not cursor.fetchone():
                        # Create the study materials table if it doesn't exist
                        cursor.execute('''
                            CREATE TABLE study_materials (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                name TEXT,
                                description TEXT,
                                file_path TEXT,
                                upload_date TEXT,
                                FOREIGN KEY (user_id) REFERENCES users (id)
                            )
                        ''')
                        conn.commit()
                        print("Study_materials table created successfully")
                    
                    # Insert the new study material
                    cursor.execute('''
                        INSERT INTO study_materials (user_id, name, description, file_path, upload_date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, mat_name, mat_description, new_filename, 
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    
                    conn.commit()
                    conn.close()
                    
                    # Get updated lists
                    documents_list = get_documents_list(user_id)
                    materials_list = get_study_materials_list(user_id)
                    return documents_list, False, "", materials_list, False, "Study material uploaded successfully!", False, ""
                    
                except Exception as e:
                    print(f"Error uploading study material: {str(e)}")
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, False, f"Error uploading study material: {str(e)}", dash.no_update, dash.no_update

            # Handle folder upload
            elif trigger_id == "upload-folder-btn" and folder_upload_clicks:
                if not all([folder_name, folder_contents, folder_filenames]):
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False, "Please fill in all required fields"
                    
                try:
                    # Create folder directory if it doesn't exist
                    folder_dir = os.path.join("static", "folders", str(user_id), folder_name)
                    os.makedirs(folder_dir, exist_ok=True)
                    
                    # Save all files from the folder
                    for content, filename in zip(folder_contents, folder_filenames):
                        if content and filename:
                            content_type, content_string = content.split(',')
                            decoded = base64.b64decode(content_string)
                            
                            filepath = os.path.join(folder_dir, filename)
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            
                            with open(filepath, 'wb') as f:
                                f.write(decoded)
                    
                    # Save folder info to database
                    conn = sqlite3.connect('data/USDH.db')
                    cursor = conn.cursor()
                    
                    # Create folders table if it doesn't exist
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS folders (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            name TEXT,
                            description TEXT,
                            folder_path TEXT,
                            upload_date TEXT,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')
                    
                    # Insert the new folder
                    cursor.execute('''
                        INSERT INTO folders (user_id, name, description, folder_path, upload_date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, folder_name, folder_description, folder_name, 
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    
                    conn.commit()
                    conn.close()
                    
                    # Get updated lists
                    documents_list = get_documents_list(user_id)
                    materials_list = get_study_materials_list(user_id)
                    return documents_list, False, "", materials_list, False, "", False, "Folder uploaded successfully!"
                    
                except Exception as e:
                    print(f"Error uploading folder: {str(e)}")
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False, f"Error uploading folder: {str(e)}"
                
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
        except Exception as e:
            print(f"Error in handle_all_updates: {str(e)}")
            return [], False, "", [], False, "", False, f"Error: {str(e)}"

    # Delete document callback
    @app.callback(
        [Output("documents-list", "children", allow_duplicate=True),
         Output("study-materials-list", "children", allow_duplicate=True)],
        [Input({"type": "delete-document", "index": dash.ALL}, "n_clicks")],
        [State({"type": "delete-document", "index": dash.ALL}, "id")],
        prevent_initial_call=True
    )
    def delete_document(n_clicks, ids):
        if not n_clicks or not any(n_clicks):
            raise dash.exceptions.PreventUpdate
            
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        doc_id = json.loads(button_id)["index"]
        
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return html.Div("Session expired"), html.Div("Session expired")
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Get file path before deleting
            cursor.execute("SELECT file_path FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
            result = cursor.fetchone()
            
            if result:
                file_path = result[0]
                # Delete from database
                cursor.execute("DELETE FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
                conn.commit()
                
                # Delete file
                full_path = os.path.join("static", "documents", str(user_id), file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            
            conn.close()
            
            # Refresh lists
            documents_list = get_documents_list(user_id)
            materials_list = get_study_materials_list(user_id)
            return documents_list, materials_list
            
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return html.Div("Error deleting document"), html.Div("Error deleting document")

    # Delete study material callback
    @app.callback(
        [Output("documents-list", "children", allow_duplicate=True),
         Output("study-materials-list", "children", allow_duplicate=True)],
        [Input({"type": "delete-material", "index": dash.ALL}, "n_clicks")],
        [State({"type": "delete-material", "index": dash.ALL}, "id")],
        prevent_initial_call=True
    )
    def delete_material(n_clicks, ids):
        if not n_clicks or not any(n_clicks):
            raise dash.exceptions.PreventUpdate
            
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        mat_id = json.loads(button_id)["index"]
        
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return html.Div("Session expired"), html.Div("Session expired")
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Get file path before deleting
            cursor.execute("SELECT file_path FROM study_materials WHERE id = ? AND user_id = ?", (mat_id, user_id))
            result = cursor.fetchone()
            
            if result:
                file_path = result[0]
                # Delete from database
                cursor.execute("DELETE FROM study_materials WHERE id = ? AND user_id = ?", (mat_id, user_id))
                conn.commit()
                
                # Delete file
                full_path = os.path.join("static", "study_materials", str(user_id), file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            
            conn.close()
            
            # Refresh lists
            documents_list = get_documents_list(user_id)
            materials_list = get_study_materials_list(user_id)
            return documents_list, materials_list
            
        except Exception as e:
            print(f"Error deleting material: {str(e)}")
            return html.Div("Error deleting material"), html.Div("Error deleting material")

    # Delete folder callback
    @app.callback(
        [Output("documents-list", "children", allow_duplicate=True),
         Output("study-materials-list", "children", allow_duplicate=True)],
        [Input({"type": "delete-folder", "index": dash.ALL}, "n_clicks")],
        [State({"type": "delete-folder", "index": dash.ALL}, "id")],
        prevent_initial_call=True
    )
    def delete_folder(n_clicks, ids):
        if not n_clicks or not any(n_clicks):
            raise dash.exceptions.PreventUpdate
            
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        folder_id = json.loads(button_id)["index"]
        
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return html.Div("Session expired"), html.Div("Session expired")
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Get folder path before deleting
            cursor.execute("SELECT folder_path FROM folders WHERE id = ? AND user_id = ?", (folder_id, user_id))
            result = cursor.fetchone()
            
            if result:
                folder_path = result[0]
                # Delete from database first
                cursor.execute("DELETE FROM folders WHERE id = ? AND user_id = ?", (folder_id, user_id))
                conn.commit()
                
                # Try to delete folder and its contents
                full_path = os.path.join("static", "folders", str(user_id), folder_path)
                if os.path.exists(full_path):
                    try:
                        import shutil
                        shutil.rmtree(full_path)
                    except PermissionError:
                        print(f"Permission denied when deleting folder: {full_path}")
                        # Continue even if folder deletion fails - we've already removed it from the database
                    except Exception as e:
                        print(f"Error deleting folder: {str(e)}")
                        # Continue even if folder deletion fails - we've already removed it from the database
            
            conn.close()
            
            # Refresh lists
            documents_list = get_documents_list(user_id)
            materials_list = get_study_materials_list(user_id)
            return documents_list, materials_list
            
        except Exception as e:
            print(f"Error in delete_folder: {str(e)}")
            return html.Div("Error deleting folder"), html.Div("Error deleting folder")

    # Folder contents modal callback
    @app.callback(
        [Output("folder-contents-modal", "is_open"),
         Output("folder-contents-modal", "children")],
        [Input({"type": "open-folder", "index": dash.ALL}, "n_clicks"),
         Input({"type": "add-files", "index": dash.ALL}, "n_clicks")],
        [State({"type": "open-folder", "index": dash.ALL}, "id"),
         State({"type": "add-files", "index": dash.ALL}, "id")],
        prevent_initial_call=True
    )
    def toggle_folder_contents_modal(n_clicks_open, n_clicks_add, ids_open, ids_add):
        ctx = callback_context
        if not ctx.triggered:
            return False, None
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if not (n_clicks_open or n_clicks_add) or not (any(n_clicks_open) or any(n_clicks_add)):
            return False, None
            
        # Get the button ID that was clicked
        if any(n_clicks_open):
            button_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        else:
            button_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
            
        folder_id = button_id["index"]
        
        user_id = flask_session.get("user_id")
        if not user_id:
            return False, html.Div("Session expired")
            
        contents = get_folder_contents(user_id, folder_id)
        return True, contents

    # Close folder modal callback
    @app.callback(
        Output("folder-contents-modal", "is_open", allow_duplicate=True),
        [Input("close-folder-btn", "n_clicks")],
        [State("folder-contents-modal", "is_open")],
        prevent_initial_call=True
    )
    def close_folder_modal(n_clicks, is_open):
        if n_clicks:
            return False
        return is_open

    # Handle folder files upload
    @app.callback(
        [Output("folder-files-upload-output", "children"),
         Output("folder-contents-modal", "children", allow_duplicate=True)],
        [Input("folder-files-upload", "contents")],
        [State("folder-files-upload", "filename"),
         State("folder-contents-modal", "children")],
        prevent_initial_call=True
    )
    def handle_folder_files_upload(contents, filenames, current_modal):
        if not contents or not filenames:
            return "", current_modal
            
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return "Session expired", current_modal
                
            # Get folder ID from the modal header
            folder_name = current_modal['props']['children'][0]['props']['children'][1]['props']['children']
            
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Get folder path
            cursor.execute('''
                SELECT id, folder_path
                FROM folders
                WHERE name = ? AND user_id = ?
            ''', (folder_name, user_id))
            
            result = cursor.fetchone()
            if not result:
                return "Folder not found", current_modal
                
            folder_id, folder_path = result
            full_path = os.path.join("static", "folders", str(user_id), folder_path)
            
            # Save files
            for content, filename in zip(contents, filenames):
                if content and filename:
                    content_type, content_string = content.split(',')
                    decoded = base64.b64decode(content_string)
                    
                    filepath = os.path.join(full_path, filename)
                    with open(filepath, 'wb') as f:
                        f.write(decoded)
            
            conn.close()
            
            # Refresh folder contents
            new_contents = get_folder_contents(user_id, folder_id)
            return html.Div(f"Successfully added {len(filenames)} files", style={"color": "green"}), new_contents
            
        except Exception as e:
            print(f"Error uploading folder files: {str(e)}")
            return html.Div(f"Error uploading files: {str(e)}", style={"color": "red"}), current_modal

    # Delete folder file callback
    @app.callback(
        [Output("folder-contents-modal", "children", allow_duplicate=True)],
        [Input({"type": "delete-folder-file", "index": dash.ALL}, "n_clicks")],
        [State({"type": "delete-folder-file", "index": dash.ALL}, "id")],
        prevent_initial_call=True
    )
    def delete_folder_file(n_clicks, ids):
        if not n_clicks or not any(n_clicks):
            raise dash.exceptions.PreventUpdate
            
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        folder_id, filename = json.loads(button_id)["index"].split("_")
        
        try:
            user_id = flask_session.get("user_id")
            if not user_id:
                return [html.Div("Session expired")]
                
            conn = sqlite3.connect('data/USDH.db')
            cursor = conn.cursor()
            
            # Get folder path
            cursor.execute('''
                SELECT folder_path
                FROM folders
                WHERE id = ? AND user_id = ?
            ''', (folder_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return [html.Div("Folder not found")]
                
            folder_path = result[0]
            file_path = os.path.join("static", "folders", str(user_id), folder_path, filename)
            
            # Delete file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            conn.close()
            
            # Refresh folder contents
            new_contents = get_folder_contents(user_id, folder_id)
            return [new_contents]
            
        except Exception as e:
            print(f"Error deleting folder file: {str(e)}")
            return [html.Div(f"Error deleting file: {str(e)}", style={"color": "red"})]

def get_documents_list(user_id):
    """Get user's documents list"""
    try:
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # First, check if the documents table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='documents'
        """)
        if not cursor.fetchone():
            # Create the documents table if it doesn't exist
            cursor.execute('''
                CREATE TABLE documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    description TEXT,
                    file_path TEXT,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
        
        # Now get the documents
        cursor.execute('''
            SELECT id, name, description, file_path, upload_date
            FROM documents
            WHERE user_id = ?
            ORDER BY upload_date DESC
        ''', (user_id,))
        
        documents = cursor.fetchall()
        conn.close()
        
        if not documents:
            return html.Div("No documents uploaded yet")
            
        documents_list = []
        for doc_id, name, description, file_path, upload_date in documents:
            # Create the full URL path for the document
            doc_url = f"/static/documents/{user_id}/{file_path}"
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.Div([
                    html.H5(name, className="mb-0"),
                        dbc.Button(
                            html.I(className="fas fa-trash-alt"),
                            id={"type": "delete-document", "index": doc_id},
                            color="danger",
                            className="float-end",
                            size="sm"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody([
                    html.P(description if description else "No description provided", className="card-text"),
                    html.P(f"Uploaded: {upload_date}", className="text-muted small"),
                    html.A(
                        "Download",
                        href=doc_url,
                        target="_blank",
                        className="btn btn-primary btn-sm"
                    )
                ])
            ], className="mb-3")
            documents_list.append(card)
            
        return html.Div(documents_list)
        
    except Exception as e:
        print(f"Error getting documents list: {str(e)}")
        return html.Div("Error loading documents", style={"color": "red"}) 

def get_folders_list(user_id):
    """Get user's folders list"""
    try:
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # First, check if the folders table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='folders'
        """)
        if not cursor.fetchone():
            # Create the folders table if it doesn't exist
            cursor.execute('''
                CREATE TABLE folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    description TEXT,
                    folder_path TEXT,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
        
        # Now get the folders
        cursor.execute('''
            SELECT id, name, description, folder_path, upload_date
            FROM folders
            WHERE user_id = ?
            ORDER BY upload_date DESC
        ''', (user_id,))
        
        folders = cursor.fetchall()
        conn.close()
        
        if not folders:
            return []
            
        folders_list = []
        for folder_id, name, description, folder_path, upload_date in folders:
            # Create the full URL path for the folder
            folder_url = f"/static/folders/{user_id}/{folder_path}"
            
            # Check if folder exists
            folder_exists = os.path.exists(os.path.join("static", "folders", str(user_id), folder_path))
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-folder me-2"),
                            html.H5(name, className="mb-0 d-inline")
                        ]),
                        dbc.Button(
                            html.I(className="fas fa-trash-alt"),
                            id={"type": "delete-folder", "index": folder_id},
                            color="danger",
                            className="float-end",
                            size="sm"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody([
                    html.P(description if description else "No description provided", className="card-text"),
                    html.P(f"Uploaded: {upload_date}", className="text-muted small"),
                    dbc.Button(
                        "Open Folder",
                        id={"type": "open-folder", "index": folder_id},
                        color="info",
                        className="btn-sm me-2"
                    ),
                    dbc.Button(
                        "Add Files",
                        id={"type": "add-files", "index": folder_id},
                        color="success",
                        className="btn-sm"
                    )
                ])
            ], className="mb-3")
            folders_list.append(card)
            
        return folders_list
        
    except Exception as e:
        print(f"Error getting folders list: {str(e)}")
        return []

def get_folder_contents(user_id, folder_id):
    """Get contents of a specific folder"""
    try:
        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # Get folder details
        cursor.execute('''
            SELECT name, folder_path
            FROM folders
            WHERE id = ? AND user_id = ?
        ''', (folder_id, user_id))
        
        result = cursor.fetchone()
        if not result:
            return html.Div("Folder not found")
            
        folder_name, folder_path = result
        full_path = os.path.join("static", "folders", str(user_id), folder_path)
        
        if not os.path.exists(full_path):
            return html.Div("Folder not found")
            
        # Get list of files in the folder
        files = []
        for filename in os.listdir(full_path):
            file_path = os.path.join(full_path, filename)
            if os.path.isfile(file_path):
                files.append({
                    'name': filename,
                    'path': f"/static/folders/{user_id}/{folder_path}/{filename}",
                    'size': os.path.getsize(file_path),
                    'modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Create the folder contents modal
        return html.Div([
            dbc.ModalHeader([
                html.Div([
                    html.I(className="fas fa-folder me-2"),
                    html.H4(folder_name, className="mb-0")
                ])
            ]),
            dbc.ModalBody([
                # Add Files Section
                dbc.Card([
                    dbc.CardHeader("Add Files"),
                    dbc.CardBody([
                        dcc.Upload(
                            id='folder-files-upload',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0'
                            },
                            multiple=True
                        ),
                        html.Div(id='folder-files-upload-output', className="mt-2")
                    ])
                ], className="mb-3"),
                
                # Files List
                html.H5("Files in Folder", className="mb-3"),
                html.Div([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("File Name"),
                                html.Th("Size"),
                                html.Th("Modified"),
                                html.Th("Actions")
                            ])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td(file['name']),
                                html.Td(f"{file['size'] / 1024:.1f} KB"),
                                html.Td(file['modified']),
                                html.Td([
                                    html.A(
                                        "Download",
                                        href=file['path'],
                                        target="_blank",
                                        className="btn btn-primary btn-sm me-2"
                                    ),
                                    dbc.Button(
                                        html.I(className="fas fa-trash-alt"),
                                        id={"type": "delete-folder-file", "index": f"{folder_id}_{file['name']}"},
                                        color="danger",
                                        size="sm"
                                    )
                                ])
                            ]) for file in files
                        ])
                    ], bordered=True, hover=True, responsive=True)
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Close", id="close-folder-btn", color="secondary")
            ])
        ])
        
    except Exception as e:
        print(f"Error getting folder contents: {str(e)}")
        return html.Div("Error loading folder contents", style={"color": "red"})
    finally:
        conn.close()

def get_study_materials_list(user_id):
    """Get user's study materials list"""
    try:
        # Ensure user_id is valid
        if not user_id:
            print("Error: No user_id provided")
            return html.Div("Please log in to view study materials", style={"color": "red"})

        # Ensure database directory exists
        if not os.path.exists('data'):
            os.makedirs('data')

        conn = sqlite3.connect('data/USDH.db')
        cursor = conn.cursor()
        
        # First, check if the study materials table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='study_materials'
        """)
        if not cursor.fetchone():
            # Create the study materials table if it doesn't exist
            cursor.execute('''
                CREATE TABLE study_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    description TEXT,
                    file_path TEXT,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
            print("Study_materials table created successfully")
        
        # Now get the study materials
        cursor.execute('''
            SELECT id, name, description, file_path, upload_date
            FROM study_materials
            WHERE user_id = ?
            ORDER BY upload_date DESC
        ''', (user_id,))
        
        materials = cursor.fetchall()
        conn.close()
        
        # Get folders list
        folders_list = get_folders_list(user_id)
        
        if not materials and not folders_list:
            return html.Div("No study materials or folders uploaded yet")
            
        materials_list = []
        
        # Add folders first
        materials_list.extend(folders_list)
        
        # Add individual materials
        for mat_id, name, description, file_path, upload_date in materials:
            # Create the full URL path for the material
            mat_url = f"/static/study_materials/{user_id}/{file_path}"
            
            # Check if file exists
            file_exists = os.path.exists(os.path.join("static", "study_materials", str(user_id), file_path))
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-file me-2"),
                            html.H5(name, className="mb-0 d-inline")
                        ]),
                        dbc.Button(
                            html.I(className="fas fa-trash-alt"),
                            id={"type": "delete-material", "index": mat_id},
                            color="danger",
                            className="float-end",
                            size="sm"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody([
                    html.P(description if description else "No description provided", className="card-text"),
                    html.P(f"Uploaded: {upload_date}", className="text-muted small"),
                    html.A(
                        "Download",
                        href=mat_url if file_exists else "#",
                        target="_blank",
                        className="btn btn-primary btn-sm" if file_exists else "btn btn-secondary btn-sm disabled",
                        style={"pointerEvents": "none" if not file_exists else "auto"}
                    ),
                    html.Small(
                        "File not found" if not file_exists else "",
                        className="text-danger d-block mt-2"
                    )
                ])
            ], className="mb-3")
            materials_list.append(card)
            
        return html.Div(materials_list)
        
    except sqlite3.Error as e:
        print(f"Database error in get_study_materials_list: {str(e)}")
        return html.Div(f"Database error: {str(e)}", style={"color": "red"})
    except Exception as e:
        print(f"Error in get_study_materials_list: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return html.Div(f"Error loading study materials: {str(e)}", style={"color": "red"}) 