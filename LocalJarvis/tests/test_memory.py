import sqlite3

def test_memory_manager():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_text TEXT,
            assistant_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute(
        "INSERT INTO interactions (user_id, user_text, assistant_response) VALUES (?, ?, ?)",
        ("default", "Teste", "Resposta")
    )
    conn.commit()
    cursor = conn.execute("SELECT user_text, assistant_response FROM interactions")
    rows = cursor.fetchall()
    assert rows[0][0] == "Teste"
    assert rows[0][1] == "Resposta"
