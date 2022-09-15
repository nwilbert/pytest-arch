import webbrowser
from pathlib import Path

import nox
from nox_poetry import session

src_path = 'src'
code_paths = [src_path, 'test', 'noxfile.py']

nox.options.sessions = [
    'blue',
    'isort',
    'flake8',
    'mypy',
    'pytest',
    'coverage',
]


@session
def blue(session):
    session.install('blue')
    session.run('blue', *code_paths)


@session
def isort(session):
    session.install('isort')
    session.run('isort', *code_paths)


@session
def flake8(session):
    session.install('flake8')
    session.run('flake8', *code_paths)


@session
def mypy(session):
    session.install('mypy', '.')
    session.run('mypy', src_path)


@session
def pytest(session):
    session.install('pytest', 'pytest-mock', '.')
    session.run('pytest')


@session
def coverage(session):
    session.install('pytest', 'pytest-mock', 'coverage', '.')
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
        session.run(
            'coverage', 'report', '--fail-under', '100', '--show-missing'
        )
    finally:
        if 'html' in session.posargs:
            session.run('coverage', 'html', '--skip-covered')
            webbrowser.open((Path.cwd() / 'htmlcov' / 'index.html').as_uri())
