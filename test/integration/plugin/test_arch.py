def test_simple_project(pytester):
    pytester.makepyfile(foobar='from foo import bar')
    pytester.makepyfile("""
        from pyarch import can_import, must_not_import

        def test_arch(arch):
            arch.check({
                'foobar': [can_import('foo.bar'), must_not_import('fiz')],
            })
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
