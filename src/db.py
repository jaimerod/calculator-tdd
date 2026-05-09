import os
import duckdb
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'calculator.duckdb')

_connection = None

def get_connection():
    global _connection
    if _connection is None:
        _connection = duckdb.connect(DB_PATH)
        _connection.execute("""
            CREATE TABLE IF NOT EXISTS calculator_sessions (
                client_id VARCHAR PRIMARY KEY,
                state_json VARCHAR NOT NULL
            )
        """)
        _connection.execute("""
            CREATE TABLE IF NOT EXISTS calculator_history (
                id INTEGER PRIMARY KEY,
                client_id VARCHAR NOT NULL,
                expression VARCHAR NOT NULL,
                result VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        _connection.execute("""
            CREATE SEQUENCE IF NOT EXISTS history_seq START 1
        """)
    return _connection

def close_connection():
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None

def load_state(client_id):
    con = get_connection()
    row = con.execute(
        'SELECT state_json FROM calculator_sessions WHERE client_id = ?',
        [client_id]
    ).fetchone()
    if row:
        return json.loads(row[0])
    else:
        state = {
            'current_value': 0,
            'pending_op': None,
            'current_input': '',
            'just_evaluated': False,
            'last_op': None,
            'last_value_before_op': 0
        }
        con.execute(
            'INSERT INTO calculator_sessions (client_id, state_json) VALUES (?, ?)',
            [client_id, json.dumps(state)]
        )
        return state

def save_state(client_id, state):
    con = get_connection()
    con.execute(
        'INSERT OR REPLACE INTO calculator_sessions (client_id, state_json) VALUES (?, ?)',
        [client_id, json.dumps(state)]
    )

def add_history(client_id, expression, result):
    con = get_connection()
    con.execute(
        'INSERT INTO calculator_history (id, client_id, expression, result) VALUES (nextval(\'history_seq\'), ?, ?, ?)',
        [client_id, expression, result]
    )

def get_history(client_id, limit=50):
    con = get_connection()
    rows = con.execute(
        'SELECT expression, result FROM calculator_history WHERE client_id = ? ORDER BY id DESC LIMIT ?',
        [client_id, limit]
    ).fetchall()
    return [{'expression': r[0], 'result': r[1]} for r in rows]

def clear_history(client_id):
    con = get_connection()
    con.execute(
        'DELETE FROM calculator_history WHERE client_id = ?',
        [client_id]
    )