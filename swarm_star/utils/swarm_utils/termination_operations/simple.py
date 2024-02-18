'''
    Simple termination simply terminates the given node and returns a TerminationOperation for the parent node.
'''
from typing import Union

from swarm_star.swarm.types import SwarmConfig, TerminationOperation, SwarmState

def execute_termination_operation(swarm: SwarmConfig, termination_operation: TerminationOperation) -> Union[TerminationOperation, None]:
    node_id = termination_operation.node_id
    swarm_state = SwarmState(swarm=swarm)
    node = swarm_state[node_id]
    node.alive = False
    swarm_state.update_state(node)
    try:
        parent_node = swarm_state[node.parent_id]
    except:
        return None
    
    return TerminationOperation(
        operation_type='terminate',
        node_id=parent_node.node_id,
        report=''
    )
