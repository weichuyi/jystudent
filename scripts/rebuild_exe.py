import os
import shutil
import PyInstaller.__main__

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)
print('Project root:', PROJECT_ROOT)
os.chdir(PROJECT_ROOT)
for p in ('dist','build'):
    if os.path.exists(p):
        if os.path.isdir(p):
            shutil.rmtree(p)
            print('Removed', p)
        else:
            os.remove(p)
            print('Removed file', p)
if os.path.exists('run.spec'):
    os.remove('run.spec')
    print('Removed run.spec')

# Hidden-imports to include problematic werkzeug modules
# Also add app.py as data so run.py can find it at runtime inside the bundle
add_data = 'app.py;.'  # windows format: source;dest
opts = [
    '--onefile',
    '--hidden-import=werkzeug.middleware.proxy_fix',
    '--hidden-import=werkzeug.contrib.fixers',
    '--hidden-import=flask',
    '--hidden-import=flask_sqlalchemy',
    '--hidden-import=flask_wtf',
    '--hidden-import=jinja2',
    '--hidden-import=werkzeug',
    '--hidden-import=click',
    '--hidden-import=itsdangerous',
    '--hidden-import=markupsafe',
    '--hidden-import=wtforms',
    '--hidden-import=sqlalchemy',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=openpyxl',
    f'--add-data={add_data}',
    # include templates and static folders so app can serve them at runtime
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--add-data=instance;instance',
    'run.py'
]
print('Running PyInstaller with opts:', opts)
PyInstaller.__main__.run(opts)
print('Done')
