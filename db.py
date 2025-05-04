import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class DatabaseService:
    """
    Service layer for handling database operations with error handling.
    """
    def __init__(self):
        self.conn = None

    def get_connection(self):
        """
        Establishes and returns a database connection.  Handles connection errors.
        """
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(
                    host=os.getenv("POSTGRES_HOST"),
                    port=os.getenv("POSTGRES_PORT"),
                    dbname=os.getenv("POSTGRES_DB"),
                    user=os.getenv("POSTGRES_USER"),
                    password=os.getenv("POSTGRES_PASSWORD"),
                    cursor_factory=RealDictCursor
                )
            return self.conn
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")  # Log the error
            raise  # Re-raise the exception for the caller to handle

    def close_connection(self):
        """Closes the database connection if it's open."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager to handle connection lifecycle."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the connection when exiting the context."""
        self.close_connection()

    def execute_query(self, query, params=None, fetchone=False):
        """
        Executes a database query and handles potential errors.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): Parameters to pass to the query. Defaults to None.
            fetchone (bool, optional): Whether to fetch only one result. Defaults to False.

        Returns:
            list or dict: The query results, or None on error.  Returns an empty list if no results.

        Raises:
            psycopg2.Error: If there's an error executing the query.
        """
        try:
            conn = self.get_connection()  # Get connection within the method
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()  # important to commit
                if fetchone is True:
                    return cur.fetchone()
                elif fetchone is False:
                    return cur.fetchall()
                else:
                    return None
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise  # Re-raise to be caught by caller
        finally:
            self.close_connection()

    def fetch_transcript_status(self, video_id):
        """Fetches the transcript and status for a given video ID.

        Args:
            video_id (str): The ID of the video.

        Returns:
            tuple: (transcript, status), or (None, None) if not found.
        """
        query = "SELECT transcript, status FROM video_transcript_mapping WHERE video_id = %s"
        try:
            result = self.execute_query(query, (video_id,), fetchone=True)
            if result:
                return result["transcript"], result["status"]
            else:
                return None, None
        except psycopg2.Error:
            return None, None  # Handle the error, and return a default

    def fetch_status_by_job_id(self, job_id):
        """Fetches the status of a video transcript mapping by job ID.

        Args:
            job_id (str): The ID of the job.

        Returns:
            str: The status, or None if not found.
        """
        query = """
            SELECT vtm.status
            FROM job_chat_context jvc
            INNER JOIN video_transcript_mapping vtm ON jvc.video_id = vtm.video_id
            WHERE jvc.job_id = %s
        """
        try:
            result = self.execute_query(query, (job_id,), fetchone=True)
            return result["status"] if result else None
        except psycopg2.Error:
            return None

    def save_or_update_transcript(self, video_id, transcript=None, status=None):
        """Saves or updates the transcript and/or status for a video.

        Args:
            video_id (str): The ID of the video.
            transcript (str, optional): The transcript text. Defaults to None.
            status (str, optional): The status of the transcript. Defaults to None.

        Raises:
            ValueError: If neither transcript nor status is provided.
        """
        if transcript is None and status is None:
            raise ValueError("At least one of 'transcript' or 'status' must be provided")

        fields_to_update = {}
        if transcript is not None:
            fields_to_update["transcript"] = transcript
        if status is not None:
            fields_to_update["status"] = status

        columns = ["video_id"] + list(fields_to_update.keys())
        values = [video_id] + list(fields_to_update.values())

        insert_columns = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in fields_to_update.keys()])

        query = f"""
            INSERT INTO video_transcript_mapping ({insert_columns})
            VALUES ({placeholders})
            ON CONFLICT (video_id)
            DO UPDATE SET {update_clause}
        """
        self.execute_query(query, values, fetchone=None)


    def fetch_context(self, job_id):
        """Fetches the context for a given job ID.

        Args:
            job_id (str): The ID of the job.

        Returns:
            list: The context, or an empty list if not found.
        """
        query = "SELECT context FROM job_chat_context WHERE job_id = %s"
        try:
            result = self.execute_query(query, (job_id,), fetchone=True)
            return json.loads(result["context"]) if result and result["context"] else []
        except psycopg2.Error:
            return []

    def fetch_video_details(self, job_id):
        """Fetches the video ID associated with a job ID.

        Args:
            job_id (str): The ID of the job.

        Returns:
            str: The video ID, or None if not found.
        """
        query = "SELECT video_id FROM job_chat_context WHERE job_id = %s"
        try:
            result = self.execute_query(query, (job_id,), fetchone=True)
            return result["video_id"] if result else None
        except psycopg2.Error:
            return None

    def create_or_update_context(self, job_id, video_id, context):
        """Creates or updates the context for a job ID and video ID.

        If context is None, it inserts an empty array.
        If context is a list, it appends it to the existing jsonb array.
        """
        query = """
                INSERT INTO job_chat_context (job_id, video_id, context)
                VALUES (%s, %s, %s::jsonb)
                ON CONFLICT (job_id) DO UPDATE
                SET context = 
                    CASE
                        WHEN job_chat_context.context IS NULL THEN EXCLUDED.context
                        ELSE job_chat_context.context || jsonb_build_array(
                            jsonb_build_object(
                                'context', EXCLUDED.context, 
                                'timestamp', NOW()
                            )
                        )
                    END
        """
        if context is None:
            context = []  # treat None as empty list

        self.execute_query(query, (job_id, video_id, json.dumps(context)), fetchone=None)

