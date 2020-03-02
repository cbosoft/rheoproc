import os
import sqlite3

def execute_sql(query, database):

    # proposed backup of database as txt file:
    # if not os.path.isfile(database):
    #     runsh('cat database.txt | sqlite3 .database.db')
        
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    return results
    
