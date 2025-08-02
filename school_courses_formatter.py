import dash_bootstrap_components as dbc
from dash import html

def format_courses2_table(df):
    """Format courses as individual cards similar to e-books layout"""
    cards = []
    for i, row in df.iterrows():
        # Create individual card for each course
        card = html.Div([
            # Card with green accent line
            html.Div([
                # Title section
                html.H4(row['subjects'], className="mb-4"),
                
                # Course details
                html.Div([
                    html.Strong("Subject: "),
                    html.Span(f"{row['subjects']}")
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("Grade: "),
                    html.Span(f"Grade {row['grade']}")
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("Preference: "),
                    html.Span("School")
                ], className="mb-3"),
                
                # Only View Resource button
                html.Div([
                    dbc.Button(
                        "View Resource",
                        href=row['video_link'],
                        target="_blank",
                        className="view-resource-btn"
                    )
                ], className="d-flex justify-content-start align-items-center")
            ], className="card-inner-content")
        ], className="e-book-card")
        
        # Wrap card in column for grid layout
        cards.append(dbc.Col(card, xl=4, lg=4, md=6, sm=12, className="mb-4"))
    
    return html.Div([
        # Section header
        html.H3("School Courses (Grades 1-12)", className="section-title"),
        html.P(f"Showing {len(df)} educational resources", className="resources-count"),
        
        # Cards grid
        dbc.Row(cards, className="g-4 mt-2")
    ], className="e-books-section")
