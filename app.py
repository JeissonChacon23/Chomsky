"""API y página web (Flask). Vercel detecta `app` en este archivo.

Rutas:
    GET  /              interfaz web
    GET  /api/example   gramática de ejemplo
    POST /api/validate  valida la gramática de entrada
    POST /api/step      ejecuta una etapa sobre la gramática actual
    POST /api/run       ejecuta el proceso completo (modo automático)
El servidor no guarda estado: el navegador conserva la gramática y el historial.
"""
from flask import Flask, Response, jsonify, request

from cfg import Converter, Grammar, build_grammar, check_cnf
from webui import INDEX_HTML

app = Flask(__name__)

EXAMPLE = {
    "variables": "S, A, B",
    "terminals": "a, b",
    "start": "S",
    "productions": "S -> A S B | ε\nA -> a A S | a\nB -> S b S | A | b b",
}


def _body() -> dict:
    return request.get_json(silent=True) or {}


def _grammar_from_dict(data):
    try:
        return Grammar.from_dict(data)
    except (KeyError, TypeError):
        return None


@app.get("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html")


@app.get("/api/example")
def example():
    return jsonify(EXAMPLE)


@app.post("/api/validate")
def validate():
    data = _body()
    grammar, errors = build_grammar(data.get("variables", ""), data.get("terminals", ""),
                                    data.get("start", ""), data.get("productions", ""))
    if errors:
        return jsonify(ok=False, errors=errors)
    return jsonify(ok=True, errors=[], grammar=grammar.to_dict())


@app.post("/api/step")
def step():
    data = _body()
    grammar = _grammar_from_dict(data.get("grammar") or {})
    if grammar is None:
        return jsonify(ok=False, errors=["Error: gramática no válida o no cargada."]), 400
    converter = Converter(grammar)
    try:
        steps = converter.apply(data.get("step", ""))
    except ValueError as exc:
        return jsonify(ok=False, errors=[str(exc)]), 400
    return jsonify(ok=True, steps=[s.to_dict() for s in steps], grammar=converter.current.to_dict(),
                   is_cnf=not check_cnf(converter.current))


@app.post("/api/run")
def run():
    grammar = _grammar_from_dict(_body().get("grammar") or {})
    if grammar is None:
        return jsonify(ok=False, errors=["Error: gramática no válida o no cargada."]), 400
    converter = Converter(grammar)
    steps = converter.run_all()
    return jsonify(ok=True, steps=[s.to_dict() for s in steps], grammar=converter.current.to_dict(),
                   is_cnf=not check_cnf(converter.current))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
