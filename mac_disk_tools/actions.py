# -*- coding: utf-8 -*-
"""Finder actions and deletion safety policy."""

from __future__ import annotations

import json
import os
import subprocess

from .config import PATHS_CONFIG

PROTECTED_DANGER_ZH = "此路径被标记为「不建议直接删除」，请使用应用内清理或更安全的卸载方式。"
PROTECTED_DANGER_EN = "This path is marked as Not recommended. Use an in-app cleanup or safer uninstall path."
PROTECTED_UNKNOWN_ZH = "此路径不在工具配置的扫描范围内，已阻止删除。"
PROTECTED_UNKNOWN_EN = "This path is outside the configured scan roots, so deletion was blocked."
MISSING_PATH_ZH = "路径不存在"
MISSING_PATH_EN = "Path does not exist"


def normalize_path(path: str):
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))


def _contains_path(root: str, candidate: str):
    try:
        return os.path.commonpath([root, candidate]) == root
    except ValueError:
        return False


def _configured_roots():
    roots = []
    for cfg in PATHS_CONFIG:
        root = normalize_path(cfg["path"])
        roots.append((root, cfg))
    roots.sort(key=lambda item: len(item[0]), reverse=True)
    return roots


def classify_configured_path(path: str):
    target = normalize_path(path)
    for root, cfg in _configured_roots():
        if target == root or _contains_path(root, target):
            return cfg
    return None


def get_delete_policy(path: str, require_exists=False):
    if not path:
        return {
            "deletable": False,
            "delete_safety": None,
            "delete_reason": MISSING_PATH_ZH,
            "delete_reason_en": MISSING_PATH_EN,
        }

    normalized = normalize_path(path)
    cfg = classify_configured_path(normalized)
    if cfg is None:
        return {
            "deletable": False,
            "delete_safety": None,
            "delete_reason": PROTECTED_UNKNOWN_ZH,
            "delete_reason_en": PROTECTED_UNKNOWN_EN,
        }

    if cfg.get("safety") == "danger":
        return {
            "deletable": False,
            "delete_safety": "danger",
            "delete_reason": PROTECTED_DANGER_ZH,
            "delete_reason_en": PROTECTED_DANGER_EN,
        }

    if require_exists and not os.path.exists(normalized):
        return {
            "deletable": False,
            "delete_safety": cfg.get("safety"),
            "delete_reason": MISSING_PATH_ZH,
            "delete_reason_en": MISSING_PATH_EN,
        }

    return {
        "deletable": True,
        "delete_safety": cfg.get("safety"),
        "delete_reason": "",
        "delete_reason_en": "",
    }


def attach_delete_policy(item: dict):
    item.update(get_delete_policy(item.get("real_path") or item.get("path") or ""))
    return item


def open_in_finder(path: str):
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return False, MISSING_PATH_ZH
    try:
        subprocess.Popen(["open", expanded])
        return True, "已在 Finder 中打开"
    except Exception as exc:
        return False, str(exc)


def move_to_trash(path: str):
    policy = get_delete_policy(path, require_exists=True)
    if not policy["deletable"]:
        return False, policy["delete_reason"]

    expanded = normalize_path(path)
    try:
        script = f'tell application "Finder" to delete POSIX file {json.dumps(expanded)}'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "✅ 已移入废纸篓"
        return False, result.stderr.strip() or "操作失败"
    except Exception as exc:
        return False, str(exc)
