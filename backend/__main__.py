"""
This file makes the backend package runnable.

When you run `python -m backend`, this script is executed.
It imports the `main` function from our `__init__.py` and runs it.
"""
from . import main

if __name__ == "__main__":
    main()
