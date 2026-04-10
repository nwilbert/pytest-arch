import webbrowser
from pathlib import Path

import nox

src_path = 'src'
code_paths = [src_path, 'test', 'noxfile.py']

nox.options.default_venv_backend = 'uv'
nox.options.sessions = [
    'format',
    'lint',
    'mypy',
    'test',
    'coverage',
    'pytest_compat',
    'audit',
]


def _sync(session: nox.Session, group: str) -> None:
    session.run('uv', 'sync', '--group', group, '--active', external=True)


@nox.session
def format(session):
    _sync(session, 'lint')
    session.run('ruff', 'format', *session.posargs, *code_paths)


@nox.session
def lint(session):
    _sync(session, 'lint')
    session.run('ruff', 'check', *code_paths)


@nox.session
def mypy(session):
    _sync(session, 'typecheck')
    session.run('mypy', src_path)


@nox.session
def test(session):
    _sync(session, 'test')
    session.run('pytest')


PYTEST_PYTHON_MATRIX = [
    ('7', ['3.10', '3.11', '3.12']),
    ('8', ['3.10', '3.11', '3.12', '3.13']),
    ('9', ['3.10', '3.11', '3.12', '3.13', '3.14']),
]


@nox.session
@nox.parametrize(
    'python,pytest_version',
    [
        (python, pytest_ver)
        for pytest_ver, pythons in PYTEST_PYTHON_MATRIX
        for python in pythons
    ],
)
def pytest_compat(session, pytest_version):
    _sync(session, 'test')
    session.run('uv', 'pip', 'install', f'pytest~={pytest_version}.0', external=True)
    session.run('pytest', 'test/integration')


@nox.session
def coverage(session):
    _sync(session, 'coverage')
    session.run(
        'coverage',
        'run',
        '--source',
        'pytest_imports',
        '-m',
        'pytest',
        'test/integration',
        'test/unit',
    )
    try:
        session.run('coverage', 'report', '--fail-under', '100', '--show-missing')
    finally:
        if 'html' in session.posargs:
            session.run('coverage', 'html', '--skip-covered')
            webbrowser.open((Path.cwd() / 'htmlcov' / 'index.html').as_uri())


@nox.session
def audit(session: nox.Session) -> None:
    _sync(session, 'audit')
    session.run('pip-audit', '--local')
