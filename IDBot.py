from bs4 import BeautifulSoup
import requests
import numpy as np
import requests
import urllib.request
import uuid
import json
import time
import datetime
import re

username ='EGarandel@UniqueIDBot'
password ='f8p9j2c0uupfmfntvtvkbkk9t56oqqqk'
homeurl ='http://wikipast.epfl.ch/wikipast/'
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
    page_modified = 0
    source_link = 'http://wikipast.epfl.ch/wiki/Special:Toutes_les_pages'
    source = requests.get(source_link).text
    soup = BeautifulSoup(source, 'lxml')

    while(source_link and page_counter <= 200):
        #On trouve la liste des pages
        pages_body = soup.find('div', class_='mw-allpages-body')
        pages_list = pages_body.find_all('li')

        #Pour chaque page dans la liste de pages, on extrait le liens
        for page in pages_list:
            page_link = page.find('a')['href']
            page_name = page.find('a')['title']

            page_link = f'http://wikipast.epfl.ch{page_link}'

            page_modified = checkAndGenerate(page_link, page_name, edit_cookie, edit_token, page_modified)
            page_counter += 1

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

    return page_counter, page_modified

def checkAndGenerate(link, title, edit_cookie, edit_token, counter):
    '''
        Check if the page contains a identifier :
        - if it is the case, it checks if it's a human and adds a identifier accordingly
        - if is is the case, it skips the page
        (Des expressions régulières sont utilisés afin de reconnaitre les patterns présents sur les pages)
    '''

    payload={'action':'parse', 'format':'json', 'page':title,'prop':'wikitext','formatversion':'2'}
    r4=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
    wikitext = json.loads(r4.text)["parse"]["wikitext"]
    
    has_id = re.search(r"Identifiant Wikipast\s:\s.+\s", wikitext)

    if has_id is not None:
        return counter
    else :    
        wikidata_found = re.search(r"Wikidata: \[.+\s.+\] \(\[https://www.wikidata.org/wiki/Q5 Q5\)\]", wikitext)
        wikidata_not_match_found = re.search(r"Wikidata: \[.+ Match not found\] \(\[https://www.wikidata.org/wiki/Q5 Q5\]\)", wikitext)
        bnf_id = re.search(r"BnF ID: \[.+\s.+\]", wikitext) 
        if (wikidata_found is not None and wikidata_not_match_found is None) or bnf_id is not None:
            return modify_page(generate_text(link), title, edit_cookie, edit_token, counter)

    return counter

def generate_text(link):
    ''' A partir d'un lien URL, génére un identifiant unique'''

    guuid = uuid.uuid5(uuid.NAMESPACE_URL, link)
    return ID_title + str(guuid)+'\n\n'

def modify_page(uuid_text, title, edit_cookie, edit_token, counter):

    '''
        Ajoute l'identifiant en début de page et indique si l'ajout a été un succès ou non (potentiel erreur)
    '''

    payload={'action':'edit','assert':'user','format':'json','utf8':'','title':title,'section':'0', 'prependtext':uuid_text, 'token':edit_token}
    r5=requests.post(homeurl+'api.php',data=payload,cookies=edit_cookie)
    id_added = json.loads(r5.text)["edit"]["result"] == "Success"

    if not id_added:
        print("Erreur de modification pour la page "+ title)
        return counter
    else :
        return counter + 1
        

def main():
    start = time.time()
    counter= 0
    edit_cookie, edit_token,logged_in = login()

    if logged_in:
        print("Connexion réussie : début de la génération des identifiants")
        counter, modification = naviguate(edit_cookie, edit_token)
        end = time.time()
        duration = end - start
        res = datetime.timedelta(seconds =duration)
        print('Fin du progamme : ', counter, ' pages ont été évaluées et ', modification, 'ont été modifiées en ',res)

    else:
        print("Erreur de connexion : vérifier vos identifiants et votre connexion (arrêt du bot)")  

if __name__ == "__main__":
    main()

