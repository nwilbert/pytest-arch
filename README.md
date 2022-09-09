
# pytest-arch

*A pythonic derivative of [ArchUnit](https://www.archunit.org), in the form of a [pytest](https://www.pytest.org) plugin.* 

## Usage

### Absolute vs. relative imports
Imports are always specified like absolute imports (i.e. fully qualified), regardless if relative imports are used in the source. You can optionally use the `absolute` argument for `import_of` to distinguish between absolute and relative imports.


## Further information

### Related libraries
- https://pypi.org/project/import-linter
- https://pypi.org/project/findimports
- https://pypi.org/project/pydeps (based on bytecode, not AST)
