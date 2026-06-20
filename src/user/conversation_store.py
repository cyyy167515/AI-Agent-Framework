"""??????
?????????????????????
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ConversationStore:
    """???????
    ?????? JSON ???????????
    """
    
    def __init__(self, user_id: str, data_dir: Optional[str] = None):
        """
        Args:
            user_id: ?? ID
            data_dir: ????
        """
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'users' / user_id
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.conversations_file = self.data_dir / 'conversations.json'
        self.conversations: List[Dict] = []
        self._load()
    
    def _load(self):
        """?????????"""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
            except Exception:
                self.conversations = []
    
    def _save(self):
        """?????????"""
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=2)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """???????????
        
        Args:
            role: ?? (user/assistant)
            content: ????
            metadata: ??????????????????
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message["metadata"] = metadata
        
        self.conversations.append(message)
        self._save()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """??????
        
        Args:
            limit: ????????None ????
        
        Returns:
            ??????
        """
        if limit and limit < len(self.conversations):
            return self.conversations[-limit:]
        return self.conversations
    
    def clear(self):
        """??????"""
        self.conversations = []
        self._save()
    
    def count(self) -> int:
        """??????"""
        return len(self.conversations)
    
    def export_text(self) -> str:
        """????????"""
        lines = []
        for msg in self.conversations:
            role = "??" if msg['role'] == 'user' else "??"
            lines.append(f"[{role}] {msg['content']}")
        return "\n".join(lines)
