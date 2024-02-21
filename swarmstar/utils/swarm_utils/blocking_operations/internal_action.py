'''
This blocking operation will call the next_function_to_call of the node's action,
combining the args, context and swarm into the function call.

Think of this as the entrypoint back into the action after a blocking operation has been completed.
'''

from __future__ import annotations
from importlib import import_module
from typing import TYPE_CHECKING, Union, List

from swarmstar.swarm.types import ActionSpace, SwarmState

if TYPE_CHECKING:
    from swarmstar.swarm.types import SwarmConfig, BlockingOperation, SwarmOperation

# This blocking operation doesn't have set args, it will just pass the args and context to the next function to call
def expected_args(BaseModel):
    pass

def execute_blocking_operation(swarm: SwarmConfig, blocking_operation: BlockingOperation) -> Union[SwarmOperation, List[SwarmOperation]]:
    action_space = ActionSpace(swarm=swarm)
    swarm_state = SwarmState(swarm=swarm)
    node_id = blocking_operation.node_id
    node = swarm_state[node_id]
    action_metadata = action_space[node.action_id]
    script_path = action_metadata.execution_metadata['script_path']
    action_script = import_module(script_path)
    
    combined_args = {}
    combined_args.update(blocking_operation.args)
    if blocking_operation.context is not None:
        combined_args.update(blocking_operation.context)
    
    return getattr(action_script, blocking_operation.next_function_to_call)(**combined_args)
