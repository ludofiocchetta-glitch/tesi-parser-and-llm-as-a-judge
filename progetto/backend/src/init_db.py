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

def destroy_tables(cursor):
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    cursor.execute("DROP TABLE IF EXISTS evaluation_results")
    cursor.execute("DROP TABLE IF EXISTS parsed_pages")
    cursor.execute("DROP TABLE IF EXISTS gold_standard")
    cursor.execute("DROP TABLE IF EXISTS web_resources")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def create_tables(cursor):  

    # web_resources table (url, domain, title, html_text, created_at)  
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_resources (
            url VARCHAR(2048) CHARACTER SET ascii COLLATE ascii_general_ci PRIMARY KEY,
            domain VARCHAR(255),
            title VARCHAR(2048),
            html_text LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # gold_standard table (url, gold_text, created_at)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_standard (
            url VARCHAR(2048) CHARACTER SET ascii COLLATE ascii_general_ci PRIMARY KEY,
            gold_text LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (url) REFERENCES web_resources(url) ON DELETE CASCADE
        )
    """)
    # parsed_pages table (url, parsed_text, created_at)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parsed_pages (
            url VARCHAR(2048) CHARACTER SET ascii COLLATE ascii_general_ci PRIMARY KEY,
            parsed_text LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (url) REFERENCES web_resources(url) ON DELETE CASCADE
        )
    """)

    # evaluation_results table (url, token level metrics, LLM judgments, evaluated_at)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_results (
            url VARCHAR(2048) CHARACTER SET ascii COLLATE ascii_general_ci PRIMARY KEY,
            
            -- Token Level metrics
            precision_val FLOAT,
            recall FLOAT,
            f1 FLOAT,
            
            -- XEval metrics
            jaccard_similarity FLOAT,
            bigram_overlap FLOAT,
            cosine_similarity FLOAT,
            meteor FLOAT,
            bert_score FLOAT,
            
            -- LLM judgments
            judge_score FLOAT,
            judge_feedback TEXT,
            
            evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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

                        cursor.execute("""
                            INSERT IGNORE INTO evaluation_results 
                            (url, precision_val, recall, f1, jaccard_similarity, bigram_overlap, cosine_similarity, meteor, bert_score, judge_score, judge_feedback)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            url, 
                            None,  
                            None, 
                            None,
                            None,  
                            None,
                            None, 
                            None,  
                            None,  
                            None,  
                            None
                        ))
                        
                    except mariadb.Error as e:
                        print(f"Error during insertion of URL {url}: {e}")
                        
    conn.commit()

def destroy_database():
    d = 9

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    destroy_tables(cursor)
    create_tables(cursor)
    populate_database(conn, cursor)
    
    conn.close()
    print("Initialization of the database completed successfully.")

if __name__ == "__main__":
    
    setup_database()