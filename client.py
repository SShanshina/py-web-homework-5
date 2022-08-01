import requests

HOST = 'http://127.0.0.1:5000'

print('>>> create normal user')
data = requests.post(f'{HOST}/user/',
                     json={
                         'user_name': 'Will Herondale',
                         'email': 'w.herondale@example.org',
                         'password': 'skdskjfakjfnal1',
                     })
print(data.json(), '\n')

print('>>> create user with too short password')
data = requests.post(f'{HOST}/user/',
                     json={
                         'user_name': 'James Carstairs',
                         'email': 'j.carstairs@example.org',
                         'password': 'gkdn',
                     })
print(data.json(), '\n')

print('>>> create user with redundant field')
data = requests.post(f'{HOST}/user/',
                     json={
                         'user_name': 'Tessa Gray',
                         'email': 't.gray@example.org',
                         'password': 'dkjsnfkjbkafnk223',
                         'blablabla': 'blablabla',
                     })
print(data.json(), '\n')

print('>>> get user by id')
data = requests.get(f'{HOST}/user/1/')
print(data.json(), '\n')

print('>>> login user 1')
data = requests.post(f'{HOST}/login/',
                     json={
                         'user_name': 'Tessa Gray',
                         'email': 't.gray@example.org',
                         'password': 'dkjsnfkjbkafnk223'
                     })
print(data.json(), '\n')

print('>>> login user 2 with wrong password')
data = requests.post(f'{HOST}/login/',
                     json={
                         'user_name': 'Will Herondale',
                         'email': 'w.herondale@example.org',
                         'password': 'skdskjfa1',
                     })
print(data.json(), '\n')

print('>>> login user 2')
data = requests.post(f'{HOST}/login/',
                     json={
                         'user_name': 'Will Herondale',
                         'email': 'w.herondale@example.org',
                         'password': 'skdskjfakjfnal1',
                     })
print(data.json(), '\n')

print('>>> post advertisement without authorization')
data = requests.post(f'{HOST}/advertisement/',
                     json={
                         'title': 'Куплю диван',
                         'description': 'Рассмотрю угловые, складные и др. виды диванов',
                     })
print(data.json(), '\n')

print('>>> post advertisement with authorization')
data = requests.post(f'{HOST}/advertisement/',
                     json={
                         'title': 'Продам стол',
                         'description': 'Дубовый стол в отличном состоянии',
                     },
                     headers={
                         'user_name': 'Tessa Gray',
                         'token': 'c0fa8f3f-6ed7-4eac-b8e4-79fb16005e69',
                     })
print(data.json(), '\n')

print('>>> get advertisement by id')
data = requests.get(f'{HOST}/advertisement/1/')
print(data.json(), '\n')

print('>>> change advertisement by id with the wrong user and token')
data = requests.put(f'{HOST}/advertisement/1/',
                    json={
                        'title': 'Продам дубовый стол',
                        'description': 'В отличном состоянии'
                    },
                    headers={
                           'user_name': 'Will Herondale',
                           'token': '0efa0717-8f96-4349-8425-a01c89ca5350',
                       })
print(data.json(), '\n')

print('>>> change advertisement by id with owner token')
data = requests.put(f'{HOST}/advertisement/1/',
                    json={
                        'title': 'Продам дубовый стол',
                        'description': 'В отличном состоянии'
                    },
                    headers={
                           'user_name': 'Tessa Gray',
                           'token': 'c0fa8f3f-6ed7-4eac-b8e4-79fb16005e69',
                       })
print(data.json(), '\n')

print('>>> delete advertisement by id with the wrong user and token')
data = requests.delete(f'{HOST}/advertisement/1/',
                       headers={
                           'user_name': 'Will Herondale',
                           'token': '0efa0717-8f96-4349-8425-a01c89ca5350',
                       })
print(data.json(), '\n')

print('>>> delete advertisement by id with authorization')
data = requests.delete(f'{HOST}/advertisement/1/',
                       headers={
                           'user_name': 'Tessa Gray',
                           'token': 'c0fa8f3f-6ed7-4eac-b8e4-79fb16005e69',
                       })
print(data.json(), '\n')
