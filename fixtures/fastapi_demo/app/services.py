from app.repository import export_records


def export_service():
    return export_records()


def public_service():
    return {"status": "synthetic"}
