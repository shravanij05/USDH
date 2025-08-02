from dash import html, dcc, dash_table, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd

def manage_schemes_layout():
    # Connect to the database
    conn = sqlite3.connect('data/USDH.db')
    # Get scholarships data
    schemes_df = pd.read_sql_query("SELECT * FROM schemes", conn)
    conn.close()
    
    layout= html.Div([
        html.Div([
            html.I(className="fas fa-arrow-left me-2", style={'color': '#1a73e8'}),
            html.Button("Back to Dashboard", id="back-to-dashboard", className="edu-button mb-4", n_clicks=0)
        ], style={'textAlign': 'left'}),
        
        html.H2("Educational Schemes Management", className="mb-4", style={
            'color': 'white',
            'textShadow': '2px 2px 4px rgba(0,0,0,0.2)',
            'fontWeight': '700'
        }),
        
        # Schemes management section
        html.Div([
            html.Div([
                html.H4("Scholarships & Educational Schemes", style={
                    'color': 'white',
                    'textShadow': '1px 1px 3px rgba(0,0,0,0.2)',
                    'fontWeight': '600'
                }),
                dbc.Button("Add New Scheme", id="add-scheme-btn", className="edu-button", n_clicks=0)
            ], className="d-flex justify-content-between align-items-center mb-3"),
            
            # Schemes data table
            dash_table.DataTable(
                id='schemes-table',
                columns=[
                    {"name": "Name", "id": "name"},
                    {"name": "Benefits", "id": "benefits"},
                    {"name": "Eligibility Criteria", "id": "eligiblity_criteria"},
                    {"name": "More Info", "id": "for_more_info"}
                ],
                data=schemes_df.to_dict('records'),
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': '#e8f0fe',
                    'color': '#1a73e8',
                    'border': '1px solid #d2e3fc',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'backgroundColor': '#ffffff',
                    'color': '#1a73e8',
                    'border': '1px solid #d2e3fc',
                    'padding': '12px',
                    'textAlign': 'left',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fe'
                    },
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': '#e8f0fe',
                        'border': '1px solid #1a73e8'
                    }
                ],
                row_selectable="single",
                style_cell_conditional=[
                    {'if': {'column_id': 'eligiblity_criteria'},
                     'width': '25%'},
                    {'if': {'column_id': 'benefits'},
                     'width': '25%'},
                ]
            ),
            
            # Action buttons
            html.Div([
                dbc.Button("Edit", id="edit-scheme-btn", className="edu-button mx-1", n_clicks=0),
                dbc.Button("Delete", id="delete-scheme-btn", className="edu-button mx-1", n_clicks=0),
                dbc.Button("View Details", id="view-scheme-btn", className="edu-button mx-1", n_clicks=0),
            ], className="d-flex justify-content-end mt-3")
        ], className="mt-4"),
        
        # Modal for adding/editing schemes
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Scholarship/Scheme Details", style={'color': '#1a73e8'}), close_button=True),
            dbc.ModalBody([
                dbc.Input(id="scheme-name-input", placeholder="Scheme Name", type="text", className="edu-input mb-3"),
                dbc.Select(
                    id="scheme-type-input",
                    options=[
                        {"label": "Scholarship", "value": "scholarship"},
                        {"label": "Grant", "value": "grant"},
                        {"label": "Fee Waiver", "value": "fee_waiver"},
                        {"label": "Education Loan", "value": "loan"}
                    ],
                    placeholder="Select Type",
                    className="edu-input mb-3"
                ),
                dbc.Textarea(id="scheme-benefits-input", placeholder="Benefits", className="edu-input mb-3", style={'height': '100px'}),
                dbc.Textarea(id="scheme-eligibility-input", placeholder="Eligibility Criteria", className="edu-input mb-3", style={'height': '100px'}),
                dbc.Input(id="scheme-link-input", placeholder="More Info Link", type="text", className="edu-input mb-3"),
                dbc.Textarea(id="scheme-notes-input", placeholder="Additional Notes", className="edu-input mb-3", style={'height': '100px'})
            ]),
            dbc.ModalFooter([
                dbc.Button("Save", id="save-scheme-btn", className="edu-button", n_clicks=0),
                dbc.Button("Cancel", id="cancel-scheme-btn", className="edu-button", n_clicks=0)
            ])
        ], id="scheme-modal", size="lg", is_open=False, style={'color': '#1a73e8', 'backgroundColor': '#ffffff'}),
        
        # Scheme details modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="scheme-detail-title", style={'color': '#1a73e8'}), close_button=True),
            dbc.ModalBody(id="scheme-detail-body"),
            dbc.ModalFooter([
                dbc.Button("Close", id="close-scheme-detail-btn", className="edu-button", n_clicks=0)
            ])
        ], id="scheme-detail-modal", size="lg", is_open=False, style={'color': '#1a73e8', 'backgroundColor': '#ffffff'}),
        
        # Add scheme success/error notification
        html.Div(id="scheme-notification", className="mt-3")
    ], className="p-4")

    return layout
# Register callbacks for the schemes management functionality in your main app file
# For example:
# @app.callback(
#     Output("scheme-modal", "is_open"),
#     [Input("add-scheme-btn", "n_clicks"),
#      Input("edit-scheme-btn", "n_clicks"),
#      Input("save-scheme-btn", "n_clicks"),
#      Input("cancel-scheme-btn", "n_clicks")],
#     [State("scheme-modal", "is_open")]
# )
# def toggle_scheme_modal(add, edit, save, cancel, is_open):
#     ctx = callback_context
#     if not ctx.triggered:
#         return is_open
#     else:
#         button_id = ctx.triggered[0]["prop_id"].split(".")[0]
#         if button_id in ["add-scheme-btn", "edit-scheme-btn"]:
#             return True
#         elif button_id in ["save-scheme-btn", "cancel-scheme-btn"]:
#             return False
#         return is_open