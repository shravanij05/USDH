import dash_bootstrap_components as dbc
from dash import html, callback_context

def format_courses_table(df):
    """Format the courses table with minimal info and show details button"""
    # Apply filters if provided
    discipline_filter = callback_context.states.get("discipline-filter.value")
    if discipline_filter:
        df = df[df['dispcipline'] == discipline_filter]
    
    cards = []
    for i, row in df.iterrows():
        card = dbc.Card([
            dbc.CardBody([
                html.H5(row['course_name_'], className="course-title"),
                html.Div([
                    html.I(className="fas fa-globe me-2", style={'color': '#3498db'}),
                    html.Span(row['website_name'], className="text-muted"),
                ], className="website-info mb-3"),
                html.Div([
                    dbc.Button(
                        [
                            html.I(className="fas fa-external-link-alt me-2"),
                            "View Course"
                        ],
                        href=f"/course/{i}",  # Changed to use index-based routing
                        target="_blank",
                        color="primary",
                        className="course-btn",
                        style={
                            'background': 'linear-gradient(135deg, #3498db, #2980b9)',
                            'border': 'none',
                            'boxShadow': '0 4px 15px rgba(52, 152, 219, 0.2)',
                            'transition': 'all 0.3s ease'
                        }
                    )
                ], className="d-flex justify-content-start align-items-center mt-3")
            ])
        ], className="course-card mb-3 h-100", style={
            'border': 'none',
            'borderRadius': '15px',
            'boxShadow': '0 5px 15px rgba(0, 0, 0, 0.08)',
            'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
            'cursor': 'pointer'
        })
        cards.append(dbc.Col(card, lg=4, md=6, sm=12))
    
    return html.Div([
        html.H3("UG/PG Courses", className="courses-title mb-3"),
        html.P(f"Showing {len(df)} courses", className="courses-count text-muted mb-3"),
        dbc.Row(cards, className="courses-grid g-3")
    ], className="courses-container")
