import json
import os
import sys
from pathlib import Path

# Defaults so app imports work in local/dev export context.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "openapi-export-secret-key-with-at-least-32-bytes")

# Ensure project root is importable as top-level package path.
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.auth_service.app.main import app as auth_app  # noqa: E402
from backend.services.discussion_service.app.main import app as discussion_app  # noqa: E402
from backend.services.notification_service.app.main import app as notification_app  # noqa: E402
from backend.services.realtime_service.app.main import app as realtime_app  # noqa: E402


def write_openapi(app, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(app.openapi(), f, indent=2)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "openapi"

    write_openapi(auth_app, out_dir / "auth_service.openapi.json")
    write_openapi(discussion_app, out_dir / "discussion_service.openapi.json")
    write_openapi(notification_app, out_dir / "notification_service.openapi.json")
    write_openapi(realtime_app, out_dir / "realtime_service.openapi.json")

    print(f"OpenAPI specs exported to: {out_dir}")


if __name__ == "__main__":
    main()
