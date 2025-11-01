#!/usr/bin/env python
import os
import sys


def main() -> None:
    """Paleidžia tinkamą Django aplinką administraciniams veiksmams."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schoolms.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Nepavyko importuoti Django. Įsitikinkite, kad jis įdiegtas ir prieinamas "
            "PYTHONPATH aplinkoje."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
