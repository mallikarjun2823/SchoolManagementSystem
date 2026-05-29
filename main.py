"""Small script used for manual invocation during development.

This module provides a lightweight `main()` entrypoint used for
ad-hoc checks while developing the project. It is not used by the
Django runtime.
"""


def main():
    """Print a short greeting for manual testing.

    This function is intentionally minimal and exists to make it easy
    to run the repository as a small script.
    """
    print("Hello from sms!")


if __name__ == "__main__":
    main()
