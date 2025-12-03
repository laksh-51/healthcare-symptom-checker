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
        print(f"PostgreSQL connection error: {e}")
        return None


def create_query_table():
    """Creates the symptom_queries table if it does not exist."""
    conn = get_db_connection()
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
            print(f"Error creating table: {e}")
        finally:
            conn.close()


def log_query_result(symptoms_input: str, llm_response: Dict[str, Any]):
    """Logs the user's symptom input and the LLM response into the database."""
    conn = get_db_connection()
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
            print(f"Error logging query to database: {e}")
        finally:
            conn.close()
