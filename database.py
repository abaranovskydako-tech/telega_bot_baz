import sqlite3
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str, username: str = None, password: str = None):
        self.db_path = db_path
        self.username = username
        self.password = password
        self.connection = None
        
    def connect(self) -> bool:
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_table_structure(self, table_name: str) -> Optional[List[Dict[str, Any]]]:
        if not self.connection:
            if not self.connect():
                return None
                
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            table_info = []
            for col in columns:
                table_info.append({
                    'cid': col[0],
                    'name': col[1],
                    'type': col[2],
                    'notnull': col[3],
                    'default_value': col[4],
                    'pk': col[5]
                })
            
            return table_info
        except Exception as e:
            print(f"Error getting table structure: {e}")
            return None
    
    def get_all_tables(self) -> List[str]:
        if not self.connection:
            if not self.connect():
                return []
                
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        except Exception as e:
            print(f"Error getting tables: {e}")
            return []
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[tuple]]:
        if not self.connection:
            if not self.connect():
                return None
                
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return None
        except Exception as e:
            print(f"Query execution failed: {e}")
            return None
    
    def insert_questionnaire_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        if not data:
            return False
            
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            self.execute_query(query, values)
            return True
        except Exception as e:
            print(f"Failed to insert data: {e}")
            return False
    
    def get_database_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        schema = {}
        tables = self.get_all_tables()
        
        for table in tables:
            table_structure = self.get_table_structure(table)
            if table_structure:
                schema[table] = table_structure
                
        return schema
