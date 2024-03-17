"""
Use this object to configure the swarm to your platform and personal preferences.
"""
from typing import Optional, Dict, Any

from pydantic import BaseModel, model_serializer
from typing_extensions import Literal
from swarmstar.utils.data import MongoDBWrapper

db = MongoDBWrapper()

class SwarmConfig(BaseModel):
    id: str
    root_path: str = None # Set this on spawn
    platform: Literal["mac", "azure"]

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return {k: v for k, v in dict(self).items() if v is not None}

    @staticmethod
    def add(swarm_config: 'SwarmConfig') -> None:
        db.insert("config", swarm_config.id, swarm_config.model_dump())
        db.append("admin", "swarms", "data", swarm_config.id)

    @staticmethod
    def get(swarm_config_id: str) -> 'SwarmConfig':
        return SwarmConfig(**db.get("config", swarm_config_id))
