def test_config_project_path_toml(pytester):
    """Test that config values are read from pyproject.toml"""
    pytester.makepyprojecttoml(
        """
        [tool.pytest.ini_options]
        arch_project_paths = [
            "foobar",
            "/foo/bar"
        ]
    """
    )
    pytester.makepyfile(
        """
        from pathlib import Path

        def test_arch(arch_project_paths, pytestconfig):
            assert len(arch_project_paths) == 2
            assert arch_project_paths[0] == pytestconfig.rootpath / 'foobar'
            assert arch_project_paths[1] == Path('/foo/bar')
    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_config_project_path_ini(pytester):
    """Test that config values are read from tox.ini"""
    pytester.makeini(
        """
        [pytest]
        arch_project_paths =
            foobar
            /foo/bar
    """
    )
    pytester.makepyfile(
        """
        from pathlib import Path

        def test_arch(arch_project_paths, pytestconfig):
            assert len(arch_project_paths) == 2
            assert arch_project_paths[0] == pytestconfig.rootpath / 'foobar'
            assert arch_project_paths[1] == Path('/foo/bar')

    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_simple_project(pytester):
    pytester.makepyfile(foobar='from foo import bar')
    pytester.makepyfile(
        """
        from pyarch.model import DotPath
        from pyarch.assertion import ImportOf

        def test_arch(package):
            assert ImportOf(DotPath('foo.bar')) in package('foobar')
            assert ImportOf(DotPath('fiz')) not in package('foobar')
    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
    print(result.stdout)
