#!/usr/bin/env python3

import os
import psycopg2
from flask import Flask, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'labdb'),
    'user': os.environ.get('DB_USER', 'labuser'),
    'password': os.environ.get('DB_PASSWORD', 'SecurePass123!')
}

FLASK_PORT = int(os.environ.get('FLASK_PORT', 80))

# HTML template for home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab 2 - Multi-tier Architecture</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        h2 {
            color: #764ba2;
            margin-top: 30px;
        }
        .info-box {
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .endpoint {
            background: #f9f9f9;
            border: 1px solid #ddd;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
        }
        .endpoint code {
            color: #d63384;
        }
        .success {
            color: #28a745;
            font-weight: bold;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        a {
            color: #667eea;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        ul {
            line-height: 1.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Lab 2: VM + VNet - Multi-tier Architecture</h1>

        <div class="info-box">
            <p class="success">✓ Aplikacja działa poprawnie!</p>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>Hostname:</strong> {{ hostname }}</p>
        </div>

        <h2>Architektura</h2>
        <p>Ta aplikacja demonstruje architekturę multi-tier w Azure:</p>
        <ul>
            <li><strong>Presentation Layer:</strong> Przeglądarka użytkownika (HTTP)</li>
            <li><strong>Application Layer:</strong> Flask app na vm-app ({{ hostname }})</li>
            <li><strong>Data Layer:</strong> PostgreSQL na vm-db ({{ db_host }})</li>
        </ul>

        <h2>Dostępne endpointy</h2>

        <div class="endpoint">
            <strong>GET</strong> <code>/</code><br>
            Strona główna (ta strona)
        </div>

        <div class="endpoint">
            <strong>GET</strong> <code>/db-test</code><br>
            Test połączenia z bazą danych PostgreSQL<br>
            <a href="/db-test" target="_blank">→ Kliknij aby przetestować</a>
        </div>

        <div class="endpoint">
            <strong>GET</strong> <code>/health</code><br>
            Health check endpoint<br>
            <a href="/health" target="_blank">→ Kliknij aby sprawdzić</a>
        </div>

        <h2>Konfiguracja sieci</h2>
        <ul>
            <li><strong>VNet:</strong> vnet-lab2 (10.1.0.0/16)</li>
            <li><strong>App Subnet:</strong> snet-app (10.1.1.0/24)</li>
            <li><strong>DB Subnet:</strong> snet-db (10.1.2.0/24)</li>
            <li><strong>Bastion Subnet:</strong> AzureBastionSubnet (10.1.254.0/26)</li>
        </ul>

        <h2>Bezpieczeństwo</h2>
        <ul>
            <li>✓ Baza danych w prywatnej podsieci (bez public IP)</li>
            <li>✓ NSG blokuje bezpośredni dostęp do DB z internetu</li>
            <li>✓ Komunikacja app-DB tylko wewnątrz VNet</li>
            <li>✓ SSH dostępny tylko przez Azure Bastion</li>
        </ul>

        <div class="footer">
            <p>Cloud Computing Lab - WAT 2025</p>
            <p>Lab 2: VM + VNet architecture</p>
        </div>
    </div>
</body>
</html>
"""


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


@app.route('/')
def home():
    """Home page with application info"""
    import socket
    return render_template_string(
        HOME_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        hostname=socket.gethostname(),
        db_host=DB_CONFIG['host']
    )


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'lab2-flask-app',
        'version': '1.0.0'
    })


@app.route('/db-test')
def db_test():
    """Test database connectivity and return data"""
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute test query
        cursor.execute("SELECT id, message, created_at FROM test_table ORDER BY id;")
        rows = cursor.fetchall()

        # Format results
        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'message': row[1],
                'created_at': row[2].isoformat() if row[2] else None
            })

        # Close connection
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'database': DB_CONFIG['database'],
            'host': DB_CONFIG['host'],
            'table': 'test_table',
            'row_count': len(data),
            'data': data,
            'timestamp': datetime.now().isoformat()
        })

    except psycopg2.OperationalError as e:
        return jsonify({
            'status': 'error',
            'message': 'Cannot connect to database',
            'error': str(e),
            'database_host': DB_CONFIG['host'],
            'database_name': DB_CONFIG['database'],
            'troubleshooting': [
                'Check if PostgreSQL is running on vm-db',
                'Verify pg_hba.conf allows connections from app subnet (10.1.1.0/24)',
                'Check NSG rules allow port 5432 between subnets',
                'Verify DB_HOST environment variable is set to vm-db private IP',
                'Test network connectivity: nc -zv $DB_HOST 5432'
            ]
        }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Database query failed',
            'error': str(e),
            'error_type': type(e).__name__
        }), 500


@app.route('/config')
def config():
    """Display current configuration (without sensitive data)"""
    return jsonify({
        'database': {
            'host': DB_CONFIG['host'],
            'database': DB_CONFIG['database'],
            'user': DB_CONFIG['user'],
            'password': '***hidden***'
        },
        'flask': {
            'port': FLASK_PORT,
            'debug': app.debug
        },
        'environment': {
            'DB_HOST': os.environ.get('DB_HOST', 'not set'),
            'DB_NAME': os.environ.get('DB_NAME', 'not set'),
            'DB_USER': os.environ.get('DB_USER', 'not set'),
            'FLASK_PORT': os.environ.get('FLASK_PORT', 'not set')
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Lab 2 - Multi-tier Architecture Flask Application")
    print("=" * 60)
    print(f"Database Host: {DB_CONFIG['host']}")
    print(f"Database Name: {DB_CONFIG['database']}")
    print(f"Database User: {DB_CONFIG['user']}")
    print(f"Flask Port: {FLASK_PORT}")
    print("=" * 60)
    print(f"Starting server on 0.0.0.0:{FLASK_PORT}")
    print("Available endpoints:")
    print(f"  - http://0.0.0.0:{FLASK_PORT}/")
    print(f"  - http://0.0.0.0:{FLASK_PORT}/health")
    print(f"  - http://0.0.0.0:{FLASK_PORT}/db-test")
    print(f"  - http://0.0.0.0:{FLASK_PORT}/config")
    print("=" * 60)

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=FLASK_PORT,
        debug=False
    )
