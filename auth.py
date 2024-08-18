import requests


def authenticate():
    session = requests.session()
    headers={"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)", 'accept-language': 'en'}
    print('valid')

    url = 'https://users.premierleague.com/accounts/login/'
    payload = {
    'password': '@Fantasy2024',
    'login': 'oyomworld@gmail.com',
    'redirect_uri': 'https://fantasy.premierleague.com/a/login',
    'app': 'plfpl-web'
    }
    response=session.post(url, data=payload,headers=headers)
    if response.status_code ==200:
        print('Login Successful')
        response = session.get('https://fantasy.premierleague.com/api/my-team/5037001')
        if  response.status_code ==200:
            return response.json()
        else:
            raise Exception('Failed to fetch team data')
    
