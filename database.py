import supabase
import psycopg2
import os

class Database:
    def __init__(self, database_url) -> None:
        self.con = psycopg2.connect(database_url)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self  # This method allows the class to be used in a 'with' statement.

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()  # Corrected to use the right attribute name for the cursor
        self.con.close()  # Corrected to use the right attribute name for the connection
        # Handle exceptions if necessary
        if exc_type:
            raise

    def upload_file(self, file_path):
        file_name = os.path.basename(file_path)
        result = self.client.storage().from_("pestimage").upload(file_name, file_path)
        public_url = self.client.storage().from_("pestimage").get_public_url(file_name)
        return public_url.data['publicURL']

    def insert_record(self, file_name, url, description):
        data = {
            "file_name": file_name,
            "url": url,
            "description": description,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.client.table("image_descriptions").insert(data).execute()

    def create_table(self):
        # [Assume table is already created on Supabase UI]
        pass
