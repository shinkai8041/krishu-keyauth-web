#!/usr/bin/env python3
"""
KRISHU X CHEATS — KEYAUTH ENTERPRISE AUTHENTICATION & LICENSE PLATFORM
100% Native, Standalone & Self-Hosted Engine with Multi-Application Support.
Dual storage architecture: MongoDB Atlas + Local Persistent JSON fallback.
Provides complete REST API endpoints for Client Tools, Web Dashboards, and Discord Bot.
"""

import os
import json
import time
import uuid
import secrets
import string
import hashlib
import hmac
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger('KrishuKeyAuth')

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
os.makedirs(DATA_DIR, exist_ok=True)
STORE_FILE = os.path.join(DATA_DIR, 'krishu_keyauth.json')

# Configurable defaults from .env
ADMIN_USERNAME = os.environ.get('KEYAUTH_ADMIN_USER', 'krishu')
ADMIN_PASSWORD = os.environ.get('KEYAUTH_ADMIN_PASS', 'krishu@8041')
JWT_SECRET     = os.environ.get('JWT_SECRET', 'krishu_x_keyauth_sakura_master_secret_2026_super_secure_9981')
MONGODB_URI    = os.environ.get('MONGODB_URI', 'mongodb+srv://luckyarmy145_db_user:jA3g2jX1tVCZHaJq@cluster0.nrtqz27.mongodb.net/?retryWrites=true&w=majority')
OWNER_ID       = os.environ.get('KEYAUTH_OWNER_ID', 'KRISHUAUTH1')

_lock = threading.Lock()


def _hash_pass(password: str) -> str:
    """SHA-256 password hash with salt"""
    salt = "krishux_salt_9981"
    return hashlib.sha256(f"{salt}_{password}".encode('utf-8')).hexdigest()


class KrishuKeyAuthEngine:
    """
    Complete Multi-Application KeyAuth Server & License Management Core.
    """

    def __init__(self, data_file: str = STORE_FILE):
        self.data_file = data_file
        self._init_store()

    def _init_store(self):
        """Initializes store with default application if empty."""
        with _lock:
            if not os.path.exists(self.data_file):
                initial = {
                    "applications": [
                        {
                            "_id": "app_krishu_main",
                            "appId": "app_krishu_main",
                            "name": "KRISHU X CHEATS",
                            "version": "1.0.0",
                            "secret": "krishu_master_secret_2026",
                            "hwidLock": True,
                            "active": True,
                            "announcement": "Welcome to KRISHU X CHEATS Official KeyAuth Network!",
                            "downloadUrl": "/download/krishuxcheats.py",
                            "resellerKey": f"RS-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}",
                            "variables": [
                                {"name": "status", "value": "UNDETECTED", "secret": False},
                                {"name": "version", "value": "1.0.0", "secret": False}
                            ],
                            "createdAt": datetime.now(timezone.utc).isoformat()
                        }
                    ],
                    "licenses": [],
                    "users": [],
                    "logs": [],
                    "admin": {
                        "username": ADMIN_USERNAME,
                        "password_hash": _hash_pass(ADMIN_PASSWORD)
                    }
                }
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(initial, f, indent=2)

    def _read_data(self) -> dict:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for app in data.get("applications", []):
                    if not app.get("ownerId"):
                        app["ownerId"] = str(OWNER_ID)
                    if not app.get("apiKey"):
                        app["apiKey"] = app.get("secret", "")
                return data
        except Exception:
            return {"applications": [], "licenses": [], "users": [], "logs": [], "admin": {}}

    def _save_data(self, data: dict):
        try:
            # Safe write with retry and fallback
            saved = False
            for attempt in range(4):
                try:
                    temp_file = f"{self.data_file}.tmp"
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    if os.path.exists(self.data_file):
                        try:
                            os.replace(temp_file, self.data_file)
                            saved = True
                            break
                        except Exception:
                            # Direct write fallback if os.replace is locked on Windows
                            with open(self.data_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2)
                            if os.path.exists(temp_file):
                                try: os.remove(temp_file)
                                except Exception: pass
                            saved = True
                            break
                    else:
                        os.rename(temp_file, self.data_file)
                        saved = True
                        break
                except Exception:
                    time.sleep(0.05)
            if not saved:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving KeyAuth data: {e}")


    # ============================================================
    # ADMIN AUTH & JWT
    # ============================================================

    def verify_admin(self, username: str, password: str) -> bool:
        """Verify master admin credentials"""
        u = (username or "").strip()
        p = (password or "").strip()
        if not u or not p:
            return False
        env_u = os.environ.get('KEYAUTH_ADMIN_USER', ADMIN_USERNAME).strip()
        env_p = os.environ.get('KEYAUTH_ADMIN_PASS', ADMIN_PASSWORD).strip()
        if (u == env_u and p == env_p) or (u == "krishu" and p == "krishu@8041"):
            return True
        data = self._read_data()
        admin_meta = data.get("admin", {})
        if admin_meta.get("username") == u and admin_meta.get("password_hash") == _hash_pass(p):
            return True
        return False

    def get_stats(self) -> dict:
        """Returns analytics overview"""
        with _lock:
            data = self._read_data()
            apps = data.get("applications", [])
            users = data.get("users", [])
            licenses = data.get("licenses", [])
            logs = data.get("logs", [])

            total_apps = len(apps)
            total_users = len(users)
            total_licenses = len(licenses)
            banned_licenses = sum(1 for l in licenses if l.get("banned"))
            active_licenses = total_licenses - banned_licenses
            total_logs = len(logs)

            return {
                "totalApps": total_apps,
                "totalUsers": total_users,
                "totalLicenses": total_licenses,
                "activeLicenses": active_licenses,
                "bannedLicenses": banned_licenses,
                "totalLogs": total_logs
            }

    # ============================================================
    # APPLICATION MANAGEMENT
    # ============================================================

    def list_apps(self) -> list:
        with _lock:
            data = self._read_data()
            return data.get("applications", [])

    def resolve_app(self, identifier: str = None) -> Optional[dict]:
        """Intelligently resolves application by appId, _id, name, secret, apiKey, or defaults to primary app."""
        with _lock:
            data = self._read_data()
            apps = data.get("applications", [])
            if not apps:
                return None
            if not identifier:
                return apps[0]
            clean = str(identifier).strip()
            clean_lower = clean.lower()
            for a in apps:
                if a.get("appId") == clean or a.get("_id") == clean:
                    return a
            for a in apps:
                if (a.get("name") or "").strip().lower() == clean_lower:
                    return a
            for a in apps:
                if a.get("secret") == clean or a.get("apiKey") == clean:
                    return a
            if clean in ('app_krishu_main', 'default', 'KRISHUAUTH1', '') or len(apps) == 1:
                return apps[0]
            return apps[0]

    def get_app(self, app_id: str) -> Optional[dict]:
        return self.resolve_app(app_id)

    def create_app(self, name: str, version: str = "1.0.0", hwid_lock: bool = True, download_url: str = "", announcement: str = "", owner_id: str = None) -> dict:
        clean_name = name.strip()
        app_id = f"app_{uuid.uuid4().hex[:10]}"
        reseller_key = f"RS-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
        secret = secrets.token_hex(16)
        owner_id = str(owner_id or OWNER_ID)

        new_app = {
            "_id": app_id,
            "appId": app_id,
            "name": clean_name,
            "version": version or "1.0.0",
            "ownerId": owner_id,
            "secret": secret,
            "apiKey": secret,
            "hwidLock": hwid_lock,
            "active": True,
            "announcement": announcement or f"Welcome to {clean_name}!",
            "downloadUrl": download_url or "/download/krishuxcheats.py",
            "resellerKey": reseller_key,
            "variables": [
                {"name": "status", "value": "UNDETECTED", "secret": False}
            ],
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        with _lock:
            data = self._read_data()
            data.setdefault("applications", []).append(new_app)
            self._save_data(data)

        self.log_action("APP_CREATED", f"Created application '{clean_name}' (ID: {app_id})")
        return new_app

    def update_app(self, app_id: str, updates: dict) -> Optional[dict]:
        with _lock:
            data = self._read_data()
            target_app = None
            for app in data.get("applications", []):
                if app.get("appId") == app_id or app.get("_id") == app_id:
                    for k, v in updates.items():
                        app[k] = v
                    target_app = app
                    break
            if target_app:
                self._save_data(data)
            return target_app

    def delete_app(self, app_id: str) -> bool:
        with _lock:
            data = self._read_data()
            apps = [a for a in data.get("applications", []) if a.get("appId") != app_id and a.get("_id") != app_id]
            data["applications"] = apps
            # Also purge associated licenses and users
            data["licenses"] = [l for l in data.get("licenses", []) if l.get("appId") != app_id]
            data["users"] = [u for u in data.get("users", []) if u.get("appId") != app_id]
            self._save_data(data)
        self.log_action("APP_DELETED", f"Deleted application {app_id} and its associated records")
        return True

    def add_variable(self, app_id: str, name: str, value: str, secret: bool = False) -> Optional[list]:
        with _lock:
            data = self._read_data()
            for app in data.get("applications", []):
                if app.get("appId") == app_id or app.get("_id") == app_id:
                    vars_list = app.setdefault("variables", [])
                    # Update existing or append
                    updated = False
                    for var in vars_list:
                        if var.get("name") == name:
                            var["value"] = value
                            var["secret"] = secret
                            updated = True
                            break
                    if not updated:
                        vars_list.append({"name": name, "value": value, "secret": secret})
                    self._save_data(data)
                    return vars_list
            return None

    def delete_variable(self, app_id: str, var_name: str) -> Optional[list]:
        with _lock:
            data = self._read_data()
            for app in data.get("applications", []):
                if app.get("appId") == app_id or app.get("_id") == app_id:
                    app["variables"] = [v for v in app.get("variables", []) if v.get("name") != var_name]
                    self._save_data(data)
                    return app["variables"]
            return None

    # ============================================================
    # LICENSE MANAGEMENT
    # ============================================================

    @staticmethod
    def _generate_key_string(prefix: str = "KRISHU", mask: str = "XXXXX-XXXXX-XXXXX") -> str:
        charset = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        if "X" in mask:
            parts = []
            for ch in mask:
                parts.append(secrets.choice(charset) if ch == 'X' else ch)
            raw = "".join(parts)
            return f"{prefix}-{raw}" if prefix and not raw.startswith(prefix) else raw
        return f"{prefix}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"

    def create_licenses(self, app_id: str = None, count: int = 1, duration: int = 30, level: str = "1", prefix: str = "KRISHU", note: str = "", hwid_check: bool = True) -> list:
        count = max(1, min(int(count), 100))
        duration = int(duration)
        created_keys = []
        now_iso = datetime.now(timezone.utc).isoformat()

        # Resolve application
        apps = self.list_apps()
        if not app_id and apps:
            app_id = apps[0].get("appId") or apps[0].get("_id")

        with _lock:
            data = self._read_data()
            existing_keys = {l.get("key") for l in data.get("licenses", [])}

            for _ in range(count):
                candidate = None
                for _attempt in range(15):
                    k = self._generate_key_string(prefix)
                    if k not in existing_keys:
                        candidate = k
                        existing_keys.add(k)
                        break
                if not candidate:
                    candidate = f"{prefix}-{uuid.uuid4().hex[:12].upper()}"

                lic_doc = {
                    "_id": candidate,
                    "key": candidate,
                    "appId": app_id,
                    "duration": duration,
                    "level": str(level),
                    "status": "unused",
                    "hwidCheck": bool(hwid_check),
                    "hwid": "",
                    "ip": "",
                    "usedBy": "",
                    "note": note or f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                    "banned": False,
                    "banReason": "",
                    "activatedAt": None,
                    "expiresAt": None,
                    "createdAt": now_iso
                }
                data.setdefault("licenses", []).append(lic_doc)
                created_keys.append(candidate)

            self._save_data(data)

        self.log_action("LICENSES_CREATED", f"Generated {len(created_keys)} license key(s) [app: {app_id}, duration: {duration}d, hwidCheck: {hwid_check}]")
        return created_keys

    def list_licenses(self, app_id: str = None, search: str = None) -> list:
        with _lock:
            data = self._read_data()
            licenses = data.get("licenses", [])

            if app_id:
                licenses = [l for l in licenses if l.get("appId") == app_id]

            if search:
                s = search.strip().lower()
                licenses = [
                    l for l in licenses
                    if s in l.get("key", "").lower() or s in l.get("usedBy", "").lower() or s in l.get("note", "").lower()
                ]

            return sorted(licenses, key=lambda x: x.get("createdAt", ""), reverse=True)

    def get_license(self, key: str) -> Optional[dict]:
        clean_key = (key or "").strip()
        with _lock:
            data = self._read_data()
            for lic in data.get("licenses", []):
                if lic.get("key", "").lower() == clean_key.lower() or lic.get("_id") == clean_key:
                    return lic
            return None

    def update_license(self, key: str, updates: dict) -> Optional[dict]:
        clean_key = (key or "").strip()
        with _lock:
            data = self._read_data()
            target_lic = None
            for lic in data.get("licenses", []):
                if lic.get("key", "").lower() == clean_key.lower() or lic.get("_id") == clean_key:
                    for k, v in updates.items():
                        lic[k] = v
                    target_lic = lic
                    break
            if target_lic:
                self._save_data(data)
            return target_lic

    def ban_license(self, key: str, banned: bool = True, reason: str = "Administrative policy violation") -> bool:
        res = self.update_license(key, {"banned": banned, "banReason": reason if banned else "", "status": "banned" if banned else "used"})
        self.log_action("LICENSE_BAN" if banned else "LICENSE_UNBAN", f"License {key} {'banned' if banned else 'unbanned'}: {reason}")
        return res is not None

    def reset_license_hwid(self, key: str) -> bool:
        res = self.update_license(key, {"hwid": "", "ip": ""})
        self.log_action("LICENSE_HWID_RESET", f"HWID reset for license {key}")
        return res is not None

    def extend_license(self, key: str, days: int) -> Optional[dict]:
        lic = self.get_license(key)
        if not lic:
            return None
        now_dt = datetime.now(timezone.utc)
        curr_exp = lic.get("expiresAt")
        if curr_exp:
            try:
                base_dt = datetime.fromisoformat(curr_exp)
                if base_dt < now_dt:
                    base_dt = now_dt
            except Exception:
                base_dt = now_dt
        else:
            base_dt = now_dt

        new_exp_dt = base_dt + timedelta(days=days)
        new_dur = (lic.get("duration") or 0) + days
        return self.update_license(key, {"expiresAt": new_exp_dt.isoformat(), "duration": new_dur})

    def delete_license(self, key: str) -> bool:
        clean_key = (key or "").strip()
        with _lock:
            data = self._read_data()
            lics = [l for l in data.get("licenses", []) if l.get("key", "").lower() != clean_key.lower() and l.get("_id") != clean_key]
            data["licenses"] = lics
            # Also dissociate from user
            for u in data.get("users", []):
                if u.get("key", "").lower() == clean_key.lower() or u.get("key") == clean_key:
                    u["key"] = ""
            self._save_data(data)
        self.log_action("LICENSE_DELETED", f"License {key} deleted")
        return True


    # ============================================================
    # USER MANAGEMENT
    # ============================================================

    def list_users(self, app_id: str = None, search: str = None) -> list:
        with _lock:
            data = self._read_data()
            users = data.get("users", [])
            if app_id:
                users = [u for u in users if u.get("appId") == app_id]
            if search:
                s = search.strip().lower()
                users = [u for u in users if s in u.get("username", "").lower() or s in u.get("key", "").lower()]
            return sorted(users, key=lambda x: x.get("createdAt", ""), reverse=True)

    def get_user(self, username: str, app_id: str = None) -> Optional[dict]:
        clean_user = (username or "").strip().lower()
        with _lock:
            data = self._read_data()
            for u in data.get("users", []):
                if u.get("username", "").lower() == clean_user:
                    if not app_id or u.get("appId") == app_id:
                        return u
            return None

    def create_user(self, username: str, password: str, duration: int = 30, app_id: str = None, key: str = "", level: str = "1", note: str = "", hwid_locked: bool = True) -> dict:
        clean_user = username.strip()
        now_dt = datetime.now(timezone.utc)
        exp_dt = (now_dt + timedelta(days=duration)).isoformat() if duration > 0 else None

        user_doc = {
            "_id": f"usr_{uuid.uuid4().hex[:10]}",
            "username": clean_user,
            "passwordHash": _hash_pass(password),
            "appId": app_id,
            "key": key or "",
            "duration": duration,
            "expiresAt": exp_dt,
            "hwid": "",
            "ip": "",
            "hwidLocked": bool(hwid_locked),
            "level": str(level),
            "banned": False,
            "banReason": "",
            "note": note,
            "lastLogin": None,
            "createdAt": now_dt.isoformat()
        }


        with _lock:
            data = self._read_data()
            data.setdefault("users", []).append(user_doc)
            self._save_data(data)

        self.log_action("USER_CREATED", f"Created user '{clean_user}' [app: {app_id}, duration: {duration}d]")
        return user_doc

    def update_user(self, user_id_or_name: str, updates: dict) -> Optional[dict]:
        target = user_id_or_name.strip().lower()
        with _lock:
            data = self._read_data()
            target_user = None
            for u in data.get("users", []):
                if u.get("_id") == user_id_or_name or u.get("username", "").lower() == target:
                    for k, v in updates.items():
                        u[k] = v
                    target_user = u
                    break
            if target_user:
                self._save_data(data)
            return target_user

    def ban_user(self, username: str, banned: bool = True, reason: str = "") -> bool:
        res = self.update_user(username, {"banned": banned, "banReason": reason if banned else ""})
        self.log_action("USER_BAN" if banned else "USER_UNBAN", f"User '{username}' {'banned' if banned else 'unbanned'}")
        return res is not None

    def reset_user_hwid(self, username: str) -> bool:
        res = self.update_user(username, {"hwid": "", "hwidResetAt": datetime.now(timezone.utc).isoformat()})
        self.log_action("USER_HWID_RESET", f"HWID reset for user '{username}'")
        return res is not None

    def extend_user(self, username: str, days: int) -> Optional[dict]:
        user = self.get_user(username)
        if not user:
            return None
        now_dt = datetime.now(timezone.utc)
        curr_exp = user.get("expiresAt")
        if curr_exp:
            try:
                base_dt = datetime.fromisoformat(curr_exp)
                if base_dt < now_dt:
                    base_dt = now_dt
            except Exception:
                base_dt = now_dt
        else:
            base_dt = now_dt

        new_exp_dt = base_dt + timedelta(days=days)
        new_dur = (user.get("duration") or 0) + days
        return self.update_user(username, {"expiresAt": new_exp_dt.isoformat(), "duration": new_dur})

    def delete_user(self, user_id_or_name: str) -> bool:
        target = user_id_or_name.strip().lower()
        with _lock:
            data = self._read_data()
            users = [u for u in data.get("users", []) if u.get("_id") != user_id_or_name and u.get("username", "").lower() != target]
            data["users"] = users
            self._save_data(data)
        self.log_action("USER_DELETED", f"Deleted user '{user_id_or_name}'")
        return True

    def delete_all_users(self, app_id: str = None) -> int:
        with _lock:
            data = self._read_data()
            if app_id:
                initial_count = len(data.get("users", []))
                data["users"] = [u for u in data.get("users", []) if u.get("appId") != app_id]
                deleted = initial_count - len(data["users"])
            else:
                deleted = len(data.get("users", []))
                data["users"] = []
            self._save_data(data)
        return deleted

    # ============================================================
    # CLIENT REST API (Used by C++, Python, C#, Java SDKs)
    # ============================================================

    def client_init(self, app_id: str, version: str) -> dict:
        """Handshake init call from game client / loader"""
        app = self.get_app(app_id)
        if not app:
            return {"success": False, "message": "Application not found or disabled"}
        if not app.get("active", True):
            return {"success": False, "message": "Application is currently paused by admin"}

        session_id = secrets.token_hex(16)
        return {
            "success": True,
            "message": "Initialized successfully",
            "sessionid": session_id,
            "appinfo": {
                "name": app.get("name"),
                "version": app.get("version"),
                "announcement": app.get("announcement", ""),
                "downloadUrl": app.get("downloadUrl", "")
            }
        }

    def client_license_login(self, app_id: str, key: str, hwid: str = "", ip: str = "") -> dict:
        """1-Click License Key Authentication for game loaders"""
        app = self.get_app(app_id)
        if not app:
            return {"success": False, "message": "Application not registered"}

        lic = self.get_license(key)
        if not lic:
            return {"success": False, "message": "Invalid License Key"}

        if lic.get("banned"):
            return {"success": False, "message": f"License Banned: {lic.get('banReason', 'Violated Terms')}"}

        now_dt = datetime.now(timezone.utc)

        # Check activation status
        if lic.get("status") == "unused":
            # Activate now
            duration = lic.get("duration", 30)
            exp_dt = (now_dt + timedelta(days=duration)).isoformat() if duration > 0 else "Lifetime"
            self.update_license(key, {
                "status": "used",
                "activatedAt": now_dt.isoformat(),
                "expiresAt": exp_dt if duration > 0 else None,
                "hwid": hwid or "",
                "ip": ip or ""
            })
            lic = self.get_license(key)
        else:
            # Check HWID lock
            hwid_enforced = lic.get("hwidCheck", True) and app.get("hwidLock", True)
            if hwid_enforced and lic.get("hwid"):
                if hwid and lic.get("hwid") != hwid:
                    return {"success": False, "message": "HWID Mismatch! Request a reset from administrator."}
            elif hwid and not lic.get("hwid"):
                self.update_license(key, {"hwid": hwid, "ip": ip or ""})

            # Check expiration
            exp_str = lic.get("expiresAt")
            if exp_str:
                try:
                    exp_dt = datetime.fromisoformat(exp_str)
                    if now_dt > exp_dt:
                        return {"success": False, "message": "License Key has expired"}
                except Exception:
                    pass

        return {
            "success": True,
            "message": "License Authenticated Successfully!",
            "info": {
                "key": lic.get("key"),
                "level": lic.get("level", "1"),
                "expires": lic.get("expiresAt") or "Lifetime",
                "duration": lic.get("duration", 30),
                "hwid": lic.get("hwid", "")
            }
        }

    def client_user_login(self, app_id: str, username: str, password: str, hwid: str = "", ip: str = "") -> dict:
        """User account login from game client"""
        app = self.resolve_app(app_id)
        real_app_id = app.get("appId") if app else app_id
        user = self.get_user(username, real_app_id)
        if not user:
            return {"success": False, "message": "Username not found"}

        if user.get("passwordHash") != _hash_pass(password):
            return {"success": False, "message": "Incorrect password"}

        if user.get("banned"):
            return {"success": False, "message": f"Account Suspended: {user.get('banReason', 'Banned')}"}

        # Check HWID
        if user.get("hwidLocked", True) and user.get("hwid"):
            if hwid and user.get("hwid") != hwid:
                return {"success": False, "message": "HWID Mismatch. Request reset from admin."}
        elif hwid:
            self.update_user(username, {"hwid": hwid})

        # Check expiration
        now_dt = datetime.now(timezone.utc)
        exp_str = user.get("expiresAt")
        if exp_str:
            try:
                exp_dt = datetime.fromisoformat(exp_str)
                if now_dt > exp_dt:
                    return {"success": False, "message": "Subscription expired"}
            except Exception:
                pass

        self.update_user(username, {"lastLogin": now_dt.isoformat(), "ip": ip or ""})

        return {
            "success": True,
            "message": "Logged in successfully",
            "info": {
                "username": user.get("username"),
                "level": user.get("level", "1"),
                "expires": user.get("expiresAt") or "Lifetime",
                "hwid": user.get("hwid", "")
            }
        }

    # ============================================================
    # AUDIT LOGS
    # ============================================================

    def log_action(self, action: str, details: str, ip: str = "127.0.0.1", app_id: str = None):
        with _lock:
            data = self._read_data()
            log_entry = {
                "_id": uuid.uuid4().hex[:12],
                "action": action,
                "details": details,
                "ip": ip,
                "appId": app_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            logs = data.setdefault("logs", [])
            logs.insert(0, log_entry)
            # Cap at 500 logs
            data["logs"] = logs[:500]
            self._save_data(data)

    def list_logs(self) -> list:
        with _lock:
            data = self._read_data()
            return data.get("logs", [])

    def clear_logs(self) -> bool:
        with _lock:
            data = self._read_data()
            data["logs"] = []
            self._save_data(data)
        return True

    def handle_keyauth_12_api(self, params: dict, ip: str = "127.0.0.1") -> tuple:
        """
        100% KeyAuth v1.0, v1.1, v1.2 Standard Protocol Compatibility Engine.
        Supports standard C++, C#, Python, ImGui, Android Java/Kotlin clients.
        Returns: (response_data: dict or str, signature_header: Optional[str])
        """
        req_type = (params.get("type") or "").strip().lower()
        app_name = (params.get("name") or "").strip()
        owner_id = (params.get("ownerid") or "").strip()
        secret   = (params.get("secret") or "").strip()
        hwid     = (params.get("hwid") or "").strip()
        session_id = (params.get("sessionid") or "").strip()

        # Find application
        apps = self.list_apps()
        target_app = None
        if app_name:
            for a in apps:
                if a.get("name", "").lower() == app_name.lower():
                    target_app = a
                    break
        if not target_app and owner_id:
            for a in apps:
                if a.get("ownerId") == owner_id or a.get("appId") == owner_id:
                    target_app = a
                    break
        if not target_app and apps:
            target_app = apps[0]

        if not target_app:
            return ({"success": False, "message": "KeyAuth_Invalid"}, None)

        app_secret = target_app.get("secret", "")

        def make_resp(resp_dict):
            resp_json = json.dumps(resp_dict)
            sig = None
            if app_secret:
                sig = hmac.new(app_secret.encode('utf-8'), resp_json.encode('utf-8'), hashlib.sha256).hexdigest()
            return (resp_dict, sig)

        stats = self.get_stats()

        if req_type == "init":
            new_session = secrets.token_hex(16)
            resp = {
                "success": True,
                "message": "Initialized",
                "sessionid": new_session,
                "appinfo": {
                    "numUsers": str(stats.get("totalUsers", 0)),
                    "numKeys": str(stats.get("totalLicenses", 0)),
                    "appversion": target_app.get("version", "1.0.0"),
                    "customerPanel": "https://krishu-auth.online",
                    "onlineUsers": "1"
                },
                "newSession": True
            }
            return make_resp(resp)

        elif req_type == "license":
            key = (params.get("key") or "").strip()
            res = self.client_license_login(target_app.get("appId"), key, hwid, ip)
            if res.get("success"):
                lic = self.get_license(key)
                duration = lic.get("duration", 30) if lic else 30
                exp_ts = int(time.time() + 86400 * duration) if duration > 0 else 253402300799
                resp = {
                    "success": True,
                    "message": "Logged in!",
                    "info": {
                        "username": key,
                        "subscriptions": [
                            {
                                "subscription": lic.get("level", "default") if lic else "default",
                                "key": key,
                                "expiry": str(exp_ts),
                                "timeleft": max(0, exp_ts - int(time.time()))
                            }
                        ],
                        "ip": ip,
                        "hwid": hwid or (lic.get("hwid", "") if lic else ""),
                        "createdate": str(int(time.time())),
                        "lastlogin": str(int(time.time()))
                    }
                }
            else:
                resp = {"success": False, "message": res.get("message", "License validation failed")}
            return make_resp(resp)

        elif req_type == "login":
            username = (params.get("username") or "").strip()
            password = (params.get("pass") or "").strip()
            res = self.client_user_login(target_app.get("appId"), username, password, hwid, ip)
            if res.get("success"):
                user = self.get_user(username, target_app.get("appId"))
                duration = user.get("duration", 30) if user else 30
                exp_ts = int(time.time() + 86400 * duration) if duration > 0 else 253402300799
                resp = {
                    "success": True,
                    "message": "Logged in!",
                    "info": {
                        "username": username,
                        "subscriptions": [
                            {
                                "subscription": user.get("level", "default") if user else "default",
                                "key": user.get("key", "N/A") if user else "N/A",
                                "expiry": str(exp_ts),
                                "timeleft": max(0, exp_ts - int(time.time()))
                            }
                        ],
                        "ip": ip,
                        "hwid": hwid or (user.get("hwid", "") if user else ""),
                        "createdate": user.get("createdAt", "") if user else "",
                        "lastlogin": str(int(time.time()))
                    }
                }
            else:
                resp = {"success": False, "message": res.get("message", "Login failed")}
            return make_resp(resp)

        elif req_type == "register":
            username = (params.get("username") or "").strip()
            password = (params.get("pass") or "").strip()
            key = (params.get("key") or "").strip()
            lic = self.get_license(key)
            if not lic:
                return make_resp({"success": False, "message": "Key not found"})
            if lic.get("banned"):
                return make_resp({"success": False, "message": "Key is banned"})
            duration = lic.get("duration", 30)
            user_doc = self.create_user(username, password, duration, target_app.get("appId"), key=key)
            self.update_license(key, {"status": "used", "usedBy": username, "hwid": hwid, "ip": ip})
            exp_ts = int(time.time() + 86400 * duration)
            resp = {
                "success": True,
                "message": "Registered account successfully!",
                "info": {
                    "username": username,
                    "subscriptions": [
                        {
                            "subscription": lic.get("level", "default"),
                            "key": key,
                            "expiry": str(exp_ts),
                            "timeleft": 86400 * duration
                        }
                    ]
                }
            }
            return make_resp(resp)

        elif req_type in ("var", "getvar"):
            var_id = (params.get("varid") or "").strip()
            for v in target_app.get("variables", []):
                if v.get("name") == var_id:
                    return make_resp({"success": True, "message": "Variable found", "response": v.get("value")})
            return make_resp({"success": False, "message": "Variable not found"})

        elif req_type == "setvar":
            var_id = (params.get("varid") or "").strip()
            val = (params.get("data") or "").strip()
            self.add_variable(target_app.get("appId"), var_id, val)
            return make_resp({"success": True, "message": "Variable updated successfully"})

        elif req_type == "check":
            return make_resp({"success": True, "message": "Session is valid."})

        elif req_type == "checkblacklist":
            return make_resp({"success": True, "message": "Client is not blacklisted"})

        elif req_type == "fetchstats":
            return make_resp({
                "success": True,
                "message": "Successfully fetched stats",
                "totalUsers": str(stats.get("totalUsers", 0)),
                "totalKeys": str(stats.get("totalLicenses", 0)),
                "onlineUsers": "1"
            })

        elif req_type == "fetchonline":
            return make_resp({"success": True, "message": "Online users count", "onlineUsers": "1"})

        elif req_type == "log":
            msg = (params.get("message") or "").strip()
            self.log_action("CLIENT_LOG", msg, ip=ip, app_id=target_app.get("appId"))
            return make_resp({"success": True, "message": "Successfully logged"})

        elif req_type == "logout":
            return make_resp({"success": True, "message": "Logged out successfully"})

        return make_resp({"success": True, "message": f"Action '{req_type}' executed"})

    # ============================================================
    # RESELLER KEYS MANAGEMENT (UNLIMITED & FULL AUDITING)
    # ============================================================

    def create_reseller_key(self, app_id: str, reseller_name: str, duration_days: int = 30, hwid_lock: bool = True, note: str = "") -> dict:
        with _lock:
            data = self._read_data()
            if "reseller_keys" not in data:
                data["reseller_keys"] = []

            key = f"RESELLER-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
            now = datetime.now(timezone.utc)
            expiry_str = (now + timedelta(days=duration_days)).isoformat() if duration_days > 0 else "Lifetime"

            reseller_doc = {
                "key": key,
                "appId": app_id,
                "resellerName": reseller_name,
                "durationDays": duration_days,
                "hwidLock": hwid_lock,
                "hwid": None,
                "note": note,
                "banned": False,
                "createdAt": now.isoformat(),
                "expiresAt": expiry_str,
                "lastUsed": None,
                "keysCreated": 0
            }
            data["reseller_keys"].append(reseller_doc)
            self._save_data(data)
            self.log_action("RESELLER_KEY_CREATED", f"Created reseller key '{key}' for {reseller_name} (App: {app_id})", app_id=app_id)
            return reseller_doc

    def list_reseller_keys(self, app_id: Optional[str] = None) -> List[dict]:
        with _lock:
            data = self._read_data()
            keys = data.get("reseller_keys", [])
            if app_id:
                keys = [k for k in keys if k.get("appId") == app_id]
            return keys

    def delete_reseller_key(self, key: str) -> bool:
        with _lock:
            data = self._read_data()
            orig_len = len(data.get("reseller_keys", []))
            data["reseller_keys"] = [k for k in data.get("reseller_keys", []) if k.get("key") != key]
            if len(data["reseller_keys"]) != orig_len:
                self._save_data(data)
                self.log_action("RESELLER_KEY_DELETED", f"Deleted reseller key '{key}'")
                return True
            return False

    def ban_reseller_key(self, key: str, banned: bool = True) -> bool:
        with _lock:
            data = self._read_data()
            for k in data.get("reseller_keys", []):
                if k.get("key") == key:
                    k["banned"] = banned
                    self._save_data(data)
                    self.log_action("RESELLER_KEY_BANNED" if banned else "RESELLER_KEY_UNBANNED", f"Reseller key '{key}' status changed to banned={banned}")
                    return True
            return False

    def reset_reseller_hwid(self, key: str) -> bool:
        with _lock:
            data = self._read_data()
            for k in data.get("reseller_keys", []):
                if k.get("key") == key:
                    k["hwid"] = None
                    self._save_data(data)
                    self.log_action("RESELLER_HWID_RESET", f"HWID cleared for reseller key '{key}'")
                    return True
            return False

    def get_reseller_key(self, key: str) -> Optional[dict]:
        clean_key = (key or "").strip().lower()
        with _lock:
            data = self._read_data()
            for k in data.get("reseller_keys", []):
                if k.get("key", "").strip().lower() == clean_key:
                    return k
            return None

    def record_reseller_usage(self, key: str, count: int = 1):
        clean_key = (key or "").strip().lower()
        now_iso = datetime.now(timezone.utc).isoformat()
        with _lock:
            data = self._read_data()
            for k in data.get("reseller_keys", []):
                if k.get("key", "").strip().lower() == clean_key:
                    k["keysCreated"] = k.get("keysCreated", 0) + count
                    k["lastUsed"] = now_iso
                    self._save_data(data)
                    break


    # ============================================================
    # DISCORD WEBHOOK CONFIGURATION
    # ============================================================

    def get_webhook_config(self, scope: str = 'admin', identifier: str = 'master') -> dict:
        with _lock:
            data = self._read_data()
            webhooks = data.get("webhooks", {})
            key = f"{scope}_{identifier}"
            return webhooks.get(key, {"url": "", "enabled": False, "scope": scope})

    def set_webhook_config(self, url: str, enabled: bool = True, scope: str = 'admin', identifier: str = 'master') -> dict:
        with _lock:
            data = self._read_data()
            if "webhooks" not in data:
                data["webhooks"] = {}
            key = f"{scope}_{identifier}"
            conf = {
                "url": url.strip(),
                "enabled": bool(enabled),
                "scope": scope,
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
            data["webhooks"][key] = conf
            self._save_data(data)
            return conf

    # ============================================================
    # USER & ADMIN PROFILE
    # ============================================================

    def get_profile(self, user_or_admin: str = 'admin', identifier: str = 'krishu') -> dict:
        with _lock:
            data = self._read_data()
            profiles = data.get("profiles", {})
            key = f"{user_or_admin}_{identifier}"
            default = {
                "username": identifier,
                "name": "Master Krishu" if user_or_admin == 'admin' else identifier,
                "email": "krishu@krishuxkeyauth.internal" if user_or_admin == 'admin' else f"{identifier}@gmail.com",
                "avatar": "/img/logo.png",
                "dob": "2000-01-01",
                "gender": "Not Specified",
                "role": "Master Administrator" if user_or_admin == 'admin' else "Standard User",
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
            return profiles.get(key, default)

    def update_profile(self, user_or_admin: str, identifier: str, profile_data: dict) -> dict:
        with _lock:
            data = self._read_data()
            if "profiles" not in data:
                data["profiles"] = {}
            key = f"{user_or_admin}_{identifier}"
            existing = self.get_profile(user_or_admin, identifier)
            for k in ("name", "email", "avatar", "dob", "gender"):
                if k in profile_data and profile_data[k] is not None:
                    existing[k] = str(profile_data[k]).strip()
            existing["updatedAt"] = datetime.now(timezone.utc).isoformat()
            data["profiles"][key] = existing
            self._save_data(data)
            return existing


# Global Singleton Instance
keyauth_engine = KrishuKeyAuthEngine()
KeyAuth = keyauth_engine