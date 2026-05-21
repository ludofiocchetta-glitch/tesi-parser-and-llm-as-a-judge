import mariadb
import json
import os
import sys
import time

def get_db_connection(max_retries=5, delay=3):
    retries = 0
    while retries < max_retries:
        try:
            conn = mariadb.connect(
                user="user",             
                password="password",
                host="mariadb_service",         
                port=3306,
                database="parser_db"
            )
            return conn
        except mariadb.Error as e:
            print(f"Attempt {retries + 1} failed. MariaDB Error: {e}")
            retries += 1
            time.sleep(delay)
    print("All attempts to connect to the database have failed. Exiting.")
    sys.exit(1)

def create_tables(cursor):    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_resources (
            url VARCHAR(2048) CHARACTER SET ascii COLLATE ascii_general_ci PRIMARY KEY,
            domain VARCHAR(255),
            title VARCHAR(2048),
            html_text LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_standard (
            url VARCHAR(2048) CHARACTER SET ascii COLLATE ascii_general_ci PRIMARY KEY,
            gold_text LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (url) REFERENCES web_resources(url) ON DELETE CASCADE
        )
    """)

def populate_database(conn, cursor):
    gs_dir = "/app/gs_data" 
    
    if not os.path.exists(gs_dir):
        print(f"Directory {gs_dir} non trovata.")
        return

    for filename in os.listdir(gs_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(gs_dir, filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                data_list = json.load(f)
                
                for item in data_list:
                    url = item.get("url")
                    domain = item.get("domain")
                    title = item.get("title")
                    html_text = item.get("html_text")
                    gold_text = item.get("gold_text")
                    
                    try:
                        cursor.execute("""
                            INSERT IGNORE INTO web_resources (url, domain, title, html_text)
                            VALUES (?, ?, ?, ?)
                        """, (url, domain, title, html_text))
                        
                        cursor.execute("""
                            INSERT IGNORE INTO gold_standard (url, gold_text)
                            VALUES (?, ?)
                        """, (url, gold_text))
                        
                    except mariadb.Error as e:
                        print(f"Error during insertion of URL {url}: {e}")
                        
    conn.commit()

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_tables(cursor)
    populate_database(conn, cursor)
    
    conn.close()
    print("Initialization of the database completed successfully.")

if __name__ == "__main__":
    setup_database()