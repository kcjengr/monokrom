import sys
from pathlib import Path

import pytest

# Add src to path so we can import monokrom modules
SRC_PATH = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))


@pytest.fixture
def lines_list():
    """Provide a fresh empty list for gcode line accumulation."""
    return []
