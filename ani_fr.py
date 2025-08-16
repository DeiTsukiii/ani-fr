#!/usr/bin/env python3
import requests
import subprocess
from bs4 import BeautifulSoup
from InquirerPy import prompt
import re
import sys
import time
from platformdirs import user_downloads_dir
import argparse

BASE_URL = "https://anime-sama.fr"
version = 1.2
last_version_url = "https://raw.githubusercontent.com/DeiTsukiii/ani-fr/refs/heads/main/ani_fr.py"
anime_sama_headers = {
    "host": "anime-sama.fr",
    "connection": "keep-alive",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://anime-sama.fr/catalogue/",
    "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
}

sibnet_headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "accept-language": "en-US,en;q=0.5",
    "connection": "keep-alive",
    "range": "bytes=0-",
    "accept-encoding": "identity",
    "referer": "https://video.sibnet.ru/",
}

def check_updates():
    try:
        content = requests.get(last_version_url).text
        match = re.search(r'^version\s*=\s*([0-9.]+)', content, re.MULTILINE)
        if match:
            last_version = float(match.group(1))
            return last_version > version
        else:
            print("Impossible de trouver la version sur GitHub")
            return None
    except Exception as e:
        print(f"Erreur lors de la requête : {str(e)}")
        return None

def search_anime(query=""): 
    try:
        url = "https://anime-sama.fr/catalogue/"
        querystring = {"search": query, "type[]": "Anime", "langue[]": "VF"}
        response = requests.get(url, headers=anime_sama_headers, params=querystring)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        result = []
        for card in soup.find_all('a', href=True):
            titre = None
            titre_tag = card.find('h1', class_='text-white font-bold uppercase text-md line-clamp-2')
            if titre_tag:
                titre = titre_tag.text.strip()
            if titre and 'catalogue' in card['href']:
                result.append({'name': titre, 'url': card['href']})
        return result
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du catalogue : {e}")
        print(f"Exception complète: {str(e)}")
        return [], []
    
def get_seasons(url):
    html_content = requests.get(url, headers=anime_sama_headers).text
    seasons = []
    pattern = r'panneauAnime\("([^"]+)",\s*"([^"]+)"\)'
    matches = re.findall(pattern, html_content)
    if not matches:
        return []
    for name, path in matches:
        if "film" not in name.lower() and name.lower() != "nom":
            seasons.append({
                'name': name,
                'url': path
            })
    return seasons

def get_langues(url):
    try:
        content = requests.get(url, headers=anime_sama_headers).text
        soup = BeautifulSoup(content, "html.parser")
        langues = []
        for a in soup.find_all("a", href=True):
            match = re.search(r"\.\./(vf\d*|vostfr)/?$", a["href"])
            if match:
                lang_path = a["href"].replace("../", "")
                full_url = url.replace("vostfr", lang_path)

                if requests.head(full_url).status_code != 404:
                    langues.append(lang_path)
        return langues
    except Exception as e:
        print(f"Erreur lors de la requête : {str(e)}")
        return None

def get_filever(url):
    try:
        content = requests.get(url, headers=anime_sama_headers).text
        pattern = r'episodes\.js\?filever=(\d+)'
        match = re.search(pattern, content)
        if match:
            filever = match.group(1)
            return filever
        return None
    except Exception as e:
        print(f"Erreur lors de la requête : {str(e)}")
        return None
    
def get_anime_episode(complete_url, filever):
    complete_url = complete_url.replace('https://', '')
    url = f"https://{complete_url}/episodes.js"
    try:
        response = requests.get(url, params={"filever": filever})
        response.raise_for_status()
        content = response.text
        sibnet_links = {}
        matches = re.finditer(r'https://video\.sibnet\.ru/shell\.php\?videoid=(\d+)', content)
        sibnet_links = {str(i): match.group(1) for i, match in enumerate(matches, 1)}
        return sibnet_links
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des épisodes : {e}")
        return {}
    
def get_video_url(video_id):
    try:
        url = "https://video.sibnet.ru/shell.php"
        response = requests.get(url, headers=anime_sama_headers, params={"videoid": video_id})
        response.raise_for_status()
        html_content = response.text
        match = re.search(r'player\.src\(\[\{src: "/v/([^/]+)/', html_content)
        if match:
            video_hash = match.group(1)
            url_sibnet = f"https://video.sibnet.ru/v/{video_hash}/{video_id}.mp4"
            response_sibnet = requests.get(url_sibnet, headers=sibnet_headers, allow_redirects=False)
            if response_sibnet.status_code == 302:
                return response_sibnet.headers['Location']
            else:
                print(f"Status code inattendu : {response_sibnet.status_code}")
        else:
            print("Pattern non trouvé dans le HTML")
        return None
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de l'URL vidéo : {e}")
        return None

def download_episode(url, filename="episode.mp4"):
    try:
        response = requests.get(url, headers=sibnet_headers, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        bar_length = 20
        start_time = time.time()
        
        with open(f"{user_downloads_dir()}/{filename}", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    percent = downloaded / total_size
                    filled_length = int(bar_length * percent)
                    bar = '=' * filled_length + '_' * (bar_length - filled_length)
                    
                    elapsed = time.time() - start_time
                    speed = downloaded / 1024 / elapsed
                    remaining = (total_size - downloaded) / 1024 / speed if speed > 0 else 0
                    
                    sys.stdout.write(
                        f"\r[{bar}] {percent*100:.1f}% - {downloaded/1024/1024:.2f} Mo / {total_size/1024/1024:.2f} Mo "
                        f"({speed:.1f} Ko/s, temps restant : {remaining:.1f}s)  "
                    )
                    sys.stdout.flush()
        
        print(f"\nTéléchargement terminé : {user_downloads_dir()}/{filename}")
    
    except Exception as e:
        print(f"\nErreur lors du téléchargement : {e}")
    
def handle_actions(video_url, episodes, current_ep, player, anime_name, season, langue):
    ep_nums = sorted(episodes.keys(), key=lambda x: int(x))
    current_index = ep_nums.index(current_ep)

    while True:
        action_prompt = [
            {
                "type": "list",
                "name": "choix",
                "message": "Sélectionne une action :",
                "choices": []
            }
        ]

        actions_map = {}

        if current_index + 1 < len(ep_nums):
            action_prompt[0]["choices"].append("⏭️  Épisode suivant")
            actions_map["⏭️  Épisode suivant"] = "next"

        if current_index > 0:
            action_prompt[0]["choices"].append("⏮️  Épisode précédent")
            actions_map["⏮️  Épisode précédent"] = "last"

        action_prompt[0]["choices"].append("⬇️  Télécharger l'épisode")
        actions_map["⬇️  Télécharger l'épisode"] = "download"

        action_prompt[0]["choices"].append("❌ Quitter")
        actions_map["❌ Quitter"] = "quit"

        chosen_action = prompt(action_prompt)
        choice = actions_map[chosen_action["choix"]]
        
        if choice == "next":
            player.terminate()
            current_index += 1
            next_ep_id = episodes[ep_nums[current_index]]
            next_video_url = get_video_url(next_ep_id)
            if next_video_url.startswith('//'):
                next_video_url = 'https:' + next_video_url
            player = subprocess.Popen(['mpv', next_video_url, '--fullscreen'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Lecture de l'épisode {ep_nums[current_index]}")
        
        elif choice == "last":
            player.terminate()
            current_index -= 1
            prev_ep_id = episodes[ep_nums[current_index]]
            prev_video_url = get_video_url(prev_ep_id)
            if prev_video_url.startswith('//'):
                prev_video_url = 'https:' + prev_video_url
            player = subprocess.Popen(['mpv', prev_video_url, '--fullscreen'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Lecture de l'épisode {ep_nums[current_index]}")
        
        elif choice == "download":
            print("Téléchargement en cours...")
            download_episode(video_url, f"ani-fr - {anime_name} - {season} - Episode {current_index + 1} - {langue}.mp4")
        
        elif choice == "quit":
            print("Fermeture du lecteur...")
            player.terminate()
            break

def main():
    parser = argparse.ArgumentParser(description="Téléchargeur d'anime en Français.")
    parser.add_argument("-v", "--version", action="store_true", help="Afficher la version du script")
    parser.add_argument("-f", "--force", action="store_true", help="Force le lancement d'une version obsolète")
    args = parser.parse_args()

    if args.version:
        print(f"ani-fr version {version}")
        return
    
    if check_updates() and not args.force:
        print("Votre version de ani-fr n'est pas a jour.")
        print("\nSi vous souhaitez la mettre a jour:")
        print("git clone https://github.com/DeiTsukiii/ani-fr.git")
        print("cd ani-fr")
        print("pip install --user -r requirements.txt")
        print("pip install --user . --upgrade")
        print("\nSinon vous pouvez faire:")
        print("ani-fr --force")
        return
    
    query = input("🔎 Nom de l'animé : " + "\033[38;2;97;175;239m")
    print("\033[0m", end="")

    search = search_anime(query.strip())

    if not search:
        print("Aucun résultat trouvé.")
        return
    
    animes_prompt = [
        {
            "type": "list",
            "name": "choix",
            "message": "Sélectionne un anime :",
            "choices": [r['name'] for r in search]
        }
    ]
    chosen_anime = prompt(animes_prompt)
    anime_name = chosen_anime['choix']
    anime_url = next(r['url'] for r in search if r['name'] == anime_name).strip()

    seasons = get_seasons(anime_url)
    if not seasons:
        print("Aucune saison trouvée.")
        return
    
    seasons_prompt = [
        {
            "type": "list",
            "name": "choix",
            "message": "Sélectionne une saison :",
            "choices": [r['name'] for r in seasons]
        }
    ]
    chosen_season = prompt(seasons_prompt)
    season_name = chosen_season['choix']
    season_url = next(r['url'] for r in seasons if r['name'] == season_name)

    complete_url = anime_url.rstrip('/') + '/' + season_url.lstrip('/')

    langues = get_langues(complete_url)
    if not langues:
        print("Aucune langues trouvée.")
        return
    
    langues_prompt = [
        {
            "type": "list",
            "name": "choix",
            "message": "Sélectionne une langue :",
            "choices": [r for r in langues]
        }
    ]
    chosen_langue = prompt(langues_prompt)
    complete_url = complete_url.replace('vostfr', chosen_langue['choix'])
    
    filever = get_filever(complete_url)
    episodes = get_anime_episode(complete_url, filever)

    if not episodes:
        print("Aucun épisode trouvé.")
        return

    episodes_prompt = [
        {
            "type": "list",
            "name": "choix",
            "message": "Sélectionne un épisode :",
            "choices": [f"Épisode {num}" for num in episodes.keys()]
        }
    ]
    chosen_episode = prompt(episodes_prompt)
    ep_num = chosen_episode['choix'].split()[-1]
    ep_id = episodes[ep_num]
    
    video_url = get_video_url(ep_id)

    if not video_url:
        print("Impossible de récupérer l'URL de la vidéo.")
        return
    
    if video_url.startswith('//'):
        video_url = 'https:' + video_url

    print(f"Lecture de la vidéo avec mpv...")
    try:
        player = subprocess.Popen(['mpv', video_url, '--fullscreen'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
    except FileNotFoundError:
        print("Erreur : mpv n'est pas installé.")
    except Exception as e:
        print(f"Erreur lors de la lecture : {e}")

    handle_actions(video_url, episodes, ep_num, player, anime_name, season_name, chosen_langue['choix'])

if __name__ == "__main__":
    main()