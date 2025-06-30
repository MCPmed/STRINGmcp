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

# Format code
black stringmcp/

# Type checking
mypy stringmcp/

# Lint code
flake8 stringmcp/
```

**Note**: Test files are not currently included in this repository. To add tests, create a `tests/` directory and add test files following the pytest configuration in `pyproject.toml`.

### Project Structure

```
STRINGmcp/
├── pyproject.toml          # Package configuration and dependencies
├── README.md              # This file
├── LICENSE                # MIT License
├── .gitignore             # Git ignore patterns
├── stringmcp/             # Main package
│   ├── __init__.py        # Package initialization
│   └── main.py            # Core STRING API bridge and MCP server
└── string_mcp.egg-info/   # Package metadata (generated during install)
    ├── PKG-INFO           # Package information
    ├── SOURCES.txt        # Source files list
    ├── dependency_links.txt
    ├── entry_points.txt   # CLI entry points
    ├── requires.txt       # Dependencies
    └── top_level.txt      # Top-level package names
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

## Example Usage

### Complete DNA Repair Protein Analysis

This example demonstrates the comprehensive functionality of the STRING-DB MCP bridge by analyzing a set of well-known human DNA repair proteins: TP53, BRCA1, BRCA2, ATM, and ATR.




#### 2. Protein Identifier Mapping

Map gene symbols to STRING identifiers:

```json
[
  {
    "queryIndex": 0,
    "queryItem": "TP53",
    "stringId": "9606.ENSP00000269305",
    "ncbiTaxonId": 9606,
    "taxonName": "Homo sapiens",
    "preferredName": "TP53",
    "annotation": "Cellular tumor antigen p53; Acts as a tumor suppressor in many tumor types; induces growth arrest or apoptosis depending on the physiological circumstances and cell type..."
  },
  {
    "queryIndex": 1,
    "queryItem": "BRCA1",
    "stringId": "9606.ENSP00000418960",
    "ncbiTaxonId": 9606,
    "taxonName": "Homo sapiens",
    "preferredName": "BRCA1",
    "annotation": "Breast cancer type 1 susceptibility protein; E3 ubiquitin-protein ligase that specifically mediates the formation of 'Lys-6'-linked polyubiquitin chains..."
  },
  {
    "queryIndex": 2,
    "queryItem": "BRCA2",
    "stringId": "9606.ENSP00000369497",
    "ncbiTaxonId": 9606,
    "taxonName": "Homo sapiens",
    "preferredName": "BRCA2",
    "annotation": "Breast cancer type 2 susceptibility protein; Involved in double-strand break repair and/or homologous recombination..."
  },
  {
    "queryIndex": 3,
    "queryItem": "ATM",
    "stringId": "9606.ENSP00000278616",
    "ncbiTaxonId": 9606,
    "taxonName": "Homo sapiens",
    "preferredName": "ATM",
    "annotation": "Serine-protein kinase ATM; Serine/threonine protein kinase which activates checkpoint signaling upon double strand breaks..."
  },
  {
    "queryIndex": 4,
    "queryItem": "ATR",
    "stringId": "9606.ENSP00000343741",
    "ncbiTaxonId": 9606,
    "taxonName": "Homo sapiens",
    "preferredName": "ATR",
    "annotation": "Serine/threonine-protein kinase ATR; Serine/threonine protein kinase which activates checkpoint signaling upon genotoxic stresses..."
  }
]
```

#### 3. Protein-Protein Interaction Network

Examine network interactions between these proteins:

```json
[
  {
    "stringId_A": "9606.ENSP00000269305",
    "stringId_B": "9606.ENSP00000369497",
    "preferredName_A": "TP53",
    "preferredName_B": "BRCA2",
    "score": 0.995
  },
  {
    "stringId_A": "9606.ENSP00000269305",
    "stringId_B": "9606.ENSP00000343741",
    "preferredName_A": "TP53",
    "preferredName_B": "ATR",
    "score": 0.996
  },
  {
    "stringId_A": "9606.ENSP00000269305",
    "stringId_B": "9606.ENSP00000278616",
    "preferredName_A": "TP53",
    "preferredName_B": "ATM",
    "score": 0.999
  },
  {
    "stringId_A": "9606.ENSP00000269305",
    "stringId_B": "9606.ENSP00000418960",
    "preferredName_A": "TP53",
    "preferredName_B": "BRCA1",
    "score": 0.999
  },
  {
    "stringId_A": "9606.ENSP00000278616",
    "stringId_B": "9606.ENSP00000369497",
    "preferredName_A": "ATM",
    "preferredName_B": "BRCA2",
    "score": 0.995
  },
  {
    "stringId_A": "9606.ENSP00000278616",
    "stringId_B": "9606.ENSP00000418960",
    "preferredName_A": "ATM",
    "preferredName_B": "BRCA1",
    "score": 0.999
  },
  {
    "stringId_A": "9606.ENSP00000278616",
    "stringId_B": "9606.ENSP00000343741",
    "preferredName_A": "ATM",
    "preferredName_B": "ATR",
    "score": 0.999
  },
  {
    "stringId_A": "9606.ENSP00000343741",
    "stringId_B": "9606.ENSP00000369497",
    "preferredName_A": "ATR",
    "preferredName_B": "BRCA2",
    "score": 0.831
  },
  {
    "stringId_A": "9606.ENSP00000343741",
    "stringId_B": "9606.ENSP00000418960",
    "preferredName_A": "ATR",
    "preferredName_B": "BRCA1",
    "score": 0.996
  },
  {
    "stringId_A": "9606.ENSP00000369497",
    "stringId_B": "9606.ENSP00000418960",
    "preferredName_A": "BRCA2",
    "preferredName_B": "BRCA1",
    "score": 0.999
  }
]
```

**Key Findings**: All interactions show very high confidence scores (>0.8), with most exceeding 0.99, indicating these proteins form a tightly interconnected functional module.

#### 4. Network Statistics

Check if this network is significantly enriched for interactions:

```json
{
  "number_of_nodes": 5,
  "number_of_edges": 10,
  "average_node_degree": 4.0,
  "local_clustering_coefficient": 1.0,
  "expected_number_of_edges": 5,
  "p_value": 0.0122
}
```

**Statistical Significance**: The network shows perfect clustering (coefficient = 1.0) and is significantly enriched for interactions (p = 0.0122), with twice as many edges as expected by chance.

#### 5. Functional Enrichment Analysis

Analyze which biological pathways are enriched in this protein set:

**Top DNA Repair Pathways (Selected Results)**:

```json
[
  {
    "category": "Process",
    "term": "GO:0071479",
    "number_of_genes": 5,
    "preferredNames": ["TP53", "ATM", "ATR", "BRCA2", "BRCA1"],
    "p_value": 9.72e-13,
    "fdr": 1.52e-08,
    "description": "Cellular response to ionizing radiation"
  },
  {
    "category": "Process",
    "term": "GO:0042770",
    "number_of_genes": 5,
    "preferredNames": ["TP53", "ATM", "ATR", "BRCA2", "BRCA1"],
    "p_value": 1.69e-11,
    "fdr": 1.32e-07,
    "description": "Signal transduction in response to DNA damage"
  },
  {
    "category": "Process",
    "term": "GO:0006281",
    "number_of_genes": 5,
    "preferredNames": ["TP53", "ATM", "ATR", "BRCA2", "BRCA1"],
    "p_value": 1.05e-08,
    "fdr": 1.10e-05,
    "description": "DNA repair"
  },
  {
    "category": "KEGG",
    "term": "hsa03440",
    "number_of_genes": 3,
    "preferredNames": ["ATM", "BRCA2", "BRCA1"],
    "p_value": 8.34e-08,
    "fdr": 2.80e-05,
    "description": "Homologous recombination"
  },
  {
    "category": "KEGG",
    "term": "hsa04115",
    "number_of_genes": 3,
    "preferredNames": ["TP53", "ATM", "ATR"],
    "p_value": 5.27e-07,`
    "fdr": 5.44e-05,`
    "description": "p53 signaling pathway"
  }
]
```

**Disease Associations**:

```json
[
  {
    "category": "DISEASES",
    "term": "DOID:1612",
    "number_of_genes": 4,
    "preferredNames": ["TP53", "ATM", "BRCA2", "BRCA1"],
    "p_value": 5.72e-10,
    "fdr": 2.02e-06,
    "description": "Breast cancer"
  },
  {
    "category": "DISEASES",
    "term": "DOID:3012",
    "number_of_genes": 3,
    "preferredNames": ["TP53", "BRCA2", "BRCA1"],
    "p_value": 6.59e-10,
    "fdr": 2.02e-06,
    "description": "Li-Fraumeni syndrome"
  }
]
```


The package can generate protein interaction network visualizations showing evidence-based functional associations.

**Example Network Visualization**: [View Protein Interaction Network](https://string-db.org/api/svg/network?identifiers=9606.ENSP00000269305%0d9606.ENSP00000418960%0d9606.ENSP00000369497%0d9606.ENSP00000278616%0d9606.ENSP00000343741&caller_identity=string_mcp_bridge&species=9606&required_score=400&show_query_node_labels=1)
![DNA Repair Protein Network](https://string-db.org/api/highres_image/network?identifiers=9606.ENSP00000269305%0d9606.ENSP00000418960%0d9606.ENSP00000369497%0d9606.ENSP00000278616%0d9606.ENSP00000343741&caller_identity=string_mcp_bridge&species=9606&required_score=400&show_query_node_labels=1)
This visualization shows the protein-protein interaction network for TP53, BRCA1, BRCA2, ATM, and ATR with high-confidence interactions (score ≥ 400).

#### 7. Functional Enrichment Visualization

The package can also create enrichment scatter plots showing the most significantly enriched biological processes.

**Example Enrichment Visualization**: [View Functional Enrichment Plot](https://string-db.org/api/svg/enrichmentfigure?identifiers=TP53%0dBRCA1%0dBRCA2%0dATM%0dATR&species=9606&caller_identity=string_mcp_bridge&number_of_term_shown=10)
![Functional Enrichment Plot](https://string-db.org/api/image/enrichmentfigure?identifiers=TP53%0dBRCA1%0dBRCA2%0dATM%0dATR&species=9606&caller_identity=string_mcp_bridge&number_of_term_shown=10)

This visualization displays the top 10 most significantly enriched biological processes and pathways for the DNA repair protein set, showing p-values and gene counts for each enriched term.

### Summary

This comprehensive analysis demonstrates that the STRING-DB MCP bridge successfully:
- **Identified all 5 DNA repair proteins** with detailed annotations
- **Discovered 10 high-confidence protein interactions** (all >0.8 score)
- **Revealed significant pathway enrichments** with p-values < 1e-8
- **Confirmed statistical significance** of the network (p = 0.0122)
- **Generated both network and enrichment visualizations**

The results validate these proteins as a core DNA damage response module, with exceptionally strong enrichment for:

- Cellular response to ionizing radiation (p = 1.52e-8)
- DNA damage signaling (p = 1.32e-7)
- Homologous recombination (p = 2.8e-5)
- p53 signaling pathway (p = 5.44e-5)
- Breast cancer associations (p = 2.02e-6)v
This showcases the complete functionality of the STRING-DB MCP bridge for protein interaction network analysis and functional annotation.