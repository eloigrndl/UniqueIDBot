import requests
import urllib.request
from bs4 import BeautifulSoup
import uuid
import json
import spacy

username='EGarandel@IDBot'
password='3oa19ucknig3qcb37imc82i1of9oqojr'
homeurl='http://wikipast.epfl.ch/wikipast/'
ID_title = 'Identifiant Wikipast : '

def login():
    ''' Connecte le bot à Wikipast et retourne les données requises pour les prochaines requêtes'''

    payload={'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
    r1=requests.post(homeurl + 'api.php', data=payload)

    login_token=r1.json()['query']['tokens']['logintoken']
    payload={'action':'login','format':'json','utf8':'','lgname':username,'lgpassword':password,'lgtoken':login_token}
    r2=requests.post(homeurl + 'api.php', data=payload, cookies=r1.cookies)

    params3='?format=json&action=query&meta=tokens&continue='
    r3=requests.get(homeurl + 'api.php' + params3, cookies=r2.cookies)

    edit_token=r3.json()['query']['tokens']['csrftoken']

    edit_cookie=r2.cookies.copy()
    edit_cookie.update(r3.cookies)
    json_data = json.loads(r2.text)

    return edit_cookie, edit_token, json_data["login"]["result"] == "Success"

def generate_text(link):
    ''' A partir d'un lien URL, génére un identifiant unique'''

    guuid = uuid.uuid3(uuid.NAMESPACE_URL, link)
    return ID_title + str(guuid)+'\n\n'

def modifyPage(uuid_text, title, edit_cookie, edit_token):

    '''
        Vérifie si la page contient déjà un identifiant Wikipast :
        - si c'est le cas, elle l'indique à l'utilisateur et n'ajoute donc rien
        - si ce n'est pas le cas, elle ajoute l'identifiant en début de page et indique si l'ajout a été un succès ou non (potentiel erreur)
    '''

    payload={'action':'parse', 'format':'json', 'page':title,'prop':'wikitext','formatversion':'2'}
    r4=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
    already_id = ID_title in json.loads(r4.text)["parse"]["wikitext"]

    if already_id:
        print("Cette page possède déjà un identifiant")
    else:

        payload={'action':'edit','assert':'user','format':'json','utf8':'','title':title,'section':'0', 'prependtext':uuid_text, 'token':edit_token}
        r5=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
        id_added = json.loads(r5.text)["edit"]["result"] == "Success"

        if not id_added:
            print("Erreur de modification pour la page "+ title)
        else :
            print("Identifiant ajouté avec succès pour la page "+ title)

def checkIfEntity(title):
    return 1

    

def main():
    edit_cookie, edit_token,logged_in = login()

    if not logged_in:
        print("Erreur de connexion : vérifier vos identifiants et votre connexion (arrêt du bot)")
        return

    print("Connexion réussie : le bot va créer ajouter des identifiants\n")
    uuid_text = generate_text("http://wikipast.epfl.ch/wiki/Bacasable")
    modifyPage(uuid_text, "Bacasable", edit_cookie, edit_token)
    '''
    payload={'action':'parse', 'format':'json', 'page':'(en) Martine Rassineux','prop':'wikitext','formatversion':'2'}
    r4=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
    print(json.loads(r4.text)["parse"]["wikitext"])

'''

if __name__ == "__main__":
    main()
