from typing import Sequence

from pyarch.testutil import Import, Package


def pytest_assertrepr_compare(
    op: str, left: str, right: str
) -> Sequence[str] | None:
    match op, left, right:
        case 'not in', Import(), Package():
            # TODO: call helper method for nice explanation with lineno
            return [f'{left} should not be imported from {right}']
        case 'in', Import(), Package():
            return [f'{left} should be imported from {right}']
    return None
