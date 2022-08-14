def test_assertions(pytester):

    pytester.makepyfile(
        """
        from pyarch.parser import build_import_model
        from pyarch.model import DotPath
        from pyarch.testutil import Import, Package

        def test_arch(project_path):
            base_node = build_import_model(project_path)
            package = Package(base_node.get(DotPath('a')))
            assert Import(DotPath('b.x')) in package
            assert Import(DotPath('c')) not in package
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
