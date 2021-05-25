from bs4 import BeautifulSoup
import requests
import numpy as np
import requests
import urllib.request
import uuid
import json

username='EGarandel@IDBot'
password='3oa19ucknig3qcb37imc82i1of9oqojr'
homeurl='http://wikipast.epfl.ch/wikipast/'
ID_title = 'Identifiant Wikipast : '
human_text = '[https://www.wikidata.org/wiki/Q5 Q5]'

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

def naviguate(edit_cookie, edit_token):

    page_counter = 0
    source_link = 'http://wikipast.epfl.ch/wiki/Special:Toutes_les_pages'
    source = requests.get(source_link).text
    soup = BeautifulSoup(source, 'lxml')

    while(source_link):
        #On trouve la liste des pages
        pages_body = soup.find('div', class_='mw-allpages-body')
        pages_list = pages_body.find_all('li')

        #Pour chaque page dans la liste de pages, on extrait le liens
        for page in pages_list:
            page_link = page.find('a')['href']
            page_name = page.find('a')['title']

            page_link = f'http://wikipast.epfl.ch{page_link}'

            checkAndGenerate(page_link, page_name, edit_cookie, edit_token)
            page_counter = page_counter + 1


        #On trouve le liens pour la page suivante
        next_page = soup.find('div', class_='mw-allpages-nav')
        next_page = next_page.find_all('a')

        '''
        La première et dernière page sont les seules contenant une seule balise de type <a> <\a> 
        indiquant page suivante ou page précédente. 
        next_page = next_page.find_all('a') est donc de longueur 1 dans ce cas. 
        Dans tous les autres cas, il y a 2 balises de type <a> <\a> pour page suivante et page précédente.
        next_page = next_page.find_all('a') est donc de longueur 2 dans ce cas. 
        '''
        #Si on se trouve sur la première ou dernière page
        if next_page.__len__() == 1:
            # Si c'est la première page, on cherche juste le liens de la page suivante:
            if source_link == 'http://wikipast.epfl.ch/wiki/Special:Toutes_les_pages':
                source_link = f'http://wikipast.epfl.ch{next_page[0]["href"]}'
                print(source_link)
            # Sinon c'est forcemment la dernière page et on peut donc s'arreter
            else:
                print('Dernière page')
                source_link = 0

        # Si on est sur les autres pages
        elif next_page.__len__() == 2:
            source_link = f'http://wikipast.epfl.ch{next_page[1]["href"]}'
            print(source_link)

        # Sinon c'est une erreur
        else:
            print('ERREUR NEXT PAGE')
            quit()

        if source_link != 0:
            #On réinitialise soup pour la page suivante et c'est reparti tant que source_link =!0
            source = requests.get(source_link).text
            soup = BeautifulSoup(source, 'lxml')

    print('Nombre total de page = ', page_counter)

def checkAndGenerate(link, title, edit_cookie, edit_token):
    '''
        Check if the page contains a identifier :
        - if it is the case, it checks if it's a human and adds a identifier accordingly
        - if is is the case, it skips the page
    '''
    payload={'action':'parse', 'format':'json', 'page':title,'prop':'wikitext','formatversion':'2'}
    r4=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
    wikitext = json.loads(r4.text)["parse"]["wikitext"]

    already_id = ID_title in wikitext
    if already_id:
        print("Cette page possède déjà un identifiant")
    else :    
        is_human = human_text in wikitext
        if is_human:
            #modify_page(generate_text(link), title, edit_cookie, edit_token)
            print("Cette page possède un humain")

def generate_text(link):
    ''' A partir d'un lien URL, génére un identifiant unique'''

    guuid = uuid.uuid3(uuid.NAMESPACE_URL, link)
    return ID_title + str(guuid)+'\n\n'

def modify_page(uuid_text, title, edit_cookie, edit_token):

    '''
        Ajoute l'identifiant en début de page et indique si l'ajout a été un succès ou non (potentiel erreur)
    '''

    payload={'action':'edit','assert':'user','format':'json','utf8':'','title':title,'section':'0', 'prependtext':uuid_text, 'token':edit_token}
    r5=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
    id_added = json.loads(r5.text)["edit"]["result"] == "Success"

    if not id_added:
        print("Erreur de modification pour la page "+ title)
    else :
        print("Identifiant ajouté avec succès pour la page "+ title)

def main():
    edit_cookie, edit_token,logged_in = login()

    if logged_in:
        print("Connexion réussie : début de la génération des identifiants")
        naviguate(edit_cookie, edit_token)
    else:
        print("Erreur de connexion : vérifier vos identifiants et votre connexion (arrêt du bot)")  

if __name__ == "__main__":
    main()

