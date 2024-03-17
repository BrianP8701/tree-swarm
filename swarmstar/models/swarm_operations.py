"""
The NodeEmbryo is what a node outputs to spawn children.

Nodes can perform 1 of 4 "SwarmOperations":
    - SpawnOperation
    - TerminationOperation
    - FailureOperation
    - BlockingOperation
    - UserCommunicationOperation
"""
from __future__ import annotations
from typing import Any, Dict, Literal, Optional, Union
from pydantic import BaseModel, Field
from pydantic import ValidationError

from swarmstar.utils.misc.generate_uuid import generate_uuid
from swarmstar.utils.data import MongoDBWrapper

db = MongoDBWrapper()

class NodeEmbryo(BaseModel):
    action_id: str
    message: str
    context: Optional[Dict[str, Any]] = {}

class SwarmOperation(BaseModel):
    id: str
    operation_type: Literal[
        "spawn",
        "terminate",
        "node_failure",
        "blocking",
        "user_communication",
        "action"
    ]

    @classmethod
    def model_validate(cls,data: Union[Dict[str, Any], 'SwarmOperation'], **kwargs) -> 'SwarmOperation':
        if isinstance(data, SwarmOperation):
            return data
        elif isinstance(data, dict):
            operation_type = data.get('operation_type')
            if operation_type == 'blocking':
                return BlockingOperation(**data)
            elif operation_type == 'spawn':
                return SpawnOperation(**data)
            elif operation_type == 'action':
                return ActionOperation(**data)
            elif operation_type == 'terminate':
                return TerminationOperation(**data)
            elif operation_type == 'node_failure':
                return FailureOperation(**data)
            elif operation_type == 'user_communication':
                return UserCommunicationOperation(**data)
        return super().model_validate(data, **kwargs)

    @staticmethod
    def save(operation: SwarmOperation) -> None:
        db.insert("swarm_operations", operation.id, operation.model_dump())

    @staticmethod
    def get(operation_id: str) -> SwarmOperation:
        operation = db.get("swarm_operations", operation_id)
        if operation is None:
            raise ValueError(f"Operation with id {operation_id} not found")
        operation_type = operation["operation_type"]
    
        operation_mapping = {
            "blocking": BlockingOperation,
            "user_communication": UserCommunicationOperation,
            "spawn": SpawnOperation,
            "terminate": TerminationOperation,
            "action": ActionOperation,
            "node_failure": FailureOperation,
        }
        
        if operation_type in operation_mapping:
            try:
                OperationClass = operation_mapping[operation_type]
                return OperationClass.model_validate(operation)
            except ValidationError as e:
                print(f"Error validating operation {operation} of type {operation_type}")
                raise e
            except Exception as e:
                raise e
        else:
            raise ValueError(f"Operation type {operation_type} not recognized")


class BlockingOperation(SwarmOperation):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid('blocking_op'))
    operation_type: Literal["blocking"] = Field(default="blocking")
    node_id: str
    blocking_type: Literal[
        "instructor_completion",
    ]
    args: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    next_function_to_call: str

class SpawnOperation(SwarmOperation):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid('spawn_op'))
    operation_type: Literal["spawn"] = Field(default="spawn")
    node_embryo: NodeEmbryo
    parent_node_id: Optional[str] = None
    node_id: Optional[str] = None

class ActionOperation(SwarmOperation):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid('action_op'))
    operation_type: Literal["action"] = Field(default="action")
    function_to_call: str
    node_id: str
    args: Dict[str, Any] = {}

class TerminationOperation(SwarmOperation):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid('termination_op'))
    operation_type: Literal["terminate"] = Field(default="terminate")
    terminator_node_id: str
    node_id: str
    context: Optional[Dict[str, Any]] = None

class FailureOperation(SwarmOperation):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid('failure_op'))
    operation_type: Literal["node_failure"] = Field(default="node_failure")
    failure_type: Literal[
        "missing_action",
        "instructor_failure",
        "execution_error"
    ]
    node_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = {}

class UserCommunicationOperation(SwarmOperation):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid('user_comms_op'))
    operation_type: Literal["user_communication"] = Field(default="user_communication")
    node_id: str
    message: str
    context: Optional[Dict[str, Any]] = {}
    next_function_to_call: str
