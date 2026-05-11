"""
Brand Strategy — 统一密钥管理
使用系统原生 Keychain（keyring 库）：
  Windows → Windows Credential Manager
  macOS   → macOS Keychain

跨平台，换机只需重新 import_secrets.py 导入一次。

依赖：pip install keyring

用法：
  # 存入
  python lib/secrets.py set KAIWEETS_SHOPIFY_TOKEN shpat_xxx

  # 读取（脚本内调用）
  from lib.secrets import get_secret
  token = get_secret("KAIWEETS_SHOPIFY_TOKEN")

  # 列出所有 key
  python lib/secrets.py list
"""

import os
import sys
from pathlib import Path

_SERVICE = "brand-strategy"
_INDEX_FILE = Path(__file__).parent.parent / "data" / "secrets_index.json"


def _kr():
    try:
        import keyring
        return keyring
    except ImportError:
        print("需要先安装：pip install keyring（或 pip3 install keyring）", file=sys.stderr)
        sys.exit(1)


def _load_index() -> list:
    """维护一个 key 名称列表（keyring 本身不支持枚举）。"""
    if _INDEX_FILE.exists():
        import json
        return json.loads(_INDEX_FILE.read_text(encoding="utf-8"))
    return []


def _save_index(keys: list):
    import json
    _INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    _INDEX_FILE.write_text(json.dumps(sorted(set(keys)), indent=2), encoding="utf-8")


def set_secret(key: str, value: str):
    _kr().set_password(_SERVICE, key, value)
    keys = _load_index()
    if key not in keys:
        keys.append(key)
        _save_index(keys)
    print(f"[secrets] {key} 已存入 Keychain")


def _dpapi_get(key: str):
    """从旧 secrets.enc（DPAPI）读取，仅 Windows 可用，迁移期间回退用。"""
    if sys.platform != "win32":
        return None
    import json, base64
    from pathlib import Path
    store_file = Path(__file__).parent.parent / "data" / "secrets.enc"
    if not store_file.exists():
        return None
    store = json.loads(store_file.read_text(encoding="utf-8"))
    if key not in store:
        return None
    try:
        import win32crypt
        raw = base64.b64decode(store[key])
        _, decrypted = win32crypt.CryptUnprotectData(raw, None, None, None, 0)
        return decrypted.decode("utf-8")
    except Exception:
        return None


def get_secret(key: str, fallback_env: bool = True) -> str:
    """读取密钥。优先 Keychain → DPAPI 旧存储 → 环境变量。"""
    value = _kr().get_password(_SERVICE, key)
    if value is not None:
        return value
    # 迁移期间回退：尝试旧 DPAPI 存储（仅 Windows）
    dpapi_val = _dpapi_get(key)
    if dpapi_val is not None:
        return dpapi_val
    if fallback_env:
        val = os.getenv(key, "")
        if val:
            return val
    raise KeyError(f"[secrets] 找不到密钥: {key}（Keychain / DPAPI / 环境变量均无记录）")


def list_keys():
    keyring_keys = set(_load_index())
    # 也列出旧 DPAPI 存储的 key（迁移期间兼容）
    import json
    from pathlib import Path
    store_file = Path(__file__).parent.parent / "data" / "secrets.enc"
    dpapi_keys = set(json.loads(store_file.read_text(encoding="utf-8")).keys()) if store_file.exists() else set()
    all_keys = sorted(keyring_keys | dpapi_keys)
    if not all_keys:
        print("（暂无存储的密钥）")
        return
    for k in all_keys:
        src = []
        if k in keyring_keys:
            src.append("keychain")
        if k in dpapi_keys:
            src.append("dpapi")
        print(f"  {k}  [{', '.join(src)}]")


def refresh_shopify_token(brand: str) -> str:
    """用 client_credentials 换取新 Shopify token，自动存储并返回。
    要求 secrets 中存有 {BRAND}_SHOPIFY_CLIENT_ID 和 {BRAND}_SHOPIFY_CLIENT_SECRET。
    token 有效期约 24 小时（expires_in ≈ 86400）。
    """
    import urllib.request, urllib.parse, json as _json, time as _time

    brand = brand.upper()
    client_id = get_secret(f"{brand}_SHOPIFY_CLIENT_ID")
    client_secret = get_secret(f"{brand}_SHOPIFY_CLIENT_SECRET")
    store_host = get_secret(f"{brand}_SHOPIFY_STORE")

    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()

    req = urllib.request.Request(
        f"https://{store_host}/admin/oauth/access_token",
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = _json.loads(r.read())

    token = resp["access_token"]
    expires_in = resp.get("expires_in", 86400)
    expires_at = int(_time.time()) + expires_in - 300  # 提前5分钟续期

    set_secret(f"{brand}_SHOPIFY_TOKEN", token)
    set_secret(f"{brand}_SHOPIFY_TOKEN_EXPIRES", str(expires_at))
    return token


def get_shopify_token(brand: str) -> str:
    """返回有效的 Shopify token，过期时自动刷新。"""
    import time as _time

    brand = brand.upper()
    try:
        expires_at = int(get_secret(f"{brand}_SHOPIFY_TOKEN_EXPIRES"))
        token = get_secret(f"{brand}_SHOPIFY_TOKEN")
        if _time.time() < expires_at:
            return token
    except (KeyError, ValueError):
        pass
    return refresh_shopify_token(brand)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args or args[0] == "list":
        list_keys()
    elif args[0] == "set" and len(args) == 3:
        set_secret(args[1], args[2])
    elif args[0] == "get" and len(args) == 2:
        print(get_secret(args[1]))
    else:
        print("用法:")
        print("  python lib/secrets.py set KEY VALUE")
        print("  python lib/secrets.py get KEY")
        print("  python lib/secrets.py list")
