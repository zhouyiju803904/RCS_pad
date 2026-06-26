# models.py
from dataclasses import dataclass

@dataclass
class AGVStatus:
    id: str
    ip: str
    name: str
    state: str   # "running", "idle", "error"
    battery: int
    location: str = ""
    task: str = ""

@dataclass
class Task:
    id: str
    priority: str
    path: str
    assigned_agv: str
    state: str
    created_at: str
    started_at: str
    finished_at: str


@dataclass
class StorageSlot:
    id: str
    status: str  # idle/occupied/reserved/error
    occupant: str = ""  # item or order occupying
    updated_at: str = ""
    capacity: int = 1
    note: str = ""
