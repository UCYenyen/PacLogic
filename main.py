"""Entry point: bootstraps the game loop."""
from src.core.engine import Game


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
