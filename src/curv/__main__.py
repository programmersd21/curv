"""Entry point for curv."""

from rich.traceback import install as install_traceback

from curv.app import App

install_traceback()


def main() -> None:
    """Run the curv application."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
