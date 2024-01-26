from pydantic import validate_arguments

from aga_swarm.actions.swarm.action_types.internal_swarm_default_action import internal_swarm_default_action as execute

@ validate_arguments
def main(swarm: dict, folder_path: str, new_folder_path: str) -> dict:
    platform = swarm['configs']['platform']
    return execute(f'aga_swarm/actions/data/folder_operations/rename_folder/{platform}_rename_folder.py', 
                   swarm, {'folder_path': folder_path, 'new_folder_name': new_folder_path})

