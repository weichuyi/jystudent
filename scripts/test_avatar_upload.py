import requests
from pathlib import Path

BASE='http://127.0.0.1:5001'
S = requests.Session()
# login with default admin
r = S.post(BASE+'/login', data={'username':'admin','password':'weichuy1'})
print('login', r.status_code)
# get cookies
logo = Path('static/images/logo.png')
if not logo.exists():
    print('logo not found', logo)
else:
    with open(logo,'rb') as f:
        files = {'avatar': ('logo.png', f, 'image/png')}
        r2 = S.post(BASE+'/profile/avatar', files=files)
        print('upload status', r2.status_code)
        print(r2.text[:400])
