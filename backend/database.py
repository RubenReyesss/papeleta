import json
import aiosqlite
from datetime import datetime, timezone
from pathlib import Path

from config import Settings


async def init_db(settings: Settings) -> None:
    """
    Crea las tablas si no existen.
    Se llama una vez al arrancar la aplicacion.
    """
    # Asegurarse de que el directorio padre existe
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  TEXT    NOT NULL,
                filename    TEXT,
                doc_type    TEXT,
                confianza   TEXT,
                resumen     TEXT,
                pasos       TEXT,   -- JSON array
                fechas      TEXT    -- JSON array
            )
        """)
        await db.commit()


async def save_analysis(settings: Settings, filename: str, result: dict) -> int:
    """
    Guarda un resultado de analisis en el historial.
    Devuelve el ID del registro creado.
    """
    async with aiosqlite.connect(settings.db_path) as db:
        cursor = await db.execute(
            """
            INSERT INTO analyses (created_at, filename, doc_type, confianza, resumen, pasos, fechas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                filename,
                result.get("tipo"),
                result.get("confianza"),
                result.get("resumen"),
                json.dumps(result.get("pasos", []), ensure_ascii=False),
                json.dumps(result.get("fechas", []), ensure_ascii=False),
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_history(settings: Settings, limit: int = 20) -> list[dict]:
    """
    Devuelve los ultimos analisis realizados, del mas reciente al mas antiguo.
    """
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()

    return [
        {
            **dict(row),
            "pasos": json.loads(row["pasos"] or "[]"),
            "fechas": json.loads(row["fechas"] or "[]"),
        }
        for row in rows
    ]
