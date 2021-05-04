import requests
import urllib.request
from bs4 import BeautifulSoup
import uuid



''' Login the bot and return the base url to be used in future requests'''

username='xxx'
password='xxx'
homeurl='http://wikipast.epfl.ch/wikipast/'

payload={'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
r1=requests.post(homeurl + 'api.php', data=payload)
login_token=r1.json()['query']['tokens']['logintoken']
payload={'action':'login','format':'json','utf8':'','lgname':username,'lgpassword':password,'lgtoken':login_token}
r2=requests.post(homeurl + 'api.php', data=payload, cookies=r1.cookies)

print(r2.text)

params3='?format=json&action=query&meta=tokens&continue='
r3=requests.get(homeurl + 'api.php' + params3, cookies=r2.cookies)

edit_token=r3.json()['query']['tokens']['csrftoken']

edit_cookie=r2.cookies.copy()
edit_cookie.update(r3.cookies)

def generate_text(link):
    uuid = uuid.uuid3(uuid.NAMESPACE_URL, link)
    return 'Clé identifiant unique de la page : ' + str(uuid)

def modifyPage(uuid_text, title):
    payload={'action':'edit','assert':'user','format':'json','utf8':'','title':title,'section:':'new','sectiontitle':'UUID de la page','text':uuid_text, 'token':edit_token}
    r4=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
    print(r4.text)
    print('Modification dans '+ title +' : ajout de l\'identifiant')
