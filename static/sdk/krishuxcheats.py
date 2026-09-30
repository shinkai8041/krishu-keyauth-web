"""
Krishu X Cheats — High-Performance Zero-Dependency Python SDK
Single file drop-in authentication module.
Compatible with Python 3.7+ (Windows, Linux, macOS)
NO PIP PACKAGES REQUIRED!
"""

import sys
import platform
import hashlib
import json
import urllib.request
import urllib.error
import uuid

class api:
    def __init__(self, name: str, ownerid: str, secret: str, version: str, api_url: str = "http://localhost:3000/api/v1"):
        self.name = str(name or "")
        self.ownerid = str(ownerid or "")
        self.secret = str(secret or "")
        self.version = str(version or "1.0.0")
        self.api_url = str(api_url or "http://localhost:3000/api/v1").rstrip('/')
        
        self.initialized = False
        self.response = {"success": False, "message": ""}
        self.user_data = {
            "username": "",
            "level": "",
            "expires": "",
            "lifetime": False,
            "hwid": "",
            "token": ""
        }
        self.app_data = {
            "name": "",
            "version": "",
            "announcement": "",
            "downloadUrl": ""
        }

    @staticmethod
    def get_hwid() -> str:
        """Returns unique system hardware fingerprint without external subprocesses."""
        if platform.system() == "Windows":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                    guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                    if guid:
                        return str(guid).strip()
            except Exception:
                pass

        try:
            node = uuid.getnode()
            raw = f"{platform.node()}-{platform.machine()}-{platform.processor()}-{node}"
            return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:32]
        except Exception:
            return "HWID-PY-GENERIC"

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.api_url}{endpoint}"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "x-api-key": self.secret,
                "x-owner-id": self.ownerid,
                "x-app-name": self.name,
                "User-Agent": "KrishuXCheats-Python/1.0"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                res_body = response.read().decode('utf-8')
                return json.loads(res_body)
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                return json.loads(err_body)
            except Exception:
                return {"success": False, "message": f"HTTP Error {e.code}: {e.reason}"}
        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}

    def _get(self, endpoint: str) -> dict:
        url = f"{self.api_url}{endpoint}"
        req = urllib.request.Request(
            url,
            headers={
                "x-api-key": self.secret,
                "x-owner-id": self.ownerid,
                "x-app-name": self.name,
                "User-Agent": "KrishuXCheats-Python/1.0"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {"success": False, "message": str(e)}

    def init(self) -> bool:
        """Handshake with Krishu X Cheats auth server."""
        payload = {
            "name": self.name,
            "ownerid": self.ownerid,
            "secret": self.secret,
            "version": self.version
        }
        res = self._post("/init", payload)
        succ = res.get("success", False)
        self.response["success"] = succ
        self.response["message"] = res.get("message", "Init completed" if succ else "Init failed")

        if succ:
            self.initialized = True
            app_info = res.get("app", {})
            self.app_data["name"] = res.get("name") or app_info.get("name", self.name)
            self.app_data["version"] = res.get("version") or app_info.get("version", self.version)
            self.app_data["announcement"] = res.get("announcement") or app_info.get("announcement", "")
            self.app_data["downloadUrl"] = res.get("downloadUrl") or app_info.get("downloadUrl", "")
            return True
        return False

    def login(self, username: str, password: str) -> bool:
        """Login user credentials and verify HWID & expiration."""
        if not self.initialized:
            self.response = {"success": False, "message": "Please initialize API before calling login()"}
            return False

        hwid = self.get_hwid()
        payload = {
            "name": self.name,
            "ownerid": self.ownerid,
            "secret": self.secret,
            "username": username,
            "password": password,
            "hwid": hwid
        }

        res = self._post("/login", payload)
        succ = res.get("success", False)
        self.response["success"] = succ
        self.response["message"] = res.get("message", "Login response")

        if succ:
            info = res.get("info", {})
            self.user_data["username"] = res.get("username") or info.get("username", username)
            self.user_data["level"] = res.get("level") or info.get("level", "Default")
            exp = res.get("expiresAt") or info.get("expiresAt")
            self.user_data["expires"] = str(exp or "Lifetime")
            self.user_data["lifetime"] = res.get("lifetime") or info.get("lifetime", self.user_data["expires"] == "Lifetime")
            self.user_data["hwid"] = res.get("hwid") or info.get("hwid", "")
            self.user_data["token"] = res.get("token", "")
            return True
        return False

    def register(self, username: str, password: str, license_key: str) -> bool:
        """Register a new account with a license key."""
        if not self.initialized:
            self.response = {"success": False, "message": "Please initialize API before calling register()"}
            return False

        hwid = self.get_hwid()
        payload = {
            "name": self.name,
            "ownerid": self.ownerid,
            "secret": self.secret,
            "username": username,
            "password": password,
            "licenseKey": license_key,
            "hwid": hwid
        }

        res = self._post("/register", payload)
        succ = res.get("success", False)
        self.response["success"] = succ
        self.response["message"] = res.get("message", "Registration response")

        if succ:
            self.user_data["username"] = res.get("username", username)
            self.user_data["level"] = res.get("level", "Default")
            self.user_data["expires"] = str(res.get("expiresAt") or "Lifetime")
            self.user_data["token"] = res.get("token", "")
            return True
        return False

    def license(self, license_key: str) -> bool:
        """1-Click license key only authentication."""
        if not self.initialized:
            self.response = {"success": False, "message": "Please initialize API before calling license()"}
            return False

        hwid = self.get_hwid()
        payload = {
            "name": self.name,
            "ownerid": self.ownerid,
            "secret": self.secret,
            "key": license_key,
            "hwid": hwid
        }

        res = self._post("/license", payload)
        succ = res.get("success", False)
        self.response["success"] = succ
        self.response["message"] = res.get("message", "License response")

        if succ:
            self.user_data["username"] = license_key
            self.user_data["level"] = res.get("level", "Default")
            self.user_data["expires"] = str(res.get("expiresAt") or "Lifetime")
            self.user_data["token"] = res.get("token", "")
            return True
        return False

    def getvar(self, var_name: str) -> str:
        """Fetch remote server variable securely."""
        res = self._get(f"/var/{var_name}")
        if res.get("success"):
            return str(res.get("value", ""))
        return ""
