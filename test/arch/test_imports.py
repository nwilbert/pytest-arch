from pytest_imports import (
    must_import,
    must_not_import,
    must_not_import_private,
    must_not_import_within_parent,
    project,
    scope,
)


def test_internal_dependencies(imports):
    imports.check(
        {
            scope('pytest_imports', without='plugin'): [
                must_not_import('pytest_imports.parser'),
                must_not_import('pytest_imports.query'),
                must_not_import('pytest_imports.plugin'),
            ],
            'pytest_imports.plugin': must_import('pytest_imports.model'),
            'pytest_imports.query': must_import('pytest_imports.model'),
            'pytest_imports.parser': must_import('pytest_imports.model'),
        }
    )


def test_all_internal_imports_must_be_relative(imports):
    imports.check(
        {
            project(): must_not_import_within_parent(via='absolute'),
        }
    )


def test_external_dependencies(imports):
    imports.check(
        {
            scope('pytest_imports', without='parser'): must_not_import('ast'),
            scope('pytest_imports', without='plugin'): must_not_import('pytest'),
        }
    )


def test_no_private_imports(imports):
    imports.check(
        {
            project(): must_not_import_private(),
        }
    )
