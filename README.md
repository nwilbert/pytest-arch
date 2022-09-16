
# pytest-arch

*A pythonic derivative of [ArchUnit](https://www.archunit.org), in the form of a [pytest](https://www.pytest.org) plugin.*

The idea is to write automated tests for the architecture aspects of your Python project.

For now, this plugin covers import statements in your Python code. This enables you to write automated tests for the dependencies in your project.

### Simple example
```python
def test_import(arch):
    assert arch.import_of('foo') in arch.modules_at('bar')
```
This will check that module `foo` is imported in module `bar`.

### Installation & use

Install `pytest-arch` via the Python package manager of your choice (e.g., pip or poetry).

If your project structure is "normal" then you can simply start using the `arch` fixture in your tests right away, as seen above. 

### Complex examples
```python
def test_import_subpackage(arch):
    assert arch.import_of('fizz.buzz') not in arch.modules_at('foo.bar')
``` 
Checks that module `buzz` in package `fizz` is not imported in module `bar` of package `foo`. Note that the dot `.` is used as path separator (other path separators like `/` are not supported).
    
```python
def test_import_complex(arch):
    assert arch.import_of('foo', absolute=True) in arch.modules_at(
        'bar', exclude=['lorem', 'ipsum']
    )
```
Via the boolean argument `absolute` you can specify that only absolute or relative imports of `foo` should be considered.
Via the argument `exclude` you can exclude subpackages from the check (in this case `bar.lorem` and `bar.ipsum`).

## Details

### How it works

In principle this plugin uses the `ast` module from the standard libray to analyze at the abstract syntax tree of your project. Import statement are collected and normalized. This is triggered by using the `arch` fixture in a test. Note that this can take a while. Behind the scenes this data is then used by `arch.modules_at` factory method in your tests.

The analysis of the abstact syntax tree is superficial, so there are limitations. Due to the dynamic nature of Python it is easy to circumvent tests if you want to. So we assume that this plugin is used in a "friendly" context.

Note that we don't track how the imported symbols are used. For example, in the case of
```python
import a
...
a.b()
```
you will *not* be able to check that `a.b` is used (e.g., via `arch.import_of('a.b')`). 

### Absolute vs. relative imports

Imports in tests are always specified like absolute imports (i.e., fully qualified), regardless if relative imports are used in the source. You can optionally use the `absolute` argument for `arch.import_of` to distinguish between absolute and relative imports.

Note that relative imports from outside the configured project source directory are not supported (because we can't normalize those).

### Internal vs. external imports

Both imports from inside your project and from external packages (standard library or installed packages) are supported.

### Configuration

This plugin uses a simple heuristic to determine the source root of your project. You can check the source root via the `arch_project_paths` fixture in a test.

Alternatively you can specify the source root in the pytest configuration. If you use a `pyproject.toml` then this looks like:
```
[tool.pytest.ini_options]
    arch_project_paths = [
        "foo/bar",
    ]
```
Other config formats are supported as well, as long as they are supported by pytest.

### Future plans

- Possibly add more architecture aspects, beyond imports.
- Optimize the implementation with regards to speed.

## License
Licensed under the Apache License, Version 2.0 - see LICENSE.md in project root directory.

## Related Python libraries
- https://pypi.org/project/import-linter
- https://pypi.org/project/findimports
- https://pypi.org/project/pydeps (based on bytecode, not AST)
