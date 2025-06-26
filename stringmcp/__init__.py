"""
STRING-DB API MCP Bridge
A comprehensive interface for interacting with the STRING database API
"""

__version__ = "0.1.0"
__author__ = "MCPmed Contributors"
__email__ = "matthias.flotho@ccb.uni-saarland.de"

from .main import StringDBBridge, StringConfig, OutputFormat

__all__ = [
    "StringDBBridge",
    "StringConfig", 
    "OutputFormat",
    "__version__",
] 