from pathlib import Path
import os

class InDirectory:
    """
    A context manager class that changes the current working directory to the specified directory.

    Attributes:
        directory_name (str): Name of the directory to change to.
        create (bool): Whether to create the directory if it does not exist.
    """

    def __init__(self, directory_name: str, create: bool = False) -> None:
        """
        Initializes a new instance of the InDirectory class.

        Args:
            directory_name (str): Name of the directory to change to.
            create (bool, optional): Whether to create the directory if it does not exist. Defaults to False.
        """
        self.dir = Path(directory_name)
        self.old = None
        if create and not self.dir.exists():
            self.dir.mkdir(parents=True)


    def __enter__(self):
        """
        Enters the context and changes the current working directory to the specified directory.

        Returns:
            InDirectory: The instance of the InDirectory class.
        """
        self.old = Path.cwd()
        if self.dir.exists():
            os.chdir(self.dir)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """
        Exits the context and changes the current working directory back to the original directory.

        Args:
            exc_type (type): The type of the exception raised in the with statement (or None if no exception was raised).
            exc_value (Exception): The exception raised in the with statement (or None if no exception was raised).
            tb (traceback): The traceback object (or None if no exception was raised).
        """
        if self.old:
            os.chdir(self.old)
