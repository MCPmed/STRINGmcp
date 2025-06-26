#!/usr/bin/env python3
"""
STRING-DB API  ➜  MCP bridge
Fully conforms to the Model-Context-Protocol (spec 2025-03-26)

▶  Key compliance points
    • Never responds to JSON-RPC notifications
    • initialize → capabilities.tools = {"executable": true}
    • tools/list descriptors use "parameters" (keeps old "inputSchema" for
      backwards compatibility)
    • tools/call results always contain  isError  (false on success)
"""

import json
import sys
import traceback
import time
from dataclasses import dataclass
from enum   import Enum
from typing import Any, Dict, List, Optional

import requests


# ──────────────────────────────────────────────────────────────────────────────
#  STRING-DB HTTP wrapper
# ──────────────────────────────────────────────────────────────────────────────
class OutputFormat(Enum):
    TSV = "tsv"
    TSV_NO_HEADER = "tsv-no-header"
    JSON = "json"
    XML = "xml"
    IMAGE = "image"
    HIGHRES_IMAGE = "highres_image"
    SVG = "svg"
    PSI_MI = "psi-mi"
    PSI_MI_TAB = "psi-mi-tab"


@dataclass
class StringConfig:
    base_url: str       = "https://string-db.org/api"
    version_url: str    = "https://version-12-0.string-db.org/api"
    caller_identity: str = "string_mcp_bridge"
    request_delay: float  = 1.0          # seconds between calls


class StringDBBridge:
    """Thin wrapper around STRING-DB REST API with polite rate-limiting."""

    def __init__(self, config: StringConfig | None = None) -> None:
        self.cfg = config or StringConfig()
        self.session = requests.Session()

    # ―― helpers ―――――――――――――――――――――――――――――――――――――――――――――――――――――――
    def _make_request(
        self,
        endpoint: str,
        fmt: OutputFormat,
        params: Dict[str, Any],
        use_version_url: bool = False,
    ) -> requests.Response:
        base = self.cfg.version_url if use_version_url else self.cfg.base_url
        url  = f"{base}/{fmt.value}/{endpoint}"

        if "caller_identity" not in params:
            params["caller_identity"] = self.cfg.caller_identity

        # STRING accepts GET; use it to stay cache-friendly
        resp = self.session.get(url, params=params, timeout=30)
        time.sleep(self.cfg.request_delay)
        resp.raise_for_status()
        return resp

    # ―― public API methods ―――――――――――――――――――――――――――――――――――――――――――
    def map_identifiers(
        self,
        identifiers: List[str],
        species: int | None = None,
        echo_query: bool = False,
    ) -> List[Dict[str, Any]]:
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")

        params = {
            "identifiers": "\r".join(identifiers),
            "echo_query": int(echo_query),
        }
        if species is not None:
            params["species"] = species

        data = self._make_request("get_string_ids", OutputFormat.JSON, params).json()
        return data if isinstance(data, list) else []

    def get_network_interactions(
        self,
        identifiers: List[str],
        species: int | None = None,
        required_score: int | None = None,
        add_nodes: int = 0,
        network_type: str = "functional",
    ) -> List[Dict[str, Any]]:
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")

        params = {
            "identifiers": "\r".join(identifiers),
            "network_type": network_type,
            "show_query_node_labels": 0,
        }
        if species is not None:
            params["species"] = species
        if required_score is not None:
            params["required_score"] = required_score
        if add_nodes:
            params["add_nodes"] = add_nodes

        data = self._make_request("network", OutputFormat.JSON, params).json()
        return data if isinstance(data, list) else []

    def get_functional_enrichment(
        self,
        identifiers: List[str],
        species: int | None = None,
        background_identifiers: List[str] | None = None,
    ) -> List[Dict[str, Any]]:
        if not identifiers:
            raise ValueError("identifiers list cannot be empty")

        params = {"identifiers": "\r".join(identifiers)}
        if species is not None:
            params["species"] = species
        if background_identifiers:
            params["background_string_identifiers"] = "\r".join(background_identifiers)

        data = self._make_request("enrichment", OutputFormat.JSON, params).json()
        return data if isinstance(data, list) else []

    def get_version_info(self) -> List[Dict[str, Any]]:
        data = self._make_request("version", OutputFormat.JSON, {}).json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []


# ──────────────────────────────────────────────────────────────────────────────
#  MCP server implementation
# ──────────────────────────────────────────────────────────────────────────────
class StringMCPServer:
    def __init__(self) -> None:
        self.bridge = StringDBBridge()
        self.request_id: int | None = None

    # ── helpers to build MCP structures ──────────────────────────────────────
    @staticmethod
    def _text_block(text: str) -> Dict[str, str]:
        return {"type": "text", "text": text}

    @staticmethod
    def _success_payload(data: Any) -> Dict[str, Any]:
        text = json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, (list, dict)) else str(data)
        return {"isError": False, "content": [StringMCPServer._text_block(text)]}

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
            "serverInfo": {"name": "string-mcp", "version": "0.2.0"},
        }
        self._send(result=result)

    def _handle_list_tools(self, _: Dict[str, Any]) -> None:
        def desc(name: str, description: str, schema: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "name": name,
                "description": description,
                "parameters": schema,     # modern field
                "inputSchema": schema,    # kept for older clients
            }

        tools = [
            desc(
                "map_identifiers",
                "Map protein identifiers to STRING IDs.",
                {
                    "type": "object",
                    "properties": {
                        "identifiers": {"type": "array", "items": {"type": "string"}},
                        "species": {"type": "integer"},
                        "echo_query": {"type": "boolean"},
                    },
                    "required": ["identifiers"],
                },
            ),
            desc(
                "get_network_interactions",
                "Retrieve STRING interaction edges.",
                {
                    "type": "object",
                    "properties": {
                        "identifiers": {"type": "array", "items": {"type": "string"}},
                        "species": {"type": "integer"},
                        "required_score": {"type": "integer"},
                        "add_nodes": {"type": "integer"},
                        "network_type": {"type": "string", "enum": ["functional", "physical"]},
                    },
                    "required": ["identifiers"],
                },
            ),
            desc(
                "get_functional_enrichment",
                "Perform GO / pathway enrichment on a protein set.",
                {
                    "type": "object",
                    "properties": {
                        "identifiers": {"type": "array", "items": {"type": "string"}},
                        "species": {"type": "integer"},
                        "background_identifiers": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["identifiers"],
                },
            ),
            desc(
                "get_version_info",
                "Return the current STRING database version.",
                {"type": "object", "properties": {}},
            ),
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

            elif name == "get_version_info":
                data = self.bridge.get_version_info()
                self._send(result=self._success_payload(data))

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
        print("STRING-DB MCP server ready …", file=sys.stderr)
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