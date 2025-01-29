### J'ai tout fait en Notebook initialement (voir le fichier notebook), j'ai dû tout mettre au sein d'un module "crawler.py"
### J'ai encapsulé toutes les fonctions comme des méthodes de la classe Crawler


## Youcef Boulfrad, Master STD

# Configuration initiale

## Installation des bibliothèques requises
# pip install requests beautifulsoup4

## Création de la structure du projet

# En bash :
# mkdir -p Web_Crawler
# cd Web_Crawler

# Ouverture du dossier avec VSCODE

# Création d'un Repo GitHub distant, et local, et utilisation des commandes GIT pour le mettre à jour

## Importation des modules nécessaires
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import urllib.robotparser
import json
import re

# Classe Crawler avec toutes les fonctions encapsulées
class Crawler:
    def __init__(self, url_depart, max_pages=50): #Arrêt à 50 pages
        self.url_depart = url_depart
        self.max_pages = max_pages
        self.pages_visitees = set()
        self.pages_a_visiter = [url_depart]
        self.resultats = []

    # Envoyer une requête GET pour télécharger une page HTML
    def telecharger_page(self, url):
        """Télécharge le contenu HTML d'une URL donnée."""
        try:
            en_tetes = {"User-Agent": "Explorateur-ENSAI"}
            reponse = requests.get(url, headers=en_tetes, timeout=5)
            reponse.raise_for_status()
            return reponse.text
        except requests.RequestException as e: # Lever une exception en cas d'échec (après 5 secondes d'attente)
            print(f"Échec du téléchargement {url}: {e}")
            return None

    # Respect d'une seconde de politesse vis à vis du serveur qu'on requête
    def attendre(self):
        """Ajoute un délai pour éviter de surcharger le serveur (politesse)."""
        time.sleep(1)
        
    # Vérification des droits de parsing via robots.txt (pour une URL donnée)
    def autorise_crawl(self, url): 
        """Vérifie si le crawler a le droit de parser une page selon robots.txt."""
        try:
            robot_parser = urllib.robotparser.RobotFileParser()
            domaine = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(url))
            robots_url = urljoin(domaine, "/robots.txt")
            robot_parser.set_url(robots_url)
            robot_parser.read()
            return robot_parser.can_fetch("*", url)
        except Exception as e:
            print(f"Impossible de lire robots.txt sur {url}: {e}")
            return False
    
    ## Fonction pour parser le HTML (c'est à dire extraire les principales informations d'une page HTML)
    def parser_html(self, html, url):
        """Parse le contenu HTML et extrait titre, premier paragraphe et liens."""
        soupe = BeautifulSoup(html, "html.parser")
        titre = soupe.title.string.strip() if soupe.title else "Sans titre" # Extraction du titre
        premier_paragraphe = ""
        paragraphes = soupe.find_all("p")
        if paragraphes:
            premier_paragraphe = paragraphes[0].get_text().strip()          # Extraction du premier paragraphe
        domaine = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(url))
        liens = {}
        for balise_a in soupe.find_all("a", href=True):
            lien = urljoin(url, balise_a["href"])
            if domaine in lien:
                liens[lien] = url                                           # Extraction des liens
        return {"titre": titre, "url": url, "premier_paragraphe": premier_paragraphe, "liens": liens}

    def explorer(self):
        """Parcourt les pages en suivant les liens, priorisant ceux contenant 'product'."""
        while self.pages_a_visiter and len(self.pages_visitees) < self.max_pages:
            url = self.pages_a_visiter.pop(0)
            if url in self.pages_visitees or not self.autorise_crawl(url):
                continue
            print(f"🔍 Exploration de: {url}")
            html = self.telecharger_page(url)
            if not html:
                continue
            contenu = self.parser_html(html, url)
            self.resultats.append(contenu)
            self.pages_visitees.add(url)
            nouveaux_liens = sorted(contenu["liens"].keys(), key=lambda x: "product" not in x) # priorisation des liens contenant "product"
            self.pages_a_visiter.extend(nouveaux_liens)
            self.attendre()
        self.sauvegarder_resultats()
    
    # Ici, pour crawler à partir de plusieurs URL de départ différentes, on stocke les sorties JSON sous des noms différents, en utilisant la bibliothèque "re"
    def sauvegarder_resultats(self):
        identifiant_unique = re.sub(r'[^a-zA-Z0-9]', '_', self.url_depart)[:50]
        nom_fichier = f"resultats_{identifiant_unique}.json"
        with open(nom_fichier, "w", encoding="utf-8") as fichier:
            json.dump(self.resultats, fichier, indent=4, ensure_ascii=False, sort_keys=True)
        print(f"Exploration terminée ! Résultats sauvegardés dans '{nom_fichier}'.")

    # Méthode pour tester (statique pour ne pas dépendre d'une instance de Crawler)
    @staticmethod
    def tester_crawler(url_depart, max_pages):
        try:
            crawler = Crawler(url_depart, max_pages)
            crawler.explorer()
        except Exception as e:
            print(f"Erreur lors du test du crawler : {e}")

# Ici on teste à partir de plusieurs URL de départ différentes, et on se limite à 10 URL par URL de départ, pour réduire le temps d'exploration
if __name__ == "__main__":
    Crawler.tester_crawler("https://web-scraping.dev/products", 10)
    Crawler.tester_crawler("https://ensai.fr", 10)
    Crawler.tester_crawler("https://insee.fr", 10)
    Crawler.tester_crawler("https://le-recensement-et-moi.fr", 10)

print("Tests terminés. Vérifiez les fichiers JSON générés.")

# Rafraichir le dossier Web_Crawler pour voir les 4 fichiers json, chacun avec un nom différent selon son URL de départ

# On remarque que les pages du site Insee.fr continennent beaucoup plus d'URL que les autres sites testés ! 