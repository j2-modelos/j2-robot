from invoke import task

@task
def build_exe(ctx):
    ctx.run('pyinstaller   main.spec --noconfirm --distpath ".dist" --workpath ".build"')
    ctx.run('python scripts/remove_from_build.py')

@task
def build_exe_teste(ctx):
    ctx.run('pyinstaller   dev_scripts/pyi/main.spec --noconfirm --distpath "dev_scripts/pyi/.dist" --workpath "dev_scripts/pyi/.build"')

@task
def testing(ctx):
    ctx.run('python scripts/remove_from_build.py')
"""
@task
def install(ctx):
    ctx.run("pip install -r requirements.txt")

@task
def lint(ctx):
    ctx.run("flake8 . --count --max-line-length=88 --statistics")

@task
def test(ctx):
    ctx.run("pytest tests/")
"""
