import psycopg2
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional

load_dotenv()


def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """Establishes and returns a new PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        print("PostgreSQL connection successful.")
        return conn
    except Exception as e:
        # MANUAL RAISE EXCEPTION for connection failures
        print(f"PostgreSQL connection error: {e}")
        raise RuntimeError(f"DB Connection Error: {e}") 
        # The line above prevents the function from returning None silently.


def create_query_table():
    """Creates the symptom_queries table if it does not exist."""
    conn = get_db_connection() # Will raise exception if connection fails
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS symptom_queries (
                        id SERIAL PRIMARY KEY,
                        symptoms_input TEXT NOT NULL,
                        llm_response_json JSONB NOT NULL,
                        query_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                conn.commit()
                print("Database table 'symptom_queries' checked/created successfully.")
        except Exception as e:
            # MANUAL RAISE EXCEPTION for table creation failures
            print(f"Error creating table: {e}")
            raise RuntimeError(f"DB Table Creation Error: {e}") 
        finally:
            conn.close()


def log_query_result(symptoms_input: str, llm_response: Dict[str, Any]):
    """Logs the user's symptom input and the LLM response into the database."""
    conn = get_db_connection() # Will raise exception if connection fails
    if conn:
        try:
            response_json_string = json.dumps(llm_response)

            with conn.cursor() as cursor:
                insert_query = """
                    INSERT INTO symptom_queries (symptoms_input, llm_response_json)
                    VALUES (%s, %s);
                """
                cursor.execute(insert_query, (symptoms_input, response_json_string))
                conn.commit()
                print("Query logged to database successfully.")
        except Exception as e:
            # MANUAL RAISE EXCEPTION for query logging failures
            print(f"Error logging query to database: {e}")
            raise RuntimeError(f"DB Log Query Error: {e}")
        finally:
            conn.close()

def get_query_history(limit: int = 10) -> list:
    """Fetches the most recent symptom queries from the database."""
    conn = get_db_connection() # Will raise exception if connection fails
    history = []
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id, 
                        symptoms_input, 
                        llm_response_json, 
                        query_timestamp 
                    FROM symptom_queries
                    ORDER BY id DESC
                    LIMIT %s;
                """, (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    
                    # FIX: Explicitly deserialize the JSONB column if it came back as a string
                    json_data = item.get('llm_response_json')
                    if isinstance(json_data, str):
                        try:
                            item['llm_response_json'] = json.loads(json_data)
                        except json.JSONDecodeError as e:
                            # Log and skip malformed entries, but don't stop the whole query
                            print(f"History Item Parsing Error for ID {item.get('id', 'Unknown')}: {e}")
                            item['llm_response_json'] = {} 
                    
                    # Safely format timestamp
                    try:
                        item['query_timestamp'] = item['query_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    except AttributeError:
                         item['query_timestamp'] = str(item['query_timestamp'])

                    history.append(item)
        
        except Exception as e:
            # MANUAL RAISE EXCEPTION for history fetching failures
            print(f"Error fetching history from database: {e}")
            raise RuntimeError(f"DB History Fetch Error: {e}")
        finally:
            conn.close()
            
    return history