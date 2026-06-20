"""??????
????????????????
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    """??????"""
    user_id: str
    username: str
    created_at: str
    last_active: str


class UserManager:
    """?????
    ?????????????????
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Args:
            data_dir: ??????????? config ?? users.json
        """
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / 'data'
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.data_dir / 'users.json'
        self.users: Dict[str, User] = {}
        
        # ??????
        self._load_users()
    
    def _load_users(self):
        """?????????"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for uid, udata in data.items():
                        self.users[uid] = User(**udata)
            except Exception:
                self.users = {}
    
    def _save_users(self):
        """?????????"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            data = {uid: u.model_dump() for uid, u in self.users.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_or_create_user(self, username: str) -> User:
        """???????
        ????????????????????????
        """
        # ??????
        for user in self.users.values():
            if user.username == username:
                user.last_active = datetime.now().isoformat()
                self._save_users()
                return user
        
        # ?????
        user_id = f"user_{len(self.users) + 1:04d}"
        now = datetime.now().isoformat()
        user = User(
            user_id=user_id,
            username=username,
            created_at=now,
            last_active=now,
        )
        self.users[user_id] = user
        self._save_users()
        
        # ????????????
        user_dir = self.data_dir / 'users' / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        return user
    
    def list_users(self) -> list:
        """????????"""
        return list(self.users.values())
    
    def get_user(self, user_id: str) -> Optional[User]:
        """?? ID ????"""
        return self.users.get(user_id)
    
    def delete_user(self, user_id: str) -> bool:
        """????????"""
        if user_id not in self.users:
            return False
        
        # ????????
        user_dir = self.data_dir / 'users' / user_id
        if user_dir.exists():
            import shutil
            shutil.rmtree(user_dir)
        
        del self.users[user_id]
        self._save_users()
        return True
