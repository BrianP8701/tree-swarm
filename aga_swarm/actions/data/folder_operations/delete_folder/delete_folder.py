from pydantic import validate_arguments

from aga_swarm.actions.swarm.action_types.internal_default_swarm_action import internal_default_swarm_action
from aga_swarm.swarm.types import SwarmID

@validate_arguments
def main(swarm_id: SwarmID, folder_path: str) -> dict:
    platform = swarm_id.platform.value
    return internal_default_swarm_action(action_id=f'aga_swarm/actions/data/folder_operations/delete_folder/{platform}_delete_folder.py', 
        params={'folder_path': folder_path})
