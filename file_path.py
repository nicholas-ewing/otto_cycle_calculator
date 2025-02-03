from os import path

def get_file_path(relative_path: str) -> str:
    """
    Get the absolute path of a file relative to the application
    """
    return str(path.abspath(path.join(path.dirname(__file__), relative_path)))