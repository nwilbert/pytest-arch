def test_internal_dependencies(arch):
    assert arch.import_of('pyarch.parser') not in arch.modules_at(
        'pyarch', exclude=['plugin']
    )
    assert arch.import_of('pyarch.query') not in arch.modules_at(
        'pyarch', exclude=['plugin']
    )
    assert arch.import_of('pyarch.plugin') not in arch.modules_at(
        'pyarch', exclude=['plugin']
    )
    assert arch.import_of('pyarch.model') in arch.modules_at('pyarch.plugin')
    assert arch.import_of('pyarch.model') in arch.modules_at('pyarch.query')
    assert arch.import_of('pyarch.model') in arch.modules_at('pyarch.parser')


def test_all_internal_imports_must_be_relative(arch):
    assert arch.import_of('pyarch', absolute=True) not in arch.modules_at(
        'pyarch'
    )


def test_external_dependencies(arch):
    assert arch.import_of('ast') not in arch.modules_at(
        'pyarch', exclude=['parser']
    )
    assert arch.import_of('pytest') not in arch.modules_at(
        'pyarch', exclude=['plugin']
    )
