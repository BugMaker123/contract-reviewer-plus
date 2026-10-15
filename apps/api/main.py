import sys
from pathlib import Path

# Add src to sys.path
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import uvicorn
from contract_app.bootstrap.app_factory import app
from contract_app.bootstrap.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "contract_app.bootstrap.app_factory:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
