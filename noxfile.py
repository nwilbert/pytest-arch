import webbrowser
from pathlib import Path

import nox

src_path = 'src'
code_paths = [src_path, 'test', 'noxfile.py']

nox.options.default_venv_backend = 'uv'
nox.options.sessions = [
    'ruff_format',
    'ruff_lint',
    'mypy',
    'pytest',
    'coverage',
]


def _sync(session: nox.Session, group: str) -> None:
    session.run('uv', 'sync', '--group', group, '--active', external=True)


@nox.session
def ruff_format(session):
    _sync(session, 'lint')
    session.run('ruff', 'format', *code_paths)


@nox.session
def ruff_lint(session):
    _sync(session, 'lint')
    session.run('ruff', 'check', *code_paths)


@nox.session
def mypy(session):
    _sync(session, 'typecheck')
    session.run('mypy', src_path)


@nox.session(python=['3.10', '3.11', '3.12', '3.13', '3.14'])
def pytest(session):
    _sync(session, 'test')
    session.run('pytest')


@nox.session
def coverage(session):
    _sync(session, 'coverage')
    session.run(
        'coverage',
        'run',
        '--source',
        'pyarch',
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
