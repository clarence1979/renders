#!/usr/bin/env python3
"""
Flask app for Enterprise AI Assistant - Render.com deployment
Save this as 'app.py' in your GitHub repository
"""

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
LOG_FILE = 'enterprise_ai_global_logs.txt'
PORT = int(os.environ.get('PORT', 10000))  # Render uses PORT environment variable

@app.route('/')
def home():
    """Serve the main HTML file"""
    try:
        return send_from_directory('.', 'index.html')
    except FileNotFoundError:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enterprise AI Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .status { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }
                code { background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🖥️ Enterprise AI Assistant Server</h1>
            
            <div class="status">
                <h3>✅ Server Status: Running on Render.com</h3>
                <p><strong>Logging endpoint:</strong> <code>/api/log</code></p>
                <p><strong>Status endpoint:</strong> <code>/status</code></p>
                <p><strong>Log file:</strong> <code>{{ log_file }}</code></p>
            </div>
            
            <div class="info">
                <h3>📋 Next Steps</h3>
                <ol>
                    <li>Upload your <code>index.html</code> file to the repository</li>
                    <li>The Enterprise AI app will be available at this URL</li>
                    <li>All logs will be saved to the server automatically</li>
                </ol>
            </div>
            
            <div class="info">
                <h3>🔗 Useful Links</h3>
                <ul>
                    <li><a href="/status">Server Status (JSON)</a></li>
                    <li><a href="/server-status">Detailed Status Page</a></li>
                </ul>
            </div>
        </body>
        </html>
        """, log_file=LOG_FILE)

@app.route('/index.html')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/api/log', methods=['POST', 'OPTIONS'])
def handle_log():
    """Handle logging requests from the Enterprise AI app"""
    
    if request.method == 'OPTIONS':
        # Handle preflight requests
        return '', 200
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract log information
        log_entry = data.get('logEntry', {})
        formatted_line = data.get('formattedLine', '')
        file_name = data.get('fileName', LOG_FILE)
        
        if not formatted_line:
            return jsonify({'error': 'No log data provided'}), 400
        
        # Write to log file
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(formatted_line + '\n')
        
        # Log to console for monitoring (visible in Render logs)
        log_type = log_entry.get('type', 'UNKNOWN')
        query = log_entry.get('query', '')[:50]
        print(f"📝 Log saved: {log_type} - {query}")
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Log saved successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error saving log: {e}")
        return jsonify({'error': f'Failed to save log: {str(e)}'}), 500

@app.route('/status')
def status():
    """API status endpoint"""
    log_exists = os.path.exists(LOG_FILE)
    log_size = os.path.getsize(LOG_FILE) if log_exists else 0
    
    return jsonify({
        'status': 'Server is running',
        'platform': 'Render.com',
        'endpoint': '/api/log',
        'log_file': LOG_FILE,
        'log_exists': log_exists,
        'log_size': log_size,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/server-status')
def server_status():
    """Detailed server status page"""
    log_exists = os.path.exists(LOG_FILE)
    log_size = os.path.getsize(LOG_FILE) if log_exists else 0
    
    # Read recent log entries
    recent_logs = "No logs yet. Start using the Enterprise AI app to see logs here."
    if log_exists:
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                recent_logs = ''.join(recent_lines) if recent_lines else "Log file is empty."
        except Exception as e:
            recent_logs = f"Error reading log file: {e}"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise AI Log Server - Render.com</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .status { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }
            code { background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto; white-space: pre-wrap; }
        </style>
        <meta http-equiv="refresh" content="30">
    </head>
    <body>
        <h1>🖥️ Enterprise AI Log Server</h1>
        <p><em>Hosted on Render.com</em></p>
        
        <div class="status">
            <h3>✅ Server Status: Running</h3>
            <p><strong>Platform:</strong> Render.com</p>
            <p><strong>Endpoint:</strong> <code>/api/log</code></p>
            <p><strong>Method:</strong> POST</p>
            <p><strong>Log file:</strong> <code>{{ log_file }}</code></p>
            <p><strong>Log exists:</strong> {{ 'Yes' if log_exists else 'No' }}</p>
            <p><strong>Log size:</strong> {{ "{:,}".format(log_size) }} bytes</p>
            <p><strong>Server time:</strong> {{ server_time }}</p>
        </div>
        
        <div class="info">
            <h3>📋 Usage Instructions</h3>
            <ol>
                <li>Your Enterprise AI app is available at: <a href="/">{{ base_url }}</a></li>
                <li>Start using the AI - all logs will be saved automatically</li>
                <li>This page auto-refreshes every 30 seconds</li>
            </ol>
        </div>
        
        <div class="info">
            <h3>📝 Recent Log Entries</h3>
            <pre>{{ recent_logs }}</pre>
        </div>
        
        <p><small>
            <a href="/">Home</a> | 
            <a href="/status">API Status</a> | 
            <a href="/server-status">Refresh</a>
        </small></p>
    </body>
    </html>
    """
    
    return render_template_string(html_template,
        log_file=LOG_FILE,
        log_exists=log_exists,
        log_size=log_size,
        server_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        base_url=request.host_url,
        recent_logs=recent_logs
    )

# Health check endpoint for Render
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print(f"🚀 Starting Enterprise AI Server on port {PORT}")
    print(f"📝 Logs will be saved to: {LOG_FILE}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
