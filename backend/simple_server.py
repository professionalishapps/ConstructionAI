"""Minimal HTTP server to serve MVP API endpoints without uvicorn.

Endpoints implemented:
- GET /api/health -> {"status": "ok"}
- GET /api/projects/current -> returns sample project + latest metric from Postgres

This uses the system venv and pg8000/psycopg2 to connect to the DB. It adds CORS headers
so the frontend at http://localhost:5173 can fetch the API.
"""
import os
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# DB driver selection
try:
    import pg8000
    DB_DRIVER = 'pg8000'
except Exception:
    try:
        import psycopg2
        DB_DRIVER = 'psycopg2'
    except Exception:
        DB_DRIVER = None

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'construction_db')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin123')

ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]


def get_db_connection():
    if DB_DRIVER == 'pg8000':
        return pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
    elif DB_DRIVER == 'psycopg2':
        return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    else:
        raise RuntimeError('No DB driver available (install pg8000 or psycopg2)')


# Ollama client (optional)
try:
    from utils.ollama_client import OllamaClient
except Exception:
    try:
        from backend.utils.ollama_client import OllamaClient
    except Exception:
        OllamaClient = None


class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        origin = self.headers.get('Origin')
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
        else:
            # allow localhost by default
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:5173')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            # Serve a small static UI from / or /static/* for MVP when Vite isn't available
            if path == '/' or path == '/index.html':
                static_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
                if os.path.exists(static_path):
                    with open(static_path, 'rb') as f:
                        content = f.read()
                    self._set_headers(200, 'text/html')
                    self.wfile.write(content)
                    return
                # fallthrough to 404

            if path.startswith('/static/'):
                rel = path[len('/static/'):]
                static_root = os.path.join(os.path.dirname(__file__), 'static')
                target = os.path.normpath(os.path.join(static_root, rel))
                if os.path.commonpath([static_root, target]) == static_root and os.path.exists(target):
                    # simple content-type mapping
                    if target.endswith('.js'):
                        ctype = 'application/javascript'
                    elif target.endswith('.css'):
                        ctype = 'text/css'
                    else:
                        ctype = 'application/octet-stream'
                    with open(target, 'rb') as f:
                        data = f.read()
                    self._set_headers(200, ctype)
                    self.wfile.write(data)
                    return

            if path == '/api/health':
                self._set_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
                return

            if path == '/api/projects/current':
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT project_id, name, type, location_lat, location_lon, contract_value, start_date, planned_completion, current_completion_pct FROM projects WHERE project_id = %s", ('PRJ-2025-001',))
                row = cur.fetchone()
                if not row:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'project': None}).encode('utf-8'))
                    return
                project = {
                    'project_id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'location': {'lat': float(row[3]), 'lon': float(row[4]) if row[4] is not None else None},
                    'contract_value': float(row[5]) if row[5] is not None else None,
                    'start_date': row[6].isoformat() if row[6] else None,
                    'planned_completion': row[7].isoformat() if row[7] else None,
                    'current_completion_pct': float(row[8]) if row[8] is not None else None,
                }
                cur.execute("SELECT date, spi, cpi, actual_pct_complete, cost_variance, schedule_variance_days, weather_risk_score FROM daily_metrics WHERE project_id=%s ORDER BY date DESC LIMIT 1", ('PRJ-2025-001',))
                m = cur.fetchone()
                latest_metric = None
                if m:
                    latest_metric = {
                        'date': m[0].isoformat() if m[0] else None,
                        'spi': float(m[1]) if m[1] is not None else None,
                        'cpi': float(m[2]) if m[2] is not None else None,
                        'actual_pct_complete': float(m[3]) if m[3] is not None else None,
                        'cost_variance': float(m[4]) if m[4] is not None else None,
                        'schedule_variance_days': int(m[5]) if m[5] is not None else None,
                        'weather_risk_score': int(m[6]) if m[6] is not None else None,
                    }
                cur.close()
                try:
                    conn.close()
                except Exception:
                    pass

                resp = {'project': project, 'latest_metric': latest_metric, 'agents': []}
                self._set_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
                return

            # Run agents and persist results
            if path == '/api/agents/run':
                from orchestrator.agent_runner import run_agent, run_all_agents
                import asyncio
                
                # Get project details and latest metrics
                conn = get_db_connection()
                cur = conn.cursor()
                
                # Get project details
                cur.execute("""
                    SELECT contract_value, start_date, planned_completion, current_completion_pct 
                    FROM projects 
                    WHERE project_id = %s
                """, ('PRJ-2025-001',))
                project = cur.fetchone()
                
                # Get latest metrics
                cur.execute("""
                    SELECT date, spi, cpi, actual_pct_complete, cost_variance, 
                           schedule_variance_days, weather_risk_score
                    FROM daily_metrics 
                    WHERE project_id = %s 
                    ORDER BY date DESC LIMIT 1
                """, ('PRJ-2025-001',))
                metrics = cur.fetchone()
                
                # Prepare input data for agents
                input_data = {
                    # Cost variance inputs
                    "budget": float(project[0]) if project[0] else 0,
                    "cpi": float(metrics[2]) if metrics[2] else 1.0,
                    "pct_complete": float(project[3]) if project[3] else 0,
                    "cost_variance": float(metrics[4]) if metrics[4] else 0,
                    "spent_to_date": float(project[0] * (project[3]/100.0)) if project[0] and project[3] else 0,
                    
                    # Weather impact inputs
                    "weather_data": {
                        "risk_score": int(metrics[6]) if metrics[6] else 0
                    },
                    "activity_type": "site_work",  # TODO: Get from current activities
                    "duration_days": 30,  # TODO: Get from schedule
                    
                    # Subcontractor inputs
                    "planned_days": 30,  # TODO: Get from schedule
                    "actual_days": 30 + (metrics[5] if metrics[5] else 0),
                    "critical_path": True,  # TODO: Get from schedule
                    "defects": 0,  # TODO: Get from quality reports
                    "rework_hours": 0,
                    "inspections_passed": 0,
                    "inspections_total": 0,
                    "incidents": 0,
                    "near_misses": 0,
                    "safety_observations": 0
                }

                # Create database session using SQLAlchemy
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                
                engine = create_engine(
                    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
                )
                Session = sessionmaker(bind=engine)
                db = Session()

                try:
                    # Run all agents
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results = loop.run_until_complete(
                        run_all_agents(db, 'PRJ-2025-001', input_data)
                    )
                    loop.close()

                    self._set_headers()
                    self.wfile.write(json.dumps(results).encode('utf-8'))
                    
                finally:
                    db.close()
                    cur.close()
                    conn.close()
                return

            if path == '/api/agents/history':
                from orchestrator.agent_runner import get_agent_history
                
                # Create database session
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                
                engine = create_engine(
                    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
                )
                Session = sessionmaker(bind=engine)
                db = Session()
                
                try:
                    results = get_agent_history(db, 'PRJ-2025-001', limit=10)
                    self._set_headers()
                    self.wfile.write(json.dumps(results).encode('utf-8'))
                finally:
                    db.close()
                return

            # fallback
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'not found'}).encode('utf-8'))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


def run(server_class=ThreadingHTTPServer, handler_class=SimpleHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving HTTP on port {port} (http://localhost:{port}/) ...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down server')
        httpd.server_close()


if __name__ == '__main__':
    run()
