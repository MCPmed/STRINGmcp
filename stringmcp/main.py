#!/usr/bin/env python3
"""
STRING‑DB → Model‑Context‑Protocol bridge (Complete)
=====================================================
A fully self‑contained server that speaks the **MCP 2025‑03‑26** JSON‑RPC
dialect and exposes ALL STRING REST endpoints that return text/JSON.

Supported tools
--------------------------
    • map_identifiers             – /get_string_ids
    • get_network_interactions    – /network
    • get_functional_enrichment   – /enrichment
    • get_functional_annotation   – /functional_annotation
    • get_interaction_partners    – /interaction_partners
    • get_homology                – /homology
    • get_homology_best           – /homology_best
    • get_ppi_enrichment          – /ppi_enrichment
    • get_version_info            – /version
    • get_network_image           – /image/network
    • get_enrichment_figure       – /image/enrichment

Protocol compliance highlights
------------------------------
* Responds **only** to requests that carry an `id`; notifications are logged
  but never answered (per JSON‑RPC §5).
* `initialize` → `capabilities.tools.executable = true`.
* Every `tools/call` result carries `isError` (false on success).
* Tool descriptors use the modern `parameters` key *and* keep the legacy
  `inputSchema` for backward compatibility.
* All STRING calls are `GET` (docs recommend it; POST imposes URL‑length
  limits anyway).
* One‑second polite delay between calls.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

# ──────────────────────────────────────────────────────────────
#  STRING HTTP wrapper
# ──────────────────────────────────────────────────────────────
class OutputFormat(Enum):
    TSV = "tsv"
    TSV_NO_HEADER = "tsv-no-header"
    JSON = "json"
    XML = "xml"
    PSI_MI = "psi-mi"
    PSI_MI_TAB = "psi-mi-tab"


@dataclass
class StringConfig:
    base_url: str = "https://string-db.org/api"
    version_url: str = "https://version-12-0.string-db.org/api"  # pin to v12
    caller_identity: str = "string_mcp_bridge"
    delay: float = 1.0  # polite delay between HTTP calls


class StringDBBridge:
    """Complete helper around STRING REST API (JSON responses only)."""

    def __init__(self, cfg: StringConfig | None = None) -> None:
        self.cfg = cfg or StringConfig()
        self.session = requests.Session()

    # internal --------------------------------------------------------------
    def _get(self, endpoint: str, fmt: OutputFormat, params: Dict[str, Any]) -> Any:
        url = f"{self.cfg.version_url}/{fmt.value}/{endpoint}"
        params.setdefault("caller_identity", self.cfg.caller_identity)
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        time.sleep(self.cfg.delay)
        return resp.json() if fmt == OutputFormat.JSON else resp.text

    # mapping ---------------------------------------------------------------
    def map_identifiers(self, identifiers: List[str], *, species: int | None = None,
                        echo_query: bool = False, limit: int | None = None) -> List[Dict[str, Any]]:
        """Map protein identifiers to STRING IDs."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p = {"identifiers": "%0d".join(identifiers), "echo_query": int(echo_query)}
        if species is not None:
            p["species"] = species
        if limit is not None:
            p["limit"] = limit
        data = self._get("get_string_ids", OutputFormat.JSON, p)
        return data if isinstance(data, list) else []

    # network ----------------------------------------------------------------
    def get_network_interactions(self, identifiers: List[str], *, species: int | None = None,
                                 required_score: int | None = None, add_nodes: int = 0,
                                 network_type: str = "functional") -> List[Dict[str, Any]]:
        """Retrieve STRING interaction edges."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p: Dict[str, Any] = {
            "identifiers": "%0d".join(identifiers),
            "network_type": network_type,
            "show_query_node_labels": 0,
        }
        if species is not None:
            p["species"] = species
        if required_score is not None:
            p["required_score"] = required_score
        if add_nodes:
            p["add_nodes"] = add_nodes
        data = self._get("network", OutputFormat.JSON, p)
        return data if isinstance(data, list) else []

    # enrichment ------------------------------------------------------------
    def get_functional_enrichment(self, identifiers: List[str], *, species: int | None = None,
                                  background_identifiers: List[str] | None = None) -> List[Dict[str, Any]]:
        """Perform GO / pathway enrichment on a protein set."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p: Dict[str, Any] = {"identifiers": "%0d".join(identifiers)}
        if species is not None:
            p["species"] = species
        if background_identifiers:
            p["background_string_identifiers"] = "%0d".join(background_identifiers)
        data = self._get("enrichment", OutputFormat.JSON, p)
        return data if isinstance(data, list) else []

    # functional annotation -------------------------------------------------
    def get_functional_annotation(self, identifiers: List[str], *, species: int | None = None,
                                   allow_pubmed: bool = False, only_pubmed: bool = False) -> List[Dict[str, Any]]:
        """Retrieve all functional annotations for proteins (not only enriched subset)."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p: Dict[str, Any] = {"identifiers": "%0d".join(identifiers)}
        if species is not None:
            p["species"] = species
        if allow_pubmed:
            p["allow_pubmed"] = 1
        if only_pubmed:
            p["only_pubmed"] = 1
        data = self._get("functional_annotation", OutputFormat.JSON, p)
        return data if isinstance(data, list) else []

    # interaction partners --------------------------------------------------
    def get_interaction_partners(self, identifiers: List[str], *, species: int | None = None,
                                 limit: int | None = None, required_score: int | None = None,
                                 network_type: str = "functional") -> List[Dict[str, Any]]:
        """Retrieve interaction partners for given proteins."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p: Dict[str, Any] = {
            "identifiers": "%0d".join(identifiers),
            "network_type": network_type,
        }
        if species is not None:
            p["species"] = species
        if limit is not None:
            p["limit"] = limit
        if required_score is not None:
            p["required_score"] = required_score
        data = self._get("interaction_partners", OutputFormat.JSON, p)
        return data if isinstance(data, list) else []

    # homology --------------------------------------------------------------
    def get_homology(self, identifiers: List[str], *, species: int | None = None) -> List[Dict[str, Any]]:
        """Get homology information for proteins."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p = {"identifiers": "%0d".join(identifiers)}
        if species is not None:
            p["species"] = species
        data = self._get("homology", OutputFormat.JSON, p)
        return data if isinstance(data, list) else []

    def get_homology_best(self, identifiers: List[str], *, species: int | None = None,
                           species_b: List[int] | None = None) -> List[Dict[str, Any]]:
        """Get best homology matches for proteins."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p = {"identifiers": "%0d".join(identifiers)}
        if species is not None:
            p["species"] = species
        if species_b:
            p["species_b"] = "%0d".join(map(str, species_b))
        data = self._get("homology_best", OutputFormat.JSON, p)
        return data if isinstance(data, list) else []

    # PPI enrichment --------------------------------------------------------
    def get_ppi_enrichment(self, identifiers: List[str], *, species: int | None = None,
                            required_score: int | None = None) -> Dict[str, Any]:
        """Get protein-protein interaction enrichment statistics."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        p = {"identifiers": "%0d".join(identifiers)}
        if species is not None:
            p["species"] = species
        if required_score is not None:
            p["required_score"] = required_score
        data = self._get("ppi_enrichment", OutputFormat.JSON, p)
        return data[0] if isinstance(data, list) and data else data

    # version ----------------------------------------------------------------
    def get_version_info(self) -> List[Dict[str, Any]]:
        """Return the current STRING database version."""
        data = self._get("version", OutputFormat.JSON, {})
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []

    # image URL builders -----------------------------------------------------
    def build_network_image_url(self, identifiers: List[str], *, species: int | None = None,
                                add_color_nodes: int | None = None, add_white_nodes: int | None = None,
                                required_score: int | None = None, network_type: str = "functional",
                                network_flavor: str = "evidence", highres: bool = True,
                                svg: bool = False, hide_node_labels: bool = False,
                                hide_disconnected_nodes: bool = False, show_query_node_labels: bool = False,
                                block_structure_pics_in_bubbles: bool = False, flat_node_design: bool = False,
                                center_node_labels: bool = False, custom_label_font_size: int | None = None) -> str:
        """Build URL for STRING network image with all available options."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        
        # Determine output format based on parameters
        if svg:
            output_format = "svg"
        elif highres:
            output_format = "highres_image"
        else:
            output_format = "image"
        
        # Use the correct URL format: https://string-db.org/api/[output-format]/network
        url = f"{self.cfg.base_url}/{output_format}/network"
        
        # Build parameters
        params = {
            "identifiers": "%0d".join(identifiers),
            "caller_identity": self.cfg.caller_identity,
        }
        
        # Add optional parameters only if they differ from defaults or are specified
        if species is not None:
            params["species"] = species
        if add_color_nodes is not None:
            params["add_color_nodes"] = add_color_nodes
        if add_white_nodes is not None:
            params["add_white_nodes"] = add_white_nodes
        if required_score is not None:
            params["required_score"] = required_score
        if network_type != "functional":  # functional is default
            params["network_type"] = network_type
        if network_flavor != "evidence":  # evidence is default
            params["network_flavor"] = network_flavor
        
        # Visual parameters - only include if different from defaults
        if hide_node_labels:
            params["hide_node_labels"] = 1
        if hide_disconnected_nodes:
            params["hide_disconnected_nodes"] = 1
        if show_query_node_labels:
            params["show_query_node_labels"] = 1
        if block_structure_pics_in_bubbles:
            params["block_structure_pics_in_bubbles"] = 1
        if flat_node_design:
            params["flat_node_design"] = 1
        if center_node_labels:
            params["center_node_labels"] = 1
        if custom_label_font_size is not None:
            # Validate font size range (5-50 according to docs)
            if not (5 <= custom_label_font_size <= 50):
                raise ValueError("custom_label_font_size must be between 5 and 50")
            params["custom_label_font_size"] = custom_label_font_size
        
        # Build final URL with query string
        return f"{url}?{urlencode(params)}"

    def build_enrichment_figure_url(self, identifiers: List[str], species: int,
                                    category: str = "Process", group_by_similarity: float | None = None,
                                    color_palette: str | None = None, number_of_term_shown: int | None = None,
                                    x_axis: str | None = None, highres: bool = False,
                                    svg: bool = False) -> str:
        """Build URL for STRING enrichment figure."""
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")
        
        # Determine output format
        if svg:
            output_format = "svg"
        elif highres:
            output_format = "highres_image"
        else:
            output_format = "image"
        
        # Correct URL format for enrichment figures - NOTE: endpoint is 'enrichmentfigure' not 'enrichment'
        url = f"{self.cfg.base_url}/{output_format}/enrichmentfigure"
        
        # Build URL manually to avoid double-encoding issues
        # The identifiers should be joined with %0d delimiter
        identifier_string = "%0d".join(identifiers)
        query_string = f"identifiers={identifier_string}&species={species}&caller_identity={self.cfg.caller_identity}"
        
        # Add optional parameters
        if category != "Process":
            query_string += f"&category={category}"
        if group_by_similarity is not None:
            query_string += f"&group_by_similarity={group_by_similarity}"
        if color_palette is not None:
            query_string += f"&color_palette={color_palette}"
        if number_of_term_shown is not None:
            query_string += f"&number_of_term_shown={number_of_term_shown}"
        if x_axis is not None:
            query_string += f"&x_axis={x_axis}"
        
        return f"{url}?{query_string}"

    def _download_image(self, url: str) -> str:
        """Download image from URL and return local path."""
        import os
        import tempfile
        from urllib.parse import urlparse
        
        # Create a temporary file with appropriate extension
        if "/svg/" in url or url.endswith('.svg'):
            suffix = '.svg'
        else:
            suffix = '.png'
        
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            tmp_file.write(response.content)
            time.sleep(self.cfg.delay)  # Be polite
            return tmp_file.name

    def fetch_svg_content(self, url: str) -> str:
        """Fetch SVG content from URL and return as string."""
        if "/svg/" not in url:
            raise ValueError("URL does not appear to be an SVG endpoint")
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        time.sleep(self.cfg.delay)  # Be polite
        return response.text


# ──────────────────────────────────────────────────────────────
#  Exceptions
# ──────────────────────────────────────────────────────────────
class MCPError(Exception):
    """Raised when user input violates tool schema/rules."""


# ──────────────────────────────────────────────────────────────
#  MCP server implementation
# ──────────────────────────────────────────────────────────────
class StringMCPServer:
    """Reads JSON‑RPC on stdin and writes JSON‑RPC on stdout."""

    def __init__(self) -> None:
        self.bridge = StringDBBridge()
        self.request_id: Optional[int] = None

    # ── helpers to build MCP structures ──────────────────────────────────────
    @staticmethod
    def _text_block(text: str) -> Dict[str, str]:
        return {"type": "text", "text": text}

    @staticmethod
    def _svg_content_block(svg_content: str) -> Dict[str, str]:
        return {"type": "text", "text": f"SVG Content:\n{svg_content}"}

    @staticmethod
    def _success_payload(data: Any) -> Dict[str, Any]:
        text = json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, (list, dict)) else str(data)
        return {"isError": False, "content": [StringMCPServer._text_block(text)]}

    @staticmethod
    def _success_payload_with_svg(data: Any, svg_content: str = None) -> Dict[str, Any]:
        content_blocks = []
        text = json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, (list, dict)) else str(data)
        content_blocks.append(StringMCPServer._text_block(text))
        if svg_content:
            content_blocks.append(StringMCPServer._svg_content_block(svg_content))
        return {"isError": False, "content": content_blocks}

    @staticmethod
    def _error_payload(msg: str) -> Dict[str, Any]:
        return {"isError": True, "content": [StringMCPServer._text_block(f"Error: {msg}")]}

    def _send(self, *, result: Optional[Dict[str, Any]] = None, error: Optional[Dict[str, Any]] = None) -> None:
        """Emit a JSON-RPC response (or error) on stdout."""
        if self.request_id is None:
            # Never send a response to a notification
            return

        payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": self.request_id}
        if error is not None:
            payload["error"] = error
        else:
            payload["result"] = result or {}

        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), flush=True)

    # ── RPC method handlers ──────────────────────────────────────────────────
    def _handle_initialize(self, params: Dict[str, Any]) -> None:
        client_version = params.get("protocolVersion", "2025-03-26")
        result = {
            "protocolVersion": client_version,
            "capabilities": {"tools": {"executable": True}},
            "serverInfo": {"name": "string-mcp", "version": "1.0.0"},
        }
        self._send(result=result)

    def _handle_list_tools(self, _: Dict[str, Any]):
        def td(name: str, desc: str, schema: Dict[str, Any]):
            return {"name": name, "description": desc, "parameters": schema, "inputSchema": schema}

        common_ids_prop = {
            "identifiers": {"type": "array", "items": {"type": "string"}, "description": "Protein list"}
        }

        tools: List[Dict[str, Any]] = [
            # Core functional API endpoints
            td("map_identifiers", "Map protein identifiers to STRING IDs.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                    "echo_query": {"type": "boolean", "description": "Echo query identifiers in response"},
                    "limit": {"type": "integer", "description": "Limit number of results"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_network_interactions", "Retrieve STRING interaction edges.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                    "required_score": {"type": "integer", "description": "Interaction confidence score threshold (0-1000)"},
                    "add_nodes": {"type": "integer", "description": "Number of additional nodes to add"},
                    "network_type": {"type": "string", "enum": ["functional", "physical"], "description": "Type of interactions"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_functional_enrichment", "Perform GO / pathway enrichment on a protein set.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                    "background_identifiers": {"type": "array", "items": {"type": "string"}, 
                                             "description": "Background proteome for enrichment analysis"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_functional_annotation", "Retrieve all functional annotations for proteins.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                    "allow_pubmed": {"type": "boolean", "description": "Include PubMed annotations (default: false)"},
                    "only_pubmed": {"type": "boolean", "description": "Return only PubMed annotations (default: false)"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_interaction_partners", "Retrieve interaction partners for given proteins.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                    "limit": {"type": "integer", "description": "Maximum number of partners to return"},
                    "required_score": {"type": "integer", "description": "Interaction confidence score threshold (0-1000)"},
                    "network_type": {"type": "string", "enum": ["functional", "physical"], "description": "Type of interactions"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_homology", "Get homology information for proteins.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_homology_best", "Get best homology matches for proteins.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "Source species NCBI/STRING taxon"},
                    "species_b": {"type": "array", "items": {"type": "integer"}, 
                                "description": "Target species list for homology search"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_ppi_enrichment", "Get protein-protein interaction enrichment statistics.", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                    "required_score": {"type": "integer", "description": "Interaction confidence score threshold (0-1000)"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_version_info", "Return the current STRING database version.", {
                "type": "object", 
                "properties": {}
            }),
            
            # Image generation endpoints
            td("get_network_image", "Return URL of STRING network image", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (e.g. 9606 for human)"},
                    "highres": {"type": "boolean", "description": "High resolution image (default: true)"},
                    "svg": {"type": "boolean", "description": "Vector graphic format (SVG)"},
                    "network_type": {"type": "string", "enum": ["functional", "physical"], "description": "Network type (default: functional)"},
                    "network_flavor": {"type": "string", "enum": ["evidence", "confidence", "actions"], "description": "Style of edges (default: evidence)"},
                    "required_score": {"type": "integer", "description": "Threshold of significance (0-1000)"},
                    "add_color_nodes": {"type": "integer", "description": "Adds color nodes based on scores to input proteins"},
                    "add_white_nodes": {"type": "integer", "description": "Adds white nodes based on scores (added after color nodes)"},
                    "download_image": {"type": "boolean", "description": "Download image to local file"},
                },
                "required": ["identifiers"]
            }),
            
            td("get_enrichment_figure", "Return URL of enrichment scatter figure", {
                "type": "object",
                "properties": {
                    **common_ids_prop,
                    "species": {"type": "integer", "description": "NCBI/STRING taxon (required)"},
                    "category": {"type": "string", "description": "Enrichment category (default: Process)"},
                    "group_by_similarity": {"type": "number", "description": "Group terms by similarity"},
                    "color_palette": {"type": "string", "description": "Color palette for visualization"},
                    "number_of_term_shown": {"type": "integer", "description": "Maximum number of terms to show"},
                    "x_axis": {"type": "string", "description": "X-axis parameter"},
                    "highres": {"type": "boolean", "description": "High resolution image (default: false)"},
                    "svg": {"type": "boolean", "description": "Vector graphic format (SVG)"},
                    "download_image": {"type": "boolean", "description": "Download image to local file"},
                },
                "required": ["identifiers", "species"]
            }),
        ]
        self._send(result={"tools": tools})

    def _handle_call_tool(self, params: Dict[str, Any]) -> None:
        name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if name == "map_identifiers":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.map_identifiers(
                    identifiers=ids,
                    species=arguments.get("species"),
                    echo_query=arguments.get("echo_query", False),
                    limit=arguments.get("limit"),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_network_interactions":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.get_network_interactions(
                    identifiers=ids,
                    species=arguments.get("species"),
                    required_score=arguments.get("required_score"),
                    add_nodes=arguments.get("add_nodes", 0),
                    network_type=arguments.get("network_type", "functional"),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_functional_enrichment":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.get_functional_enrichment(
                    identifiers=ids,
                    species=arguments.get("species"),
                    background_identifiers=arguments.get("background_identifiers"),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_functional_annotation":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.get_functional_annotation(
                    identifiers=ids,
                    species=arguments.get("species"),
                    allow_pubmed=arguments.get("allow_pubmed", False),
                    only_pubmed=arguments.get("only_pubmed", False),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_interaction_partners":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.get_interaction_partners(
                    identifiers=ids,
                    species=arguments.get("species"),
                    limit=arguments.get("limit"),
                    required_score=arguments.get("required_score"),
                    network_type=arguments.get("network_type", "functional"),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_homology":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.get_homology(
                    identifiers=ids,
                    species=arguments.get("species"),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_homology_best":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.get_homology_best(
                    identifiers=ids,
                    species=arguments.get("species"),
                    species_b=arguments.get("species_b"),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_ppi_enrichment":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                data = self.bridge.get_ppi_enrichment(
                    identifiers=ids,
                    species=arguments.get("species"),
                    required_score=arguments.get("required_score"),
                )
                self._send(result=self._success_payload(data))

            elif name == "get_version_info":
                data = self.bridge.get_version_info()
                self._send(result=self._success_payload(data))

            elif name == "get_network_image":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                
                url = self.bridge.build_network_image_url(
                    identifiers=ids,
                    species=arguments.get("species"),
                    add_color_nodes=arguments.get("add_color_nodes"),
                    add_white_nodes=arguments.get("add_white_nodes"),
                    required_score=arguments.get("required_score"),
                    network_type=arguments.get("network_type", "functional"),
                    network_flavor=arguments.get("network_flavor", "evidence"),
                    highres=arguments.get("highres", True),
                    svg=arguments.get("svg", False),
                    hide_node_labels=arguments.get("hide_node_labels", False),
                    hide_disconnected_nodes=arguments.get("hide_disconnected_nodes", False),
                    show_query_node_labels=arguments.get("show_query_node_labels", False),
                    block_structure_pics_in_bubbles=arguments.get("block_structure_pics_in_bubbles", False),
                    flat_node_design=arguments.get("flat_node_design", False),
                    center_node_labels=arguments.get("center_node_labels", False),
                    custom_label_font_size=arguments.get("custom_label_font_size"),
                )
                
                # Test the URL by making a HEAD request
                try:
                    test_response = self.bridge.session.head(url, timeout=10)
                    if test_response.status_code != 200:
                        print(f"Warning: URL may be invalid (status {test_response.status_code}): {url}", file=sys.stderr)
                except requests.RequestException as e:
                    print(f"Warning: Could not verify URL: {e}", file=sys.stderr)
                
                if arguments.get("download_image"):
                    local_path = self.bridge._download_image(url)
                    self._send(result=self._success_payload({"image_path": local_path}))
                else:
                    self._send(result=self._success_payload({"image_url": url}))

            elif name == "get_enrichment_figure":
                ids = arguments.get("identifiers", [])
                if not ids:
                    raise ValueError("identifiers parameter is required and cannot be empty")
                species = arguments.get("species")
                if species is None:
                    raise ValueError("species parameter is required for get_enrichment_figure")
                
                url = self.bridge.build_enrichment_figure_url(
                    identifiers=ids,
                    species=species,
                    category=arguments.get("category", "Process"),
                    group_by_similarity=arguments.get("group_by_similarity"),
                    color_palette=arguments.get("color_palette"),
                    number_of_term_shown=arguments.get("number_of_term_shown"),
                    x_axis=arguments.get("x_axis"),
                    highres=arguments.get("highres", False),
                    svg=arguments.get("svg", False),
                )
                
                # Test the URL
                try:
                    test_response = self.bridge.session.head(url, timeout=10)
                    if test_response.status_code != 200:
                        print(f"Warning: URL may be invalid (status {test_response.status_code}): {url}", file=sys.stderr)
                except requests.RequestException as e:
                    print(f"Warning: Could not verify URL: {e}", file=sys.stderr)
                
                if arguments.get("download_image"):
                    local_path = self.bridge._download_image(url)
                    self._send(result=self._success_payload({"image_path": local_path}))
                else:
                    self._send(result=self._success_payload({"image_url": url}))

            else:
                self._send(result=self._error_payload(f"Unknown tool: {name}"))

        except requests.RequestException as e:
            self._send(result=self._error_payload(f"HTTP request failed: {e}"))
        except ValueError as e:
            self._send(result=self._error_payload(str(e)))
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            self._send(result=self._error_payload(f"Internal error: {e}"))

    # simple stubs for optional endpoints
    def _handle_list_resources(self, _: Dict[str, Any]) -> None:
        self._send(result={"resources": []})

    def _handle_list_prompts(self, _: Dict[str, Any]) -> None:
        self._send(result={"prompts": []})

    # ── main event loop ───────────────────────────────────────────────────────
    def run(self) -> None:
        print("STRING-DB MCP server ready (Complete API coverage) …", file=sys.stderr)
        for raw in sys.stdin:
            line = raw.strip()
            if not line:
                continue

            try:
                req = json.loads(line)
            except json.JSONDecodeError as e:
                self.request_id = None  # can't reply usefully
                print(f"Bad JSON from host: {e}", file=sys.stderr)
                continue

            self.request_id = req.get("id")  # None for notifications
            method = req.get("method")
            params = req.get("params", {})

            # Notifications (id is None) —> do not respond
            if self.request_id is None:
                if method == "notifications/initialized":
                    print("Client says: initialized", file=sys.stderr)
                # ignore any others silently
                continue

            if method == "initialize":
                self._handle_initialize(params)
            elif method == "tools/list":
                self._handle_list_tools(params)
            elif method == "tools/call":
                self._handle_call_tool(params)
            elif method == "resources/list":
                self._handle_list_resources(params)
            elif method == "prompts/list":
                self._handle_list_prompts(params)
            else:
                self._send(error={"code": -32601, "message": f"Method not found: {method}"})


def main() -> None:
    StringMCPServer().run()


if __name__ == "__main__":
    sys.exit(main())