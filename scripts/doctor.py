#!/usr/bin/env python3
"""Diagnose prerequisites used by the verified frontend review plugin."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
EXTENSION_DIR = ROOT / "assets" / "cdp-bridge-extension"
REQUIRED_EXTENSION_FILES = ("manifest.json", "background.js", "popup.html", "LICENSE")
REQUIRED_PERMISSIONS = {"debugger", "tabs", "scripting", "alarms"}


def find_workspace_root(start: Path) -> Path:
    """Locate user-local configuration from the active workspace, not plugin files."""

    current = start.resolve()
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in (".git", ".github", "AGENTS.md", "CLAUDE.md")):
            return candidate
    return current


def check_local_config(path: Path, required_keys: tuple[str, ...], env_keys: tuple[str, ...]) -> dict[str, Any]:
    """Report credential readiness without returning any credential values."""

    if all(os.environ.get(key) for key in env_keys):
        return {"status": "configured", "source": "environment", "note": "未执行远端认证测试"}
    if not path.is_file():
        return {"status": "missing", "path": str(path)}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"status": "invalid", "path": str(path), "detail": str(error)}
    missing = [key for key in required_keys if not payload.get(key)]
    return {
        "status": "configured" if not missing else "incomplete",
        "path": str(path),
        "missingKeys": missing,
        "note": "configured 仅表示字段完整，实际调用仍可能因过期或权限失败",
    }


def check_command(name: str) -> dict[str, Any]:
    """Resolve executables without invoking package downloads during diagnostics."""

    path = shutil.which(name)
    return {"status": "ready" if path else "missing", "path": path}


def check_extension_bundle(directory: Path = EXTENSION_DIR) -> dict[str, Any]:
    """Verify the bundled extension is loadable and matches the pinned bridge release."""

    missing = [name for name in REQUIRED_EXTENSION_FILES if not (directory / name).is_file()]
    if missing:
        return {"status": "invalid", "path": str(directory), "missing": missing}
    try:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"status": "invalid", "path": str(directory), "error": str(error)}

    permissions = set(manifest.get("permissions", []))
    missing_permissions = sorted(REQUIRED_PERMISSIONS - permissions)
    status = "ready" if manifest.get("manifest_version") == 3 and not missing_permissions else "invalid"
    return {
        "status": status,
        "path": str(directory.resolve()),
        "name": manifest.get("name"),
        "version": manifest.get("version"),
        "missingPermissions": missing_permissions,
    }


def probe_bridge(url: str = "http://127.0.0.1:18766/link", timeout: float = 1.2) -> dict[str, Any]:
    """Use the bridge's real session endpoint instead of treating an open port as healthy."""

    request = Request(
        url,
        data=json.dumps({"cmd": "get_all_sessions"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError) as error:
        return {
            "status": "server_not_running",
            "url": url,
            "sessionCount": 0,
            "detail": f"{type(error).__name__}: {error}",
        }

    sessions = payload.get("r") or []
    session_count = len(sessions) if isinstance(sessions, (list, dict)) else 0
    return {
        "status": "ready" if session_count else "extension_not_connected",
        "url": url,
        "sessionCount": session_count,
    }


def diagnose() -> dict[str, Any]:
    """Return actionable state without exposing tokens or browser session contents."""

    workspace = find_workspace_root(Path.cwd())
    checks = {
        "node": check_command("node"),
        "npx": check_command("npx"),
        "uvx": check_command("uvx"),
        "figmaAuth": {
            "status": "ready" if os.environ.get("FIGMA_API_KEY") else "not_in_environment",
            "note": "已有其他已授权 Figma 连接时可忽略此项。",
        },
        "extensionBundle": check_extension_bundle(),
        "cdpBridge": probe_bridge(),
        "cteamOpenApi": check_local_config(
            workspace / ".ops-local" / "cw-credentials.json",
            ("userId", "token"),
            ("CW_USER_ID", "CW_ACCESS_TOKEN"),
        ),
        "cteamImageLogin": check_local_config(
            workspace / ".ops-local" / "cw-browser-login.json",
            ("loginUrl", "username", "password"),
            ("CW_LOGIN_URL", "CW_USERNAME", "CW_PASSWORD"),
        ),
    }
    fatal = [name for name in ("node", "npx", "uvx", "extensionBundle") if checks[name]["status"] != "ready"]
    bridge_status = checks["cdpBridge"]["status"]
    overall = "ready" if not fatal and bridge_status == "ready" else "action_required"
    return {
        "status": overall,
        "workspace": str(workspace),
        "checks": checks,
        "extensionInstall": {
            "path": str(EXTENSION_DIR.resolve()),
            "steps": [
                "打开 chrome://extensions/",
                "开启开发者模式",
                "点击“加载已解压的扩展程序”",
                "选择 extensionInstall.path 指向的目录",
                "调用一次 browser_get_tabs 启动 MCP，等待约 5 秒后重新运行 doctor",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Collab Verified Review MCP and Chrome extension setup")
    parser.add_argument("--require-connected", action="store_true", help="Return failure unless the extension is connected")
    args = parser.parse_args()
    result = diagnose()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.require_connected and result["checks"]["cdpBridge"]["status"] != "ready":
        return 2
    fatal = any(result["checks"][name]["status"] != "ready" for name in ("node", "npx", "uvx", "extensionBundle"))
    return 1 if fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
