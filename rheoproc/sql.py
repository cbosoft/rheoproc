# rheoproc.sql
# light wrapper around the sqlite3 builtin module - tidies the API into a single function call.

import os
import sqlite3

def execute_sql(query, database):

    # proposed backup of database as txt file:
    # if not os.path.isfile(database):
    #     runsh('cat database.txt | sqlite3 .database.db')
        
    conn = sqlite3.connect(database)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
    finally:
        if conn:
            conn.close()
    return results

