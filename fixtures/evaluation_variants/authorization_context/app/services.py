from app.controls import opaque
from app.repository import export_records


def export_service():
    return export_records()


@opaque
def unknown_service():
    return export_records()
