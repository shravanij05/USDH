def get_theme_colors():
    return {
        'primary': '#1a237e',
        'secondary': '#0d47a1',
        'accent': '#2962ff',
        'background': '#f5f6fa',
        'text': '#2c3e50',
        'success': '#2ecc71',
        'warning': '#f1c40f',
        'danger': '#e74c3c'
    }

def get_theme_styles():
    colors = get_theme_colors()
    return {
        'container': {
            'background': f'linear-gradient(135deg, {colors["primary"]} 0%, {colors["secondary"]} 100%)',
            'min-height': '100vh',
            'padding': '20px',
            'position': 'relative'
        },
        'card': {
            'background': 'rgba(255, 255, 255, 0.95)',
            'backdrop-filter': 'blur(10px)',
            'border-radius': '16px',
            'box-shadow': '0 8px 32px rgba(0, 0, 0, 0.1)',
            'border': '1px solid rgba(255, 255, 255, 0.2)'
        },
        'button': {
            'transition': 'all 0.3s ease',
            'border-radius': '8px',
            'font-weight': '500'
        }
    }
