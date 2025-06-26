# STRING-MCP

A comprehensive Python package for interacting with the STRING database API through a Model Context Protocol (MCP) bridge.

## Installation

Install the package in development mode:

```bash
pip install -e .
```

Or install from PyPI (when available):

```bash
pip install string-mcp
```

## Usage

### MCP Server (Primary Use Case)

The package provides an MCP server for integration with MCP-compatible clients:

```bash
# Run the MCP server
string-mcp-server
```

The MCP server provides the following tools:

- **map_identifiers**: Map protein identifiers to STRING IDs
- **get_network_interactions**: Get network interactions data
- **get_functional_enrichment**: Perform functional enrichment analysis
- **get_network_image**: Generate network visualization images
- **get_version_info**: Get STRING database version information

### Command Line Interface

The package also provides a `string-mcp` command for standalone usage:

```bash
# Run demo
string-mcp demo

# Get help
string-mcp --help

# Map protein identifiers
string-mcp map TP53 BRCA1 EGFR --species 9606

# Get network interactions
string-mcp network TP53 BRCA1 --species 9606

# Generate network image
string-mcp image TP53 BRCA1 --output network.png --species 9606
```

### Python API

```python
from stringmcp.main import StringDBBridge

# Initialize the bridge
bridge = StringDBBridge()

# Map protein identifiers
proteins = ["TP53", "BRCA1", "EGFR"]
mapped = bridge.map_identifiers(proteins, species=9606)  # 9606 = human

# Get network interactions
interactions = bridge.get_network_interactions(proteins, species=9606)

# Perform functional enrichment
enrichment = bridge.get_functional_enrichment(proteins, species=9606)
```

## Features

- **Protein Identifier Mapping**: Convert various protein identifiers to STRING IDs
- **Network Analysis**: Retrieve protein-protein interaction networks
- **Functional Enrichment**: Perform gene ontology and pathway enrichment analysis
- **Network Visualization**: Generate network images in various formats
- **Interaction Partners**: Find all interaction partners for proteins
- **Functional Annotations**: Get detailed functional annotations
- **Protein Similarity**: Calculate similarity scores between proteins
- **PPI Enrichment**: Test for protein-protein interaction enrichment
- **MCP Integration**: Full Model Context Protocol server implementation

## API Methods

### Core Methods

- `map_identifiers()`: Map protein identifiers to STRING IDs
- `get_network_interactions()`: Get network interaction data
- `get_network_image()`: Generate network visualization images
- `get_interaction_partners()`: Find all interaction partners
- `get_functional_enrichment()`: Perform enrichment analysis
- `get_functional_annotation()`: Get functional annotations
- `get_protein_similarity()`: Calculate similarity scores
- `get_ppi_enrichment()`: Test for PPI enrichment
- `get_version_info()`: Get STRING database version

### Configuration

The package uses a `StringConfig` class for configuration:

```python
from stringmcp.main import StringConfig, StringDBBridge

config = StringConfig(
    base_url="https://string-db.org/api",
    version_url="https://version-12-0.string-db.org/api",
    caller_identity="my_app",
    request_delay=1.0  # Delay between requests in seconds
)

bridge = StringDBBridge(config)
```

## Output Formats

The package supports multiple output formats:

- `JSON`: Structured data (default)
- `TSV`: Tab-separated values
- `XML`: XML format
- `IMAGE`: Network visualization images
- `SVG`: Scalable vector graphics
- `PSI_MI`: PSI-MI format

## Species Support

The package supports all species available in STRING. Common species IDs:

- Human: 9606
- Mouse: 10090
- Rat: 10116
- Yeast: 4932
- E. coli: 511145

## MCP Server Configuration

To use the MCP server with an MCP client, configure it as follows:

```json
{
  "mcpServers": {
    "string-mcp": {
      "command": "string-mcp-server",
      "env": {}
    }
  }
}
```

The server will automatically handle:
- JSON-RPC communication
- Tool discovery and invocation
- Error handling and reporting
- Base64 encoding for image data

## Development

### Setup Development Environment

```bash
# Install in development mode with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black stringmcp/

# Type checking
mypy stringmcp/
```

### Project Structure

```
STRINGmcp/
├── pyproject.toml      # Package configuration
├── README.md          # This file
├── LICENSE            # MIT License
├── stringmcp/         # Main package
│   ├── __init__.py    # Package initialization
│   ├── main.py        # Core STRING API bridge
│   ├── cli.py         # Command-line interface
│   └── mcp_server.py  # MCP server implementation
└── tests/             # Test files
    ├── __init__.py
    ├── test_main.py   # Tests for main functionality
    └── test_mcp_server.py  # Tests for MCP server
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker. 