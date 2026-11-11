"""Gastos registrados manualmente (servidores, proxies, etc.) frente al presupuesto mensual.

No consulta ningún proveedor de facturación: refleja lo que el propietario anota."""
import sqlite3
import time
import uuid
from datetime import datetime, timezone

MAX_AMOUNT = 100_000.0


class ExpenseStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS expenses (id TEXT PRIMARY KEY, at REAL NOT NULL, concept TEXT NOT NULL, amount_usd REAL NOT NULL)")

    def add(self, concept: str, amount_usd: float) -> dict:
        concept = concept.strip()
        if not concept or len(concept) > 80 or not 0 < amount_usd <= MAX_AMOUNT:
            raise ValueError("Concepto (1-80 caracteres) o importe (0-100000 USD) inválidos")
        item = {"id": "exp_" + uuid.uuid4().hex[:12], "at": time.time(), "concept": concept, "amount_usd": round(amount_usd, 2)}
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO expenses VALUES (?, ?, ?, ?)", (item["id"], item["at"], item["concept"], item["amount_usd"]))
        return item

    def month(self, budget_usd: float, now: float | None = None) -> dict:
        moment = datetime.fromtimestamp(now or time.time(), timezone.utc)
        start = moment.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT id, at, concept, amount_usd FROM expenses WHERE at>=? ORDER BY at DESC", (start,)).fetchall()
        total = round(sum(r[3] for r in rows), 2)
        return {"month": moment.strftime("%Y-%m"), "budget_usd": budget_usd, "spent_usd": total, "remaining_usd": round(budget_usd - total, 2),
                "over_budget": total > budget_usd, "entries": [dict(zip(("id", "at", "concept", "amount_usd"), r)) for r in rows]}
