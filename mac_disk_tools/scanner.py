# -*- coding: utf-8 -*-
"""Filesystem scanning helpers for Mac Disk Tools."""

from __future__ import annotations

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

from .config import PATHS_CONFIG, TRANSLATIONS_EN

MAX_SCAN_WORKERS = 8
DU_TIMEOUT_SECONDS = 60


def get_dir_size_bytes(path: str):
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return None
    try:
        result = subprocess.run(
            ["du", "-sk", expanded],
            capture_output=True,
            text=True,
            timeout=DU_TIMEOUT_SECONDS,
        )
        if result.returncode == 0:
            return int(result.stdout.split("\t")[0]) * 1024
    except Exception:
        pass
    return 0


def get_disk_info():
    try:
        result = subprocess.run(["df", "-k", "/"], capture_output=True, text=True)
        parts = result.stdout.strip().split("\n")[1].split()
        total = int(parts[1]) * 1024
        used = int(parts[2]) * 1024
        available = int(parts[3]) * 1024
        return {"total": total, "used": used, "available": available}
    except Exception:
        return {"total": 0, "used": 0, "available": 0}


def fmt(n, lang="zh"):
    missing = "不存在" if lang == "zh" else "Not found"
    if n is None:
        return missing
    if n == 0:
        return "0 B"
    if n < 1024**2:
        return f"{n / 1024:.0f} KB"
    if n < 1024**3:
        return f"{n / 1024**2:.1f} MB"
    return f"{n / 1024**3:.2f} GB"


def enrich_item(cfg: dict, size):
    name_en, desc_en, category_en = TRANSLATIONS_EN.get(
        cfg["path"],
        (cfg["name"], cfg["desc"], cfg["category"]),
    )
    return {
        **cfg,
        "name_en": name_en,
        "desc_en": desc_en,
        "category_en": category_en,
        "size": size,
        "size_formatted": fmt(size, "en"),
        "exists": size is not None,
        "real_path": os.path.expanduser(cfg["path"]),
    }


def scan_paths(configs: Iterable[dict] = PATHS_CONFIG, max_workers=MAX_SCAN_WORKERS):
    configs = list(configs)
    if not configs:
        return []

    def scan_one(cfg):
        return enrich_item(cfg, get_dir_size_bytes(cfg["path"]))

    worker_count = min(max_workers, len(configs))
    items = []
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(scan_one, cfg) for cfg in configs]
        for future in as_completed(futures):
            items.append(future.result())

    items.sort(key=lambda x: x["size"] if x["size"] is not None else 0, reverse=True)
    return items


def _scan_child(entry):
    try:
        size = get_dir_size_bytes(entry.path)
        return {
            "name": entry.name,
            "path": entry.path,
            "is_dir": entry.is_dir(follow_symlinks=False),
            "is_hidden": entry.name.startswith(".") and entry.name not in (".Trash",),
            "size": size,
            "size_formatted": fmt(size, "en"),
        }
    except Exception:
        return None


def browse_dir(path: str, max_workers=MAX_SCAN_WORKERS):
    """List direct children and their sizes, sorted by size descending."""
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return None, "路径不存在"
    if not os.path.isdir(expanded):
        return None, "不是目录"
    try:
        children = sorted(os.scandir(expanded), key=lambda e: e.name)
    except PermissionError:
        return None, "权限不足，无法读取此目录"

    if not children:
        return [], None

    results = []
    worker_count = min(max_workers, len(children))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(_scan_child, child) for child in children]
        for future in as_completed(futures):
            item = future.result()
            if item is not None:
                results.append(item)

    results.sort(key=lambda x: x["size"] if x["size"] is not None else 0, reverse=True)
    return results, None
