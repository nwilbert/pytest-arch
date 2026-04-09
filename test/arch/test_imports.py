from pyarch import (
    must_import,
    must_not_import,
    must_not_import_private,
    must_not_import_within_parent,
    project,
    scope,
)


def test_internal_dependencies(arch):
    arch.check(
        {
            scope('pyarch', without='plugin'): [
                must_not_import('pyarch.parser'),
                must_not_import('pyarch.query'),
                must_not_import('pyarch.plugin'),
            ],
            'pyarch.plugin': must_import('pyarch.model'),
            'pyarch.query': must_import('pyarch.model'),
            'pyarch.parser': must_import('pyarch.model'),
        }
    )


def test_all_internal_imports_must_be_relative(arch):
    arch.check(
        {
            project(): must_not_import_within_parent(via='absolute'),
        }
    )


def test_external_dependencies(arch):
    arch.check(
        {
            scope('pyarch', without='parser'): must_not_import('ast'),
            scope('pyarch', without='plugin'): must_not_import('pytest'),
        }
    )


def test_no_private_imports(arch):
    arch.check(
        {
            project(): must_not_import_private(),
        }
    )
