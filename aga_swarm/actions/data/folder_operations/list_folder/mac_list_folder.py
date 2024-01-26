import os
from pydantic import validate_arguments

# Function to list the contents of a folder on a mac
@validate_arguments
def mac_list_folder(folder_path: str) -> dict:
    try:
        # List the contents of the folder
        contents = os.listdir(folder_path)
        return {'status_message': 'Success', 'error_message': '', 'contents': contents}
    except Exception as e:
        # Return error message if an exception occurs
        return {'status_message': 'Failure', 'error_message': str(e)}

# Main section
@validate_arguments
def main(folder_path: str) -> dict:
    return mac_list_folder(folder_path)