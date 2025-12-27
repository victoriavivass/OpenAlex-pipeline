import sys
from pathlib import Path

# Add the /src folder to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openalex_pipeline.utils import decompress_abstract

print("utils import OK")
