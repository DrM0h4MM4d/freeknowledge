#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    print("""
\n** Freeknowledge Web Application developed by DrM0h4MM4d under GPL License  **
This is the first version of this project and its fully buggy now XD [FIXING ...]
FreeKnowledgeWAP: v1.0
Developer: DrM0h4MM4d
""")
    main()
