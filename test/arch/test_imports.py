from pyarch import can_import, must_not_import, scope


def test_internal_dependencies(arch):
    arch.check(
        {
            scope('pyarch', without='plugin'): [
                must_not_import('pyarch.parser'),
                must_not_import('pyarch.query'),
                must_not_import('pyarch.plugin'),
            ],
            'pyarch.plugin': can_import('pyarch.model'),
            'pyarch.query': can_import('pyarch.model'),
            'pyarch.parser': can_import('pyarch.model'),
        }
    )


def test_all_internal_imports_must_be_relative(arch):
    arch.check(
        {
            scope('pyarch'): must_not_import('pyarch', via='absolute'),
        }
    )


def test_external_dependencies(arch):
    arch.check(
        {
            scope('pyarch', without='parser'): must_not_import('ast'),
            scope('pyarch', without='plugin'): must_not_import('pytest'),
        }
    )
