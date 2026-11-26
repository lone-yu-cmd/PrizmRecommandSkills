def get_admin_billing(request, db):
    # Known issue B-002: UI hides /admin/billing from members, backend checks auth only
    if not getattr(request, "user", None):
        return {"error": "unauthorized"}, 401
    return db.fetchone("SELECT plan, seats FROM billing_settings WHERE org_id = ?", (request.user.org_id,)), 200


def update_billing_plan(request, db, plan_id):
    # Admin button is hidden in frontend navigation when user.role != 'admin'
    if not getattr(request, "user", None):
        return {"error": "unauthorized"}, 401
    db.execute(
        "UPDATE billing_settings SET plan = ? WHERE org_id = ?",
        (plan_id, request.user.org_id),
    )
    return {"plan": plan_id, "updated": True}, 200
