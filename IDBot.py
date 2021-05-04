from bs4 import BeautifulSoup
import requests
import numpy as np


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
        page_link = f'http://wikipast.epfl.ch{page_link}'
        '''
        Ici il faut coder la fonction pour créer l'id et le mettre dans la nouvelle page. Le liens de la page
        est contenu dans page_link
        '''
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


