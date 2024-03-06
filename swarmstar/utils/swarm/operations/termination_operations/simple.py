"""
    Simple termination simply terminates the given node and returns a TerminationOperation for the parent node.
"""
from typing import Union

from swarmstar.swarm.types import SwarmConfig, TerminationOperation
from swarmstar.utils.swarm.swarmstar_space import get_swarm_node, update_swarm_node

def terminate(
    swarm: SwarmConfig, termination_operation: TerminationOperation
) -> Union[TerminationOperation, None]:
    node_id = termination_operation.node_id
    node = get_swarm_node(swarm, node_id)
    node.alive = False
    update_swarm_node(swarm, node)

    try:
        parent_node = get_swarm_node(swarm, node.parent_id)
    except:
        return None

    return TerminationOperation(
        node_id=parent_node.id, 
    )
