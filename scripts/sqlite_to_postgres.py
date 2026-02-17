import os
from pathlib import Path
from sqlalchemy import create_engine, text, inspect

def normalize_pg_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

# ---- Source SQLite (old DB)
SQLITE_PATH = os.environ.get("SQLITE_OLD_PATH", r"D:\intelligence_systems_site\instance\site_old.db")
sqlite_path = Path(SQLITE_PATH)
if not sqlite_path.exists():
    raise FileNotFoundError(f"SQLite file not found: {sqlite_path}")

sqlite_url = "sqlite:///" + sqlite_path.resolve().as_posix()

# ---- Target Postgres (Render)
pg_url = os.environ.get("DATABASE_URL")
if not pg_url:
    raise RuntimeError("DATABASE_URL env var is not set")
pg_url = normalize_pg_url(pg_url)

sqlite_engine = create_engine(sqlite_url)
pg_engine = create_engine(pg_url)

def coerce_rows_for_postgres(table_name: str, rows: list[dict]) -> list[dict]:
    """
    Convert SQLite-style values to match Postgres column types:
    - booleans 0/1 -> True/False
    - fill missing created_at/updated_at if Postgres columns are NOT NULL
    """
    insp = inspect(pg_engine)
    cols = insp.get_columns(table_name)

    bool_cols = set()
    notnull_cols = set()
    for c in cols:
        t = str(c["type"]).lower()
        if "bool" in t:
            bool_cols.add(c["name"])
        if not c.get("nullable", True):
            notnull_cols.add(c["name"])

    # If Postgres expects these NOT NULL, we will fill when missing
    needs_created = "created_at" in notnull_cols
    needs_updated = "updated_at" in notnull_cols

    fixed = []
    for r in rows:
        rr = dict(r)

        # Boolean coercion
        for k in bool_cols:
            if k in rr:
                v = rr[k]
                if v in (1, "1", True):
                    rr[k] = True
                elif v in (0, "0", False):
                    rr[k] = False

        # Timestamp backfill
        # If created_at/updated_at are NULL in SQLite, fill with CURRENT_TIMESTAMP string
        # (Postgres accepts this format)
        if needs_created and rr.get("created_at") in (None, ""):
            rr["created_at"] = "2000-01-01 00:00:00"  # safe default
        if needs_updated and rr.get("updated_at") in (None, ""):
            rr["updated_at"] = rr.get("created_at") or "2000-01-01 00:00:00"

        fixed.append(rr)

    return fixed


def copy_table(table_name: str):
    with sqlite_engine.connect() as sconn, pg_engine.connect() as pconn:
        # Fetch from SQLite
        rows = sconn.execute(text(f"SELECT * FROM {table_name}")).mappings().all()
        if not rows:
            print(f"{table_name}: no rows")
            return

        rows = [dict(r) for r in rows]
        rows = coerce_rows_for_postgres(table_name, rows)

        # Clear target table to avoid duplicates
        pconn.execute(text(f'DELETE FROM "{table_name}"'))
        pconn.commit()

        cols = list(rows[0].keys())
        col_list = ", ".join([f'"{c}"' for c in cols])
        val_list = ", ".join([f":{c}" for c in cols])

        pconn.execute(
            text(f'INSERT INTO "{table_name}" ({col_list}) VALUES ({val_list})'),
            rows
        )
        pconn.commit()
        print(f"{table_name}: copied {len(rows)} rows")

def reset_sequence(table_name: str, id_col: str = "id"):
    # Reset Postgres sequence so future inserts work
    with pg_engine.connect() as conn:
        try:
            conn.execute(text(f"""
                SELECT setval(
                  pg_get_serial_sequence('"{table_name}"','{id_col}'),
                  COALESCE(MAX("{id_col}"), 1)
                )
                FROM "{table_name}";
            """))
            conn.commit()
            print(f"{table_name}: sequence reset")
        except Exception:
            # ignore if table doesn't have serial id
            pass

def main():
    tables = [
        "site_settings",
        "user",
        "program",
        "faculty",
        "gallery_album",
        "gallery_image",
        "news",
        "event",
        "page",
        "achievement",
        "alumni",
        "enquiry",
        "funded_project",
        "mo_u",
        "newsletter",
        "placement_stat",
        "hero_slides",
    ]

    # Don't copy these (leftovers / internal)
    skip = {"_alembic_tmp_hero_slides", "sqlite_sequence", "alembic_version"}
    tables = [t for t in tables if t not in skip]

    for t in tables:
        try:
            copy_table(t)
        except Exception as e:
            print(f"{t}: FAILED -> {e}")

    # Reset sequences where applicable
    for t in tables:
        reset_sequence(t)

if __name__ == "__main__":
    main()
