from invoke import task

@task
def build_exe(ctx):
    ctx.run('pyinstaller   main.spec --noconfirm --distpath ".dist" --workpath ".build"')

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
