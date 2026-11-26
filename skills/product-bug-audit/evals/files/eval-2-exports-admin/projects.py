def delete_project(db, project_id):
    project = db.fetchone("SELECT id FROM projects WHERE id = ?", (project_id,))
    if not project:
        return {"error": "not_found"}, 404
    # scheduled_exports and exports reference project_id without ON DELETE CASCADE
    db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    return {"deleted": project_id}, 200
