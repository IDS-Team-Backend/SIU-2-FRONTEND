import json
from pathlib import Path

# Los .json viven en frontend/mocks (este módulo está en frontend/services).
MOCKS_DIR = Path(__file__).resolve().parent.parent / "mocks"


def _load_mock(filename):
    with open(MOCKS_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


cursos_mock = {int(k): v for k, v in _load_mock("cursos.json").items()}
listar_materiales = _load_mock("materiales.json")

listar_materias = [
    {"id": c["id"], "codigo": c["codigo"], "nombre": c["nombre"]}
    for c in cursos_mock.values()
]
