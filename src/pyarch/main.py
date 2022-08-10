from pathlib import Path

from pyarch.parser import build_import_model


def main():
    base_path = Path('/Users/niko/projects/bobbytime/bobbytime')
    root_node = build_import_model(base_path)
    pass


if __name__ == '__main__':
    main()
