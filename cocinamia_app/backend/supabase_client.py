# from supabase import create_client
# import os

# # --- CREDENCIALES ---
# SUPABASE_URL = "https://odeytwqlyqhlactydllu.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kZXl0d3FseXFobGFjdHlkbGx1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4ODE5MDAsImV4cCI6MjA3NTQ1NzkwMH0.XvTKVFb9TU-myLfcqZA8zGDsicZKKRkRUyw87b4l7Zg"

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# backend/supabase_client.py
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # lee .env

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "menu_images")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Define SUPABASE_URL y SUPABASE_KEY en .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- MENU sync ---
def get_menu_remote():
    resp = supabase.table("menu").select("*").execute()
    return resp.data if resp.data else []

def upsert_menu_remote_by_nombre(item):
    # item: dict with nombre, precio, inventario, imagen (imagen is url)
    # We try to find remote by nombre; if exists update, else insert
    nombre = item.get("nombre")
    existing = supabase.table("menu").select("*").eq("nombre", nombre).execute()
    if existing.data and len(existing.data) > 0:
        rid = existing.data[0]["id"]
        supabase.table("menu").update({
            "precio": item.get("precio"),
            "inventario": item.get("inventario"),
            "imagen": item.get("imagen")
        }).eq("id", rid).execute()
    else:
        supabase.table("menu").insert({
            "nombre": item.get("nombre"),
            "precio": item.get("precio"),
            "inventario": item.get("inventario"),
            "imagen": item.get("imagen")
        }).execute()

# --- PEDIDOS sync (only finalizados) ---
def insert_pedido_remote(mesa_id, total, items):
    # pedido: dict with mesa_id, items (list), total, timestamp, finalizado

    timestamp = datetime.now().isoformat(timespec='seconds')
    supabase.table("pedidos").insert({
        "mesa_id": mesa_id,
        "item": items,
        "total": total,
        "timestamp": timestamp,
        "finalizado": False
    }).execute()

def get_pedidos_remote():
    resp = supabase.table("pedidos").select("*").eq("finalizado", False).execute()
    
    print("Remote pedidos:", resp.data)
    
    return resp.data if resp.data else []

# --- Storage: subir imagen a bucket y devolver URL pública ---
def upload_image_to_storage(local_path, dest_filename):
    with open(local_path, "rb") as f:
        data = f.read()
    # put object
    res = supabase.storage.from_(SUPABASE_BUCKET).upload(dest_filename, data)
    # obtener public URL
    public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(dest_filename)
    # public_url is dict {'publicURL': 'https://...'}
    return public_url.get("publicURL") if isinstance(public_url, dict) else public_url

def finalizar_pedido_remoto(pedido_id, estado: bool):
    """Actualiza el estado 'finalizado' de un pedido remoto en Supabase."""
    try:
        supabase.table("pedidos").update({"finalizado": estado}).eq("id", pedido_id).execute()
        return True
    except Exception as e:
        print("Error actualizando finalizado remoto:", e)
        return False

def get_pedidos_remote_all():
    resp = supabase.table("pedidos").select("*").execute()
    
    print("Remote pedidos:", resp.data)
    
    return resp.data if resp.data else []
