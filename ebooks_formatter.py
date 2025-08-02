import dash_bootstrap_components as dbc
from dash import html, callback_context
import pandas as pd

def format_ebooks_table(df):
    """Format the ebooks with book-like cards"""
    # Apply filters if provided
    subject_filter = callback_context.states.get("ebook-subject-filter.value")
    state_filter = callback_context.states.get("ebook-state-filter.value")
    if subject_filter:
        df = df[df['subject'] == subject_filter]
    if state_filter:
        df = df[df['states'] == state_filter]
    
    cards = []
    for idx, row in df.iterrows():
        card = dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.Div(className="book-spine-line"),
                    html.H5(row['website'], className="book-card-title"),
                    html.P(f"Subject: {row['subject'] if pd.notna(row['subject']) else '-'}", 
                           className="book-card-info"),
                    html.P(f"State: {row['states']}", 
                           className="book-card-info"),
                    html.P(f"Preference: {row['preference']}", 
                           className="book-card-info text-muted"),
                    html.Div([
                        html.A("View Resource", 
                              href=row['link'],
                              target="_blank",
                              className="book-view-btn")
                    ], className="d-flex justify-content-start align-items-center")
                ], className="book-inner-content")
            ]),
            className="custom-book-card mb-4"
        )
        cards.append(dbc.Col(card, lg=4, md=6, sm=12))
    
    return html.Div([
        html.H3("Educational E-Books", className="ebooks-title"),
        html.P(f"Showing {len(df)} e-books resources", className="ebooks-count"),
        dbc.Row(cards, className="g-4")
    ], className="ebooks-container")
