"""
Accounts Domain Model and IAS Synchronization Service for SIR Minecraft Ecosystem.

Implements:
- Bi-Modal Account Architecture (Microsoft OAuth 2.0 PKCE + Offline IAS UUIDv5)
- Offline UUIDv5 deterministic generation: uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}")
- In-game ias_accounts.json propagation across root and instance directories
- Local accounts.json persistence and state caching
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

try:
    from shared_core.runtime import atomic_write_json
except ImportError:
    def atomic_write_json(path: str, value: Any) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as h:
            json.dump(value, h, indent=2, ensure_ascii=False)
        os.replace(temp, path)


def generate_offline_uuid(username: str) -> str:
    """Generates deterministic UUIDv5 for offline Minecraft accounts matching Notchian offline spec."""
    clean_user = str(username or "Player").strip()
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{clean_user}"))


@dataclass
class Account:
    """Standard account representation across SIR ecosystem."""
    accountId: str
    displayName: str
    accountType: str = "offline"  # "offline" or "microsoft"
    uuid: str = ""
    prismProfileId: str = ""
    skinUrl: str = ""
    model: str = "classic"  # "classic" or "slim"
    active: bool = False
    needsRelink: bool = False
    updatedAt: str = ""

    def __post_init__(self):
        if not self.uuid:
            self.uuid = generate_offline_uuid(self.displayName)
        if not self.skinUrl:
            self.skinUrl = f"https://mc-heads.net/skin/{self.displayName}"
        if not self.accountId:
            digest = hashlib.sha256(f"sir:{self.accountType}:{self.displayName.lower()}".encode("utf-8")).hexdigest()[:24]
            self.accountId = f"sir-{digest}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_ias_dict(self) -> Dict[str, Any]:
        return {
            "name": self.displayName,
            "type": self.accountType,
            "uuid": self.uuid,
            "skinUrl": self.skinUrl,
            "model": self.model
        }


class AccountsManager:
    """Manages persistent accounts, Microsoft OAuth PKCE credentials, and in-game IAS sync."""

    SCHEMA_VERSION = 1

    def __init__(self, data_dir: str):
        self.data_dir = os.path.abspath(data_dir)
        self.accounts_file = os.path.join(self.data_dir, "accounts.json")
        self.ias_file = os.path.join(self.data_dir, "ias_accounts.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self.accounts: List[Account] = self.load_accounts()
        self.active_account_id: str = self._load_active_id()

    def _load_active_id(self) -> str:
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as h:
                    raw = json.load(h)
                if isinstance(raw, dict) and raw.get("activeAccountId"):
                    return str(raw["activeAccountId"])
            except Exception:
                pass
        for acc in self.accounts:
            if acc.active:
                return acc.accountId
        return self.accounts[0].accountId if self.accounts else ""

    def load_accounts(self) -> List[Account]:
        """Loads accounts from accounts.json with schema validation."""
        if not os.path.exists(self.accounts_file):
            return []
        try:
            with open(self.accounts_file, "r", encoding="utf-8") as h:
                raw = json.load(h)
            items = raw.get("accounts", []) if isinstance(raw, dict) else raw
            accounts: List[Account] = []
            for item in items:
                if isinstance(item, dict) and item.get("displayName"):
                    name = str(item["displayName"]).strip()
                    acc_type = str(item.get("accountType") or item.get("type") or "offline")
                    raw_uuid = str(item.get("uuid") or generate_offline_uuid(name))
                    accounts.append(Account(
                        accountId=str(item.get("accountId") or ""),
                        displayName=name,
                        accountType=acc_type,
                        uuid=raw_uuid,
                        prismProfileId=str(item.get("prismProfileId") or ""),
                        skinUrl=str(item.get("skinUrl") or f"https://mc-heads.net/skin/{name}"),
                        model=str(item.get("model") or "classic"),
                        active=bool(item.get("active", False)),
                        needsRelink=bool(item.get("needsRelink", False)),
                        updatedAt=str(item.get("updatedAt") or "")
                    ))
            return accounts
        except Exception:
            return []

    def save_accounts(self) -> None:
        """Persists accounts and activeAccountId atomically to accounts.json."""
        payload = {
            "schemaVersion": self.SCHEMA_VERSION,
            "activeAccountId": self.active_account_id,
            "accounts": [acc.to_dict() for acc in self.accounts]
        }
        atomic_write_json(self.accounts_file, payload)
        self.sync_to_ingame_ias()

    def sync_to_ingame_ias(self) -> None:
        """Propagates ias_accounts.json compatibility format to root and all instance directories."""
        active_acc = next((a for a in self.accounts if a.accountId == self.active_account_id), None)
        active_name = active_acc.displayName if active_acc else (self.accounts[0].displayName if self.accounts else "Player")

        ias_payload = {
            "schemaVersion": 1,
            "active": active_name,
            "accounts": [acc.to_ias_dict() for acc in self.accounts]
        }
        atomic_write_json(self.ias_file, ias_payload)

        # Propagate to instances subdirectories
        instances_dir = self.data_dir
        if os.path.exists(instances_dir):
            for entry in os.listdir(instances_dir):
                entry_path = os.path.join(instances_dir, entry)
                if os.path.isdir(entry_path) and not entry.startswith("."):
                    mc_dir = os.path.join(entry_path, "minecraft")
                    if os.path.isdir(mc_dir):
                        atomic_write_json(os.path.join(mc_dir, "ias_accounts.json"), ias_payload)
                    if os.path.exists(os.path.join(entry_path, "mmc-pack.json")) or os.path.exists(os.path.join(entry_path, "instance.cfg")):
                        atomic_write_json(os.path.join(entry_path, "ias_accounts.json"), ias_payload)

    def add_offline_account(self, username: str, skin_url: str = "", model: str = "classic") -> Dict[str, Any]:
        """Creates or switches to an offline account with deterministic UUIDv5."""
        clean_name = str(username or "").strip()
        if not clean_name or len(clean_name) < 2 or len(clean_name) > 16:
            return {"success": False, "error": "Username must be between 2 and 16 characters."}
        if not re.match(r"^[a-zA-Z0-9_]+$", clean_name):
            return {"success": False, "error": "Username contains invalid characters. Use letters, numbers, and underscores only."}

        existing = next((a for a in self.accounts if a.displayName.lower() == clean_name.lower()), None)
        if existing:
            self.active_account_id = existing.accountId
            for a in self.accounts:
                a.active = (a.accountId == existing.accountId)
            self.save_accounts()
            return {"success": True, "account": existing.to_dict(), "message": f"Switched to offline profile '{clean_name}'."}

        new_acc = Account(
            accountId="",
            displayName=clean_name,
            accountType="offline",
            uuid=generate_offline_uuid(clean_name),
            skinUrl=skin_url or f"https://mc-heads.net/skin/{clean_name}",
            model=model,
            active=True
        )
        for a in self.accounts:
            a.active = False
        self.accounts.append(new_acc)
        self.active_account_id = new_acc.accountId
        self.save_accounts()
        return {"success": True, "account": new_acc.to_dict(), "message": f"Created offline profile '{clean_name}'."}

    def remove_account(self, name_or_id: str) -> Dict[str, Any]:
        """Removes an account by ID or name and updates active selection."""
        val = str(name_or_id or "").strip().lower()
        target = next((a for a in self.accounts if a.accountId.lower() == val or a.displayName.lower() == val), None)
        if not target:
            return {"success": False, "error": "Account not found."}
        self.accounts = [a for a in self.accounts if a.accountId != target.accountId]
        if self.active_account_id == target.accountId:
            self.active_account_id = self.accounts[0].accountId if self.accounts else ""
            if self.accounts:
                self.accounts[0].active = True
        self.save_accounts()
        return {"success": True, "accounts": [a.to_dict() for a in self.accounts]}


# Re-export AuthService from auth_service
from .auth_service import AuthService

__all__ = ["Account", "AccountsManager", "AuthService", "generate_offline_uuid"]
