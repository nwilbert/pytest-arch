from pyarch.testutil import Import as import_of


def test_arch(package):
    assert import_of('pyarch.parser') in package('pyarch.model')
    assert import_of('pyarch.model') in package('pyarch.parser')


def test_assertions(pytester):

    pytester.makepyfile(
        """
        from pyarch.testutil import Import as import_of

        def test_arch(package):
            assert import_of('pyarch.parser') not in package('pyarch.model')
            assert import_of('pyarch.model') in package('pyarch.parser')
    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)


# TODO: implement "without"
# assert import_of('a.b') not in
# package('bobbytime.models').without('repository')
# TODO: implment import variations
# assert Import_of_exactly('bobbytime.database')
# not in package('bobbytime.models').without('repository')
