def test_explain_can_import_fail(pytester):
    pytester.makepyfile(foo='import fizz')
    pytester.makepyfile("""
        from pyarch import can_import

        def test_arch(arch):
            arch.check({'foo': can_import('bar')})
    """)
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)
    explanation_lines = [
        line
        for line in result.outlines
        if 'no matching import' in line and '[scope' in line
    ]
    assert len(explanation_lines) == 1
    assert 'foo.py' in explanation_lines[0]


def test_explain_must_not_import_fail(pytester):
    pytester.makepyfile(
        foobar="""
        from foo import bar
        import foo.bar
    """
    )
    pytester.makepyfile("""
        from pyarch import must_not_import

        def test_arch(arch):
            arch.check({'foobar': must_not_import('foo.bar')})
    """)
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)
    explanation_lines = [
        line for line in result.outlines if 'found in' in line and '[scope' in line
    ]
    assert len(explanation_lines) == 2
    assert 'foobar.py:1' in explanation_lines[0]
    assert 'foobar.py:2' in explanation_lines[1]
