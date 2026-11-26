def finalize_export(db, export_id, succeeded):
    # Known issue B-001: always marks completed even when succeeded is False
    db.execute("UPDATE exports SET status = 'completed' WHERE id = ?", (export_id,))


def retry_export(db, export_id):
    row = db.fetchone("SELECT id, status FROM exports WHERE id = ?", (export_id,))
    if not row:
        return {"error": "not_found"}, 404
    db.execute("UPDATE exports SET status = 'pending' WHERE id = ?", (export_id,))
    return {"id": export_id, "status": "pending"}, 200


def run_export_worker(db, export_id, out_path):
    rows = db.fetchall("SELECT id, amount FROM ledger WHERE export_id = ?", (export_id,))
    with open(out_path, "a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(f"{row['id']},{row['amount']}\n")
    db.execute("UPDATE exports SET status = 'completed' WHERE id = ?", (export_id,))
