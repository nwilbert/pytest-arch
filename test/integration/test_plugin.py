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
        def test_arch(arch):
            assert arch.import_of('foo.bar') in arch.modules_at('foobar')
            assert arch.import_of('fiz') not in arch.modules_at('foobar')
    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
    print(result.stdout)


def test_explain_contains_fail(pytester):
    pytester.makepyfile(foo='import fizz')
    pytester.makepyfile(
        """
        def test_arch(arch):
            assert arch.import_of('bar') in arch.modules_at('foo')
    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)
    explanation_lines = [
        line for line in result.outlines if 'no matching import' in line
    ]
    assert len(explanation_lines) == 1
    assert 'foo.py' in explanation_lines[0]


def test_explain_not_contains_fail(pytester):
    pytester.makepyfile(
        foobar="""
        from foo import bar
        import foo.bar
    """
    )
    pytester.makepyfile(
        """
        def test_arch(arch):
            assert arch.import_of('foo.bar') not in arch.modules_at('foobar')
    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)
    explanation_lines = [
        line for line in result.outlines if 'found import' in line
    ]
    assert len(explanation_lines) == 2
    assert 'foobar.py:1' in explanation_lines[0]
    assert 'foobar.py:2' in explanation_lines[1]
