import requests, time

url = 'http://127.0.0.1:5001/dashboard'
for i in range(10):
    try:
        r = requests.get(url, timeout=3)
        print('OK', r.status_code)
        break
    except Exception as e:
        print('TRY', i, e)
        time.sleep(1)
else:
    print('FAILED')
