'''
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
'''
from pydantic import BaseModel
from typing import List
from typing_extensions import Literal

from swarm_star.utils.data.kv_operations.main import get_kv
from swarm_star.utils.data.internal_operations import get_internal_action_metadata
from swarm_star.swarm.types.swarm_config import SwarmConfig

class ActionNode(BaseModel):
    is_folder: bool
    type: Literal['azure_blob_storage_folder', 'internal_folder', 'internal_action', 'azure_blob_action']
    name: str
    description: str
    children: List[str] = None
    parent: str = None

class ActionFolder(ActionNode):
    is_folder: True
    type: Literal['internal_folder', 'azure_blob_storage_folder']
    name: str
    description: str
    children: List[str]
    parent: str = None

class Action(ActionNode):
    is_folder: False
    type: Literal['internal_action', 'azure_blob_action']
    name: str
    description: str
    parent: str
    children = None
    termination_policy: Literal[
        'simple',
        'parallel_review',
        'clone_with_reports'
    ]

class InternalAction(Action):
    is_folder: False
    type: Literal['internal_action']
    name: str
    description: str
    children = None
    parent: str
    termination_policy: Literal[
        'simple',
        'parallel_review',
        'clone_with_reports'
    ]
    internal_action_path: str

class InternalFolder(ActionFolder):
    is_folder: True
    type: Literal['internal_folder']
    name: str
    description: str
    children: List[str]
    parent: str = None
    internal_folder_path: str

class ActionSpace(BaseModel):
    '''
    The action space metadata is stored in the swarm's kv store as:
    
        action_id: ActionMetadata
    '''
    swarm: SwarmConfig
    
    def __getitem__(self, action_id: str) -> ActionNode:
        try:
            internal_action_metadata = get_internal_action_metadata(self.swarm, action_id)
            action_metadata =  ActionNode(**internal_action_metadata)
        except Exception as e1:
            try:
                external_action_metadata = get_kv(self.swarm, 'action_space', action_id)
                if external_action_metadata is not None:
                    action_metadata = ActionNode(**external_action_metadata)
                else:
                    raise ValueError(f"This action id: `{action_id}` does not exist in external action space.") from e1
            except Exception as e2:
                raise ValueError(f"This action id: `{action_id}` does not exist in both internal and external action spaces.") from e2
            
        type_mapping = {
            'internal_action': InternalAction,
            'internal_folder': InternalFolder,
        }
        
        action_type = action_metadata.type
        if action_type in type_mapping:
            return type_mapping[action_type](**action_metadata)
        else:
            return ActionNode(**action_metadata)
    
    def get_root(self) -> ActionNode:
        return self['swarm_star/actions']
    