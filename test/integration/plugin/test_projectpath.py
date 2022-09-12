from inspect import cleandoc


def test_project_path_from_toml_config(pytester):
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


def test_project_path_from_ini_config(pytester):
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


def test_project_path_from_heuristic_with_src_dir(pytester):
    """Test that config values are read from tox.ini"""
    (pytester.path / 'root' / 'src' / 'foobar').mkdir(parents=True)
    (pytester.path / 'root' / 'test').mkdir(parents=True)
    (pytester.path / 'root' / 'pyproject.toml').write_text('#')
    (pytester.path / 'root' / 'test' / 'test_path.py').write_text(
        cleandoc(
            f"""
            def test_path(arch_project_paths):
                assert len(arch_project_paths) == 1
                assert (str(arch_project_paths[0]) ==
                    '{pytester.path / 'root' / 'src'}')
            """
        )
    )
    result = pytester.runpytest('--rootdir', pytester.path / 'root' / 'test')
    result.assert_outcomes(passed=1)


def test_project_path_from_heuristic_with_nested_dirs(pytester):
    """Test that config values are read from tox.ini"""
    (pytester.path / 'root' / 'foobar').mkdir(parents=True)
    (pytester.path / 'root' / 'test1' / 'test2').mkdir(parents=True)
    (pytester.path / 'root' / 'pyproject.toml').write_text('#')
    (pytester.path / 'root' / 'test1' / 'test2' / 'test_path.py').write_text(
        cleandoc(
            f"""
            def test_path(arch_project_paths):
                assert len(arch_project_paths) == 1
                assert str(arch_project_paths[0]) == '{pytester.path / 'root'}'
            """
        )
    )
    result = pytester.runpytest(
        '--rootdir', pytester.path / 'root' / 'test1' / 'test2'
    )
    result.assert_outcomes(passed=1)


def test_project_path_from_heuristic_with_setup_py(pytester):
    """Test that config values are read from tox.ini"""
    (pytester.path / 'root' / 'foobar').mkdir(parents=True)
    (pytester.path / 'root' / 'test').mkdir(parents=True)
    (pytester.path / 'root' / 'setup.py').write_text('#')
    (pytester.path / 'root' / 'test' / 'test_path.py').write_text(
        cleandoc(
            f"""
            def test_path(arch_project_paths):
                assert len(arch_project_paths) == 1
                assert str(arch_project_paths[0]) == '{pytester.path / 'root'}'
            """
        )
    )
    result = pytester.runpytest('--rootdir', pytester.path / 'root' / 'test')
    result.assert_outcomes(passed=1)
