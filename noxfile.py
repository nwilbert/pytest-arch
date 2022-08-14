import nox
from nox_poetry import session

src_path = 'src'
code_paths = [src_path, 'test', 'noxfile.py']

nox.options.sessions = ['blue', 'isort', 'flake8', 'mypy', 'pytest']


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
