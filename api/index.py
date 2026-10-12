from datetime import datetime
from threading import Lock

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
lock = Lock()
waiting = []
desks = {i: {"id": i, "status": "available", "current_ticket": None, "updated_at": None} for i in range(1, 5)}
sequence = 0
served = 0


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def board():
    current = next((d["current_ticket"] for d in desks.values() if d["current_ticket"]), None)
    return {"waiting": list(waiting), "desks": list(desks.values()), "current": current,
            "stats": {"waiting": len(waiting), "served": served,
                      "available": sum(d["status"] == "available" for d in desks.values()),
                      "busy": sum(d["status"] == "busy" for d in desks.values())}}


@app.get("/api/board")
def get_board():
    with lock:
        return jsonify(board())


@app.post("/api/tickets")
def create_ticket():
    global sequence
    data = request.get_json(silent=True) or {}
    with lock:
        sequence += 1
        ticket = {"id": sequence, "code": f"A{sequence:02d}",
                  "patient": (data.get("patient") or "Paciente").strip()[:100] or "Paciente",
                  "service": (data.get("service") or "Análisis de laboratorio")[:80], "created_at": now()}
        waiting.append(ticket)
        return jsonify(ticket), 201


@app.post("/api/desks/<int:desk_id>")
def update_desk(desk_id):
    global served
    if desk_id not in desks:
        return jsonify(error="La ventanilla no existe."), 404
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in ("available", "busy"):
        return jsonify(error="Estado de ventanilla inválido."), 400
    with lock:
        desk = desks[desk_id]
        if status == "available" and desk["status"] == "busy":
            desk["current_ticket"] = None
            served += 1
            desk["status"] = "available"
            desk["updated_at"] = now()
            call_next_locked(desk)
        elif status == "busy" and desk["status"] == "available":
            desk["status"] = "busy"
            desk["updated_at"] = now()
        return jsonify(board())


def call_next_locked(desk):
    if waiting:
        desk["current_ticket"] = waiting.pop(0)
        # Calling a patient does not occupy the desk until staff press Ocupar.
        desk["status"] = "available"
        desk["updated_at"] = now()


@app.post("/api/call-next")
def call_next():
    with lock:
        desk = next((d for d in desks.values() if d["status"] == "available" and not d["current_ticket"]), None)
        if not waiting:
            return jsonify(error="No hay turnos en espera."), 409
        if not desk:
            return jsonify(error="Todas las ventanillas están ocupadas."), 409
        call_next_locked(desk)
        return jsonify(board())


@app.get("/api/<path:path>")
@app.post("/api/<path:path>")
def not_found(path):
    return jsonify(error="Ruta de API no encontrada."), 404
