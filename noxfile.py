import nox
from nox_poetry import session

src_path = 'src'
code_paths = [src_path, 'test', 'noxfile.py']

nox.options.sessions = ['blue', 'isort']


@session
def blue(session):
    session.install('blue')
    session.run('blue', *code_paths)


@session
def isort(session):
    session.install('isort')
    session.run('isort', *code_paths)
