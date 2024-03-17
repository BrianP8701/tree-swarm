"""
Every node in the swarm corresponds to an action.

The action space metadata organizes the actions and is used to search
for actions and execute them.

Every action has the same IO: 
    message: str, swarm: Swarm and node_id: str

The actual actions are all prewritten code. The action space metadata's
purpose is:

    (1) To allow the swarm to organize and search for actions
    (2) To allow the swarm to execute actions

Because the swarm can dynamically create actions we need (2). For example,
we might need to dynamically spin up a docker container and execute a function.
The execution_metadata provides a place to store the information to be passed
to the executor who handles this action_type.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from typing_extensions import Literal

from swarmstar.utils.misc.generate_uuid import generate_uuid
from swarmstar.utils.data import MongoDBWrapper
from swarmstar.models.internal_metadata import SwarmstarInternal

db = MongoDBWrapper()

class ActionMetadata(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid('action'))
    is_folder: bool
    type: Literal[
        "internal_folder",
        "internal_action",
    ]
    name: str
    description: str
    children_ids: Optional[List[str]] = None
    parent: Optional[str] = None
    routable: bool = True

    @staticmethod
    def get(action_id: str) -> 'ActionMetadata':
        try:
            action_metadata = db.get("action_space", action_id)
            if action_metadata is None:
                raise ValueError(
                    f"This action id: `{action_id}` does not exist in external action space."
                )
        except Exception as e1:
            try:
                action_metadata = SwarmstarInternal.get_action_metadata(action_id)
                if action_metadata is None:
                    raise ValueError(
                        f"This action id: `{action_id}` does not exist in internal action space."
                    ) from e1
            except Exception as e2:
                raise ValueError(
                    f"This action id: `{action_id}` does not exist in both internal and external action spaces."
                ) from e2

        type_mapping = {
            "internal_action": InternalAction,
            "internal_folder": InternalFolder,
        }
        action_type = action_metadata["type"]
        if action_type in type_mapping:
            return type_mapping[action_type](**action_metadata)
        return ActionMetadata(**action_metadata)

class ActionFolder(ActionMetadata):
    is_folder: Literal[True] = Field(default=True)
    type: Literal["internal_folder", "azure_blob_storage_folder"]
    name: str
    description: str
    children_ids: List[str]
    parent: Optional[str] = None


class Action(ActionMetadata):
    is_folder: Literal[False] = Field(default=False)
    type: Literal["internal_action", "azure_blob_action"]
    name: str
    description: str
    parent: str
    children_ids: Optional[List[str]] = Field(default=None)
    termination_policy: Literal["simple", "confirm_directive_completion", "clone_with_questions_answered"]


class InternalAction(Action):
    type: Literal["internal_action"] = Field(default="internal_action")
    name: str
    description: str
    children_ids: Optional[List[str]] = Field(default=None)
    parent: str
    termination_policy: Literal["simple", "confirm_directive_completion", "clone_with_questions_answered"]
    internal_action_path: str


class InternalFolder(ActionFolder):
    type: Literal["internal_folder"] = Field(default="internal_folder")
    name: str
    description: str
    children_ids: List[str]
    parent: str = None
    internal_folder_path: str
