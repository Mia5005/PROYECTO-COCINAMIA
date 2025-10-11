# ``import sqlite3
# import os
# import json
# from flask import Flask, render_template, request, jsonify
# from datetime import datetime

# app = Flask(__name__)

# # Ruta al archivo de la base de datos
# DB_PATH = "cocinamia.db"

# # Función para conectarse a la base de datos
# def get_db_connection():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
#     return conn

# # ---------------- CONFIGURACIÓN ----------------
# MENU_FILE = "data/menu.json"
# PEDIDOS_FILE = "data/pedidos.json"
# HISTORIAL_FILE = "data/historial.json"

# # Asegurar existencia de archivos
# for fpath, default in [
#     (PEDIDOS_FILE, []),
#     (HISTORIAL_FILE, []),
# ]:
#     if not os.path.exists(fpath):
#         with open(fpath, "w", encoding="utf-8") as f:
#             json.dump(default, f, ensure_ascii=False, indent=2)


# # ---------------- RUTAS ----------------
# @app.route("/")
# def index():
#     """Página principal del menú interactivo"""
#     with open(MENU_FILE, "r", encoding="utf-8") as f:
#         menu = json.load(f)
#     return render_template("index.html", menu=menu)


# @app.route("/pedido", methods=["POST"])
# def pedido():
#     """Guardar un pedido desde el cliente"""
#     data = request.get_json()
#     mesa_id = data.get("mesa_id", "SinMesa")
#     items = data.get("items", [])

#     if not items:
#         return jsonify({"status": "error", "message": "No se enviaron platos."}), 400

#     pedido = {
#         "mesa_id": mesa_id,
#         "items": items,
#         "total": sum(i["precio"] * i["cantidad"] for i in items),
#         "timestamp": datetime.now().isoformat(timespec="seconds")
#     }

#     # Guardar pedido nuevo
#     with open(PEDIDOS_FILE, "r+", encoding="utf-8") as f:
#         pedidos = json.load(f)
#         pedidos.append(pedido)
#         f.seek(0)
#         json.dump(pedidos, f, ensure_ascii=False, indent=2)
#         f.truncate()

#     # Actualizar inventario del menú
#     with open(MENU_FILE, "r+", encoding="utf-8") as f:
#         menu = json.load(f)
#         for item in items:
#             for plato in menu:
#                 if str(plato["id"]) == str(item["id"]):
#                     plato["inventario"] = max(0, plato["inventario"] - item["cantidad"])
#         f.seek(0)
#         json.dump(menu, f, ensure_ascii=False, indent=2)
#         f.truncate()

#     return jsonify({"status": "ok", "message": "Pedido guardado correctamente."})


# @app.route("/cocina")
# def cocina():
#     """Vista para el personal de cocina"""
#     with open(PEDIDOS_FILE, "r", encoding="utf-8") as f:
#         pedidos = json.load(f)
#     return render_template("cocina.html", pedidos=pedidos)


# @app.route("/cocina/finalizar/<int:pedido_index>", methods=["POST"])
# def finalizar_pedido(pedido_index):
#     """Mueve un pedido al historial y lo elimina de pendientes"""
#     with open(PEDIDOS_FILE, "r+", encoding="utf-8") as f:
#         pedidos = json.load(f)

#         if 0 <= pedido_index < len(pedidos):
#             finalizado = pedidos.pop(pedido_index)
#             finalizado["finalizado"] = datetime.now().isoformat(timespec="seconds")

#             # Guardar en historial
#             with open(HISTORIAL_FILE, "r+", encoding="utf-8") as h:
#                 historial = json.load(h)
#                 historial.append(finalizado)
#                 h.seek(0)
#                 json.dump(historial, h, ensure_ascii=False, indent=2)
#                 h.truncate()

#             # Actualizar archivo de pedidos
#             f.seek(0)
#             json.dump(pedidos, f, ensure_ascii=False, indent=2)
#             f.truncate()

#             return jsonify({"status": "ok", "message": f"Pedido de {finalizado['mesa_id']} finalizado y guardado en historial."})
#         else:
#             return jsonify({"status": "error", "message": "Índice de pedido inválido."}), 400


# @app.route("/historial")
# def historial():
#     """Ver el historial de pedidos finalizados"""
#     with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
#         historial = json.load(f)
#     return render_template("historial.html", historial=historial)

# @app.route("/finalizar_dia", methods=["POST"])
# def finalizar_dia():
#     try:
#         conn = get_db_connection()
#         conn.execute("DELETE FROM pedidos WHERE finalizado = 1")
#         conn.execute("DELETE FROM pedido_items WHERE pedido_id NOT IN (SELECT id FROM pedidos)")
#         conn.commit()
#         conn.close()
#         return jsonify({"status": "ok", "message": "Historial borrado correctamente."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})


# @app.route("/admin")
# def admin():
#     """Panel para gestionar menú, pedidos e historial"""
#     with open(MENU_FILE, "r", encoding="utf-8") as f:
#         menu = json.load(f)
#     with open(PEDIDOS_FILE, "r", encoding="utf-8") as f:
#         pedidos = json.load(f)
#     with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
#         historial = json.load(f)
#     return render_template("admin.html", menu=menu, pedidos=pedidos, historial=historial)

# @app.route("/admin/eliminar_pedido/<int:index>", methods=["DELETE"])
# def eliminar_pedido(index):
#     """Eliminar un pedido activo desde admin"""
#     with open(PEDIDOS_FILE, "r+", encoding="utf-8") as f:
#         pedidos = json.load(f)
#         if 0 <= index < len(pedidos):
#             eliminado = pedidos.pop(index)
#             f.seek(0)
#             json.dump(pedidos, f, ensure_ascii=False, indent=2)
#             f.truncate()
#             return jsonify({"status": "ok", "message": f"Pedido de mesa {eliminado['mesa_id']} eliminado."})
#         return jsonify({"status": "error", "message": "Índice inválido"}), 400

# @app.route("/admin/eliminar_historial/<int:index>", methods=["DELETE"])
# def eliminar_historial(index):
#     """Eliminar un pedido del historial"""
#     with open(HISTORIAL_FILE, "r+", encoding="utf-8") as f:
#         historial = json.load(f)
#         if 0 <= index < len(historial):
#             eliminado = historial.pop(index)
#             f.seek(0)
#             json.dump(historial, f, ensure_ascii=False, indent=2)
#             f.truncate()
#             return jsonify({"status": "ok", "message": f"Pedido de mesa {eliminado['mesa_id']} eliminado del historial."})
#         return jsonify({"status": "error", "message": "Índice inválido"}), 400

# ##### ----- ----- ------ -------- --------

# from werkzeug.utils import secure_filename

# # Carpeta donde se guardarán las imágenes
# UPLOAD_FOLDER = os.path.join("static", "images")
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# @app.route("/admin/subir_imagen/<int:plato_id>", methods=["POST"])
# def subir_imagen(plato_id):
#     """Permite subir o actualizar la imagen de un plato"""
#     if "imagen" not in request.files:
#         return jsonify({"status": "error", "message": "No se envió ninguna imagen."}), 400

#     imagen = request.files["imagen"]
#     if imagen.filename == "":
#         return jsonify({"status": "error", "message": "Archivo vacío."}), 400

#     # Guardar la imagen en la carpeta static/images
#     filename = secure_filename(imagen.filename)
#     save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     imagen.save(save_path)

#     # Actualizar el campo 'imagen' en la base de datos o menú JSON
#     with open(MENU_FILE, "r+", encoding="utf-8") as f:
#         menu = json.load(f)
#         for plato in menu:
#             if int(plato["id"]) == plato_id:
#                 plato["imagen"] = f"/static/images/{filename}"
#         f.seek(0)
#         json.dump(menu, f, ensure_ascii=False, indent=2)
#         f.truncate()

#     return jsonify({"status": "ok", "message": "Imagen actualizada correctamente."})


# # ---------------- EJECUCIÓN ----------------
# if __name__ == "__main__":
#     app.run(debug=True)

























# ## ------------ EJECUCIÓN DEL SUPABASE -------------
# from flask import Flask, render_template, request, jsonify
# from datetime import datetime
# from supabase_client import supabase

# app = Flask(__name__)

# # --- MENÚ ---
# @app.route("/")
# def index():
#     """Página principal: mostrar menú desde Supabase"""
#     response = supabase.table("menu").select("*").execute()
#     menu = response.data
#     return render_template("index.html", menu=menu)

# # --- PEDIDOS ---
# @app.route("/pedido", methods=["POST"])
# def pedido():
#     """Guardar un pedido nuevo en Supabase"""
#     data = request.get_json()
#     mesa_id = data.get("mesa_id", "SinMesa")
#     items = data.get("items", [])

#     if not items:
#         return jsonify({"status": "error", "message": "No se enviaron platos."}), 400

#     total = sum(i["precio"] * i["cantidad"] for i in items)

#     supabase.table("pedidos").insert({
#         "mesa_id": mesa_id,
#         "total": total,
#         "items": items,
#         "timestamp": datetime.now().isoformat()
#     }).execute()

#     # Actualiza inventario
#     for item in items:
#         supabase.table("menu").update({
#             "inventario": f"greatest(inventario - {item['cantidad']}, 0)"
#         }).eq("id", item["id"]).execute()

#     return jsonify({"status": "ok", "message": "Pedido guardado correctamente."})

# # --- PANEL COCINA ---
# @app.route("/cocina")
# def cocina():
#     pedidos = supabase.table("pedidos").select("*").execute().data
#     return render_template("cocina.html", pedidos=pedidos)

# @app.route("/cocina/finalizar/<int:pedido_id>", methods=["POST"])
# def finalizar_pedido(pedido_id):
#     pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute().data
#     if not pedido:
#         return jsonify({"status": "error", "message": "Pedido no encontrado."}), 404

#     pedido = pedido[0]
#     pedido["finalizado"] = datetime.now().isoformat()

#     supabase.table("historial").insert(pedido).execute()
#     supabase.table("pedidos").delete().eq("id", pedido_id).execute()

#     return jsonify({"status": "ok", "message": f"Pedido {pedido_id} finalizado."})

# # --- HISTORIAL ---
# @app.route("/historial")
# def historial():
#     historial = supabase.table("historial").select("*").execute().data
#     return render_template("historial.html", historial=historial)












# app.py
import os
from flask import Flask, render_template, request, jsonify
from backend.database import (
    init_db, get_menu_local, upsert_menu_local, insert_menu_local,
    get_pedidos_local, insert_pedido_local, finalizar_pedido_local,
    get_historial_local, clear_historial_local, update_menu_by_id_local, get_menu_local as menu_local_all
)
from backend.supabase_client import (
    get_menu_remote, upsert_menu_remote_by_nombre, insert_pedido_remote,
    upload_image_to_storage, get_pedidos_remote, finalizar_pedido_remoto, get_pedidos_remote_all
)
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
init_db()

# Al iniciar, sincronizamos remote -> local (solo menú)
def sync_supabase_to_local_menu():
    remote = get_menu_remote()
    for r in remote:
        # r expected keys: nombre, precio, inventario, imagen
        upsert_menu_local(r.get("nombre"), float(r.get("precio", 0)), int(r.get("inventario", 0)), r.get("imagen"))

# each time app restarts pull remote menu to local
try:
    sync_supabase_to_local_menu()
except Exception as e:
    print("Warning: no se pudo sincronizar menu remoto -> local:", e)

# ------------------ RUTAS ------------------

@app.route("/")
def index():
    menu = menu_local_all()
    print("Menu loaded:", menu)
    return render_template("index.html", menu=menu)

# @app.route("/pedido", methods=["POST"])
# def crear_pedido():
#     data = request.get_json()
#     mesa_id = data.get("mesa_id", "SinMesa")
#     items = data.get("items", [])
#     if not items:
#         return jsonify({"status":"error","message":"No hay items"}), 400
#     total = sum(i["precio"] * i["cantidad"] for i in items)
#     pid = insert_pedido_local(mesa_id, items, total)
#     return jsonify({"status":"ok", "message":"Pedido guardado localmente", "pedido_id": pid})

@app.route("/pedido", methods=["POST"])
def crear_pedido():
    try:
        data = request.get_json()
        # print("Datos recibidos para nuevo pedido:", data)
        if not data:
            return jsonify({"status": "error", "message": "No se envió JSON válido"}), 400

        mesa_id = data.get("mesa_id", "SinMesa")
        items = data.get("items", [])
        print("Procesando pedido para mesa:", mesa_id, "con items:", items)

        if not items:
            return jsonify({"status": "error", "message": "No hay items"}), 400

        #total = sum(i["precio"] * i["cantidad"] print(i) for i in items)
        total = sum( i["cantidad"] for i in items)

        print(total)
        pid = insert_pedido_remote(mesa_id, total, items)

        return jsonify({
            "status": "ok",
            "message": f"Pedido guardado correctamente (ID {pid})",
            "pedido_id": pid
        }), 200

    except Exception as e:
        print("Error al crear pedido:", e)
        return jsonify({
            "status": "error",
            "message": f"Error interno del servidor: {str(e)}"
        }), 500


@app.route("/cocina")
def cocina():    
    pedidos = get_pedidos_remote()
    for p in pedidos:
        if isinstance(p["item"], str):
            try:
                p["item"] = json.loads(p["item"])
            except:
                p["item"] = []

    return render_template("cocina.html", pedidos=pedidos)
    return render_template("cocina.html", pedidos=pedidos)

@app.route("/cocina/finalizar/<int:pedido_id>", methods=["POST"])
def finalizar_pedido(pedido_id):


    try:
        # 1️⃣ Marca como finalizado en SQLite

        # 2️⃣ Marca como finalizado en Supabase
        finalizar_pedido_remoto(pedido_id, True)

        return jsonify({"status": "ok", "message": f"Pedido {pedido_id} finalizado correctamente en local y remoto."})

    except Exception as e:
        print("Error finalizando pedido:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/historial")
def historial():
    historial = get_pedidos_remote_all()
    return render_template("historial.html", historial=historial)

@app.route("/finalizar_dia", methods=["POST"])
def finalizar_dia():
    # sincronizar finalizados y luego limpiar
    finalizados = get_pedidos_local(finalizado=1)
    for f in finalizados:
        try:
            insert_pedido_remote({
                "mesa_id": f["mesa_id"],
                "items": f["items"],
                "total": f["total"],
                "timestamp": f["timestamp"],
                "finalizado": True
            })
        except Exception as e:
            print("Warning: no se pudo enviar a supabase:", e)
    clear_historial_local()
    return jsonify({"status":"ok","message":"Día finalizado, finalizados sincronizados y historial local borrado."})

# ---------------- ADMIN ----------------

@app.route("/admin")
def admin():
    menu = get_menu_local()
    pedidos = get_pedidos_local(finalizado=0)
    historial = get_historial_local()
    return render_template("admin.html", menu=menu, pedidos=pedidos, historial=historial)

@app.route("/admin/actualizar", methods=["POST"])
def admin_actualizar():
    data = request.get_json()
    # data must contain id, nombre, precio, inventario
    update_menu_by_id_local(data["id"], data["nombre"], data["precio"], data["inventario"], data.get("imagen"))
    # sync this menu item to supabase
    try:
        # build object based on latest local
        item = None
        for m in get_menu_local():
            if m["id"] == data["id"]:
                item = m
                break
        if item:
            upsert_menu_remote_by_nombre(item)
    except Exception as e:
        print("Warning: no se pudo sincronizar menu -> supabase:", e)
    return jsonify({"status":"ok","message":"Plato actualizado localmente y sincronizado."})

@app.route("/admin/subir_imagen/<int:menu_id>", methods=["POST"])
def admin_subir_imagen(menu_id):
    # recibe archivo en form-data con campo 'imagen'
    file = request.files.get("imagen")
    if not file:
        return jsonify({"status":"error","message":"No file sent"}), 400
    # guardar temporalmente
    filename = file.filename
    tmp_path = os.path.join("static", "images")
    os.makedirs(tmp_path, exist_ok=True)
    local_path = os.path.join(tmp_path, filename)
    file.save(local_path)

    # subir a supabase storage y obtener url
    try:
        public_url = upload_image_to_storage(local_path, f"menu/{filename}")
    except Exception as e:
        return jsonify({"status":"error","message":f"Error subiendo a supabase: {e}"}), 500

    # actualizar registro local menu con la URL
    # get item by id
    conn = None
    from backend.database import get_conn
    # update local
    update_menu_by_id_local(menu_id, *[
        # get current values then replace imagen
        *(lambda m: (m["nombre"], m["precio"], m["inventario"], public_url))(next(m for m in get_menu_local() if m["id"] == menu_id))
    ])
    # sync up to supabase (by nombre)
    try:
        item = next(m for m in get_menu_local() if m["id"] == menu_id)
        upsert_menu_remote_by_nombre(item)
    except Exception as e:
        print("Warning: no se pudo sincronizar la imagen a supabase:", e)

    return jsonify({"status":"ok","message":"Imagen subida y sincronizada.", "url": public_url})

# endpoint to trigger full two-way sync (optional)
@app.route("/admin/sync", methods=["POST"])
def admin_sync():
    # push local menu to supabase
    menu = get_menu_local()
    for m in menu:
        try:
            upsert_menu_remote_by_nombre(m)
        except Exception as e:
            print("Warning:", e)
    # pull remote menu to local (in case remote has changes)
    try:
        sync_supabase_to_local_menu()
    except Exception as e:
        print("Warning:", e)
    return jsonify({"status":"ok","message":"Sincronización ejecutada."})

if __name__ == "__main__":
    app.run(debug=True)
