"""
Main application entry point for the HBnB API server.
"""

from app import create_app
from app.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    # Server configuration
    host = '0.0.0.0'  # Listen on all interfaces
    port = 5000
    debug = True
    
    print("\n" + "="*50)
    print("🚀 HBnB API Server")
    print("="*50)
    
    # Display available routes
    print("\n🔍 Available routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join(sorted((rule.methods or set()) - {'OPTIONS', 'HEAD'}))
        print(f"  {rule.rule} -> {rule.endpoint} [{methods}]")
    
    # Display important URLs (using 127.0.0.1 for clickable links in terminal)
    display_url = f"http://127.0.0.1:{port}"
    print("\n🌐 Important URLs (clickable in terminal):")
    print(f"  📱 Swagger UI:    {display_url}/")
    print(f"  👤 Users API:     {display_url}/api/v1/users")
    print(f"  🏠 Amenities API: {display_url}/api/v1/amenities")
    print(f"  📍 Places API:    {display_url}/api/v1/places")
    print(f"  🏠 Reviews API: {display_url}/api/v1/reviews")
    
    print("\n⚙️  Configuration:")
    print(f"  • Debug mode: {'✅ ON' if debug else '❌ OFF'}")
    print(f"  • Host: 0.0.0.0 (accessible from network)")
    print(f"  • Port: {port}")
    
    print("\n" + "="*50)
    print("Starting server... (Press Ctrl+C to stop)")
    print("="*50 + "\n")
    
    # Start the development server
    app.run(host=host, port=port, debug=debug, use_reloader=False)