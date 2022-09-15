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
