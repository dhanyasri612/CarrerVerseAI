"""Refresh the allowlisted official teaching resources without processing resumes."""

import json
import sys

from app.ai.rag.technical_sources import build_resource_specs, refresh_technical_sources
from app.services.teaching_resource_service import AUTHORITATIVE_RESOURCE_BANK


def main() -> int:
    specs = build_resource_specs(AUTHORITATIVE_RESOURCE_BANK)
    result = refresh_technical_sources(specs)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
