import os
import uuid
import sqlite3
import datetime
from supabase import create_client, Client

import config

supabase_client: Client = None

# Initialize real Supabase client if not in mock mode
if not config.IS_MOCK_MODE:
    try:
        supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        print("Falling back to local mock mode.")
        config.IS_MOCK_MODE = True

# SQLite Mock Database Setup
MOCK_DB_PATH = "local_mandi.db"

def init_mock_db():
    """Initializes a local SQLite database to mimic Supabase tables for testing/offline use."""
    conn = sqlite3.connect(MOCK_DB_PATH)
    cursor = conn.cursor()
    
    # Create mock users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        role TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Create mock scans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        produce_type TEXT NOT NULL,
        grade TEXT NOT NULL,
        confidence REAL NOT NULL,
        status TEXT NOT NULL,
        image_url TEXT NOT NULL,
        color_uniformity REAL,
        defect_score REAL,
        size_score REAL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.commit()
    conn.close()

if config.IS_MOCK_MODE:
    init_mock_db()

# --- Auth Operations ---

def sign_up_user(email: str, password: str, full_name: str, role: str) -> dict:
    """Signs up a new user and creates their profile."""
    if config.IS_MOCK_MODE:
        conn = sqlite3.connect(MOCK_DB_PATH)
        cursor = conn.cursor()
        try:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {"success": False, "error": "User already exists with this email."}
            
            user_id = str(uuid.uuid4())
            now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            cursor.execute(
                "INSERT INTO users (id, email, password, full_name, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, email, password, full_name, role, now_str)
            )
            conn.commit()
            
            # Create a mock session token
            token = f"mock-jwt-token-{user_id}"
            return {
                "success": True,
                "user": {"id": user_id, "email": email, "full_name": full_name, "role": role},
                "token": token
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    else:
        try:
            # 1. Sign up user in Supabase Auth
            auth_response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if not auth_response.user:
                return {"success": False, "error": "Failed to create user."}
            
            user_id = auth_response.user.id
            
            # 2. Insert profile info into public.profiles table
            profile_response = supabase_client.table("profiles").insert({
    "id": user_id,
    "full_name": full_name,
    "email": email,
    "role": role
}).execute()
            
            # Access session token
            token = auth_response.session.access_token if auth_response.session else ""
            
            return {
                "success": True,
                "user": {"id": user_id, "email": email, "full_name": full_name, "role": role},
                "token": token
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

def sign_in_user(email: str, password: str) -> dict:
    """Authenticates a user and returns a session token."""
    if config.IS_MOCK_MODE:
        conn = sqlite3.connect(MOCK_DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, email, password, full_name, role FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Invalid email or password."}
            
            user_id, db_email, db_password, full_name, role = row
            # Simple password check (for mock purposes, plaintext is used. Real Supabase Auth uses bcrypt)
            if password != db_password:
                return {"success": False, "error": "Invalid email or password."}
                
            token = f"mock-jwt-token-{user_id}"
            return {
                "success": True,
                "user": {"id": user_id, "email": db_email, "full_name": full_name, "role": role},
                "token": token
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    else:
        try:
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                return {"success": False, "error": "Authentication failed."}
                
            user_id = auth_response.user.id
            
            # Fetch profile
            profile_response = supabase_client.table("profiles").select("full_name, role").eq("id", user_id).execute()
            profile_data = profile_response.data[0] if profile_response.data else {"full_name": "", "role": "farmer"}
            
            token = auth_response.session.access_token if auth_response.session else ""
            
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": auth_response.user.email,
                    "full_name": profile_data.get("full_name"),
                    "role": profile_data.get("role")
                },
                "token": token
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

def get_user_from_token(token: str) -> dict:
    """Verifies a JWT/session token and returns user details."""
    if not token:
        return {"success": False, "error": "No token provided."}
        
    if config.IS_MOCK_MODE:
        if not token.startswith("mock-jwt-token-"):
            return {"success": False, "error": "Invalid session token."}
            
        user_id = token.replace("mock-jwt-token-", "")
        conn = sqlite3.connect(MOCK_DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, email, full_name, role FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Session expired or user not found."}
                
            db_id, email, full_name, role = row
            return {
                "success": True,
                "user": {"id": db_id, "email": email, "full_name": full_name, "role": role}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    else:
        try:
            # Query Supabase Auth for user matching this JWT
            user_response = supabase_client.auth.get_user(token)
            if not user_response or not user_response.user:
                return {"success": False, "error": "Invalid credentials or session expired."}
                
            user_id = user_response.user.id
            
            # Fetch profile
            profile_response = supabase_client.table("profiles").select("full_name, role").eq("id", user_id).execute()
            profile_data = profile_response.data[0] if profile_response.data else {"full_name": "", "role": "farmer"}
            
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": user_response.user.email,
                    "full_name": profile_data.get("full_name"),
                    "role": profile_data.get("role")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# --- Storage & Database Scan Operations ---

def upload_produce_image(image_bytes: bytes, filename: str, user_id: str) -> str:
    """
    Uploads the crop scan image to Supabase Storage (bucket: 'produce-scans')
    or saves it locally (mock mode) and returns the public URL.
    """
    clean_filename = f"{user_id}_{int(datetime.datetime.now().timestamp())}_{filename}"
    
    if config.IS_MOCK_MODE:
        # In mock mode, we save the image inside a local "mock_storage" directory served statically
        storage_dir = os.path.join("frontend", "mock_storage")
        os.makedirs(storage_dir, exist_ok=True)
        
        file_path = os.path.join(storage_dir, clean_filename)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
            
        # Return static path relative to the server
        return f"/mock_storage/{clean_filename}"
    else:
        try:
            bucket_name = "produce-scans"
            
            # Upload file
            response = supabase_client.storage.from_(bucket_name).upload(
                path=clean_filename,
                file=image_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Get public url
            public_url = supabase_client.storage.from_(bucket_name).get_public_url(clean_filename)
            return public_url
        except Exception as e:
            print(f"Supabase Storage Upload Error: {e}")
            # If upload fails but database save needs something, return a placeholder or local mock url
            # Or propagate error
            raise e

def save_scan_record(user_id: str, scan_data: dict, image_url: str) -> dict:
    """Saves the scan record in Supabase Database or SQLite."""
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    scan_id = str(uuid.uuid4())
    
    if config.IS_MOCK_MODE:
        conn = sqlite3.connect(MOCK_DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO scans (
                    id, user_id, produce_type, grade, confidence, status, image_url,
                    color_uniformity, defect_score, size_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    user_id,
                    scan_data["produce_type"],
                    scan_data["grade"],
                    scan_data["confidence"],
                    scan_data["status"],
                    image_url,
                    scan_data["metrics"]["color_uniformity"],
                    scan_data["metrics"]["defect_score"],
                    scan_data["metrics"]["size_score"],
                    now_str
                )
            )
            conn.commit()
            
            return {
                "id": scan_id,
                "user_id": user_id,
                "produce_type": scan_data["produce_type"],
                "grade": scan_data["grade"],
                "confidence": scan_data["confidence"],
                "status": scan_data["status"],
                "image_url": image_url,
                "metrics": scan_data["metrics"],
                "created_at": now_str
            }
        except Exception as e:
            print(f"Mock Save Scan Record Error: {e}")
            raise e
        finally:
            conn.close()
    else:
        try:
            db_record = {
                "user_id": user_id,
                "produce_type": scan_data["produce_type"],
                "grade": scan_data["grade"],
                "confidence": scan_data["confidence"],
                "status": scan_data["status"],
                "image_url": image_url,
                "color_uniformity": scan_data["metrics"]["color_uniformity"],
                "defect_score": scan_data["metrics"]["defect_score"],
                "size_score": scan_data["metrics"]["size_score"]
            }
            
            response = supabase_client.table("scans").insert(db_record).execute()
            if response.data:
                record = response.data[0]
                # Format to match standard format
                return {
                    "id": record["id"],
                    "user_id": record["user_id"],
                    "produce_type": record["produce_type"],
                    "grade": record["grade"],
                    "confidence": record["confidence"],
                    "status": record["status"],
                    "image_url": record["image_url"],
                    "metrics": {
                        "color_uniformity": record["color_uniformity"],
                        "defect_score": record["defect_score"],
                        "size_score": record["size_score"]
                    },
                    "created_at": record["created_at"]
                }
            raise Exception("No data returned from database insert.")
        except Exception as e:
            print(f"Supabase Save Scan Record Error: {e}")
            raise e

def get_user_scan_history(user_id: str) -> list:
    """Fetches grading scan history for the specified user."""
    if config.IS_MOCK_MODE:
        conn = sqlite3.connect(MOCK_DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, user_id, produce_type, grade, confidence, status, image_url,
                       color_uniformity, defect_score, size_score, created_at
                FROM scans 
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "user_id": row[1],
                    "produce_type": row[2],
                    "grade": row[3],
                    "confidence": row[4],
                    "status": row[5],
                    "image_url": row[6],
                    "metrics": {
                        "color_uniformity": row[7],
                        "defect_score": row[8],
                        "size_score": row[9]
                    },
                    "created_at": row[10]
                })
            return history
        except Exception as e:
            print(f"Mock Get Scan History Error: {e}")
            return []
        finally:
            conn.close()
    else:
        try:
            response = supabase_client.table("scans")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
                
            history = []
            for record in response.data:
                history.append({
                    "id": record["id"],
                    "user_id": record["user_id"],
                    "produce_type": record["produce_type"],
                    "grade": record["grade"],
                    "confidence": record["confidence"],
                    "status": record["status"],
                    "image_url": record["image_url"],
                    "metrics": {
                        "color_uniformity": record["color_uniformity"],
                        "defect_score": record["defect_score"],
                        "size_score": record["size_score"]
                    },
                    "created_at": record["created_at"]
                })
            return history
        except Exception as e:
            print(f"Supabase Get Scan History Error: {e}")
            return []
