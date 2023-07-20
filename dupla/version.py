from pathlib import Path

from packaging.version import parse

__all__ = ["__version__"]

with Path(__file__).with_name("_version.txt").open("r") as file:
    version_obj = parse(file.readline().strip())

# string representation of the version
__version__ = str(version_obj)
