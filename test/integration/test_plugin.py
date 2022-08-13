def test_assertions(pytester):

    pytester.makepyfile(
        """
        from pyarch.testutil import Import as import_of

        def test_arch(package):
            assert import_of('b.x') in package('a')
            assert import_of('c') not in package('a')
    """
    )

    pytester.makeconftest(
        """
        import pytest
        import pathlib

        @pytest.fixture
        def project_path(tmp_path):
            (pathlib.Path(tmp_path) / 'a.py').write_text('from b import x')
            return tmp_path
    """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
