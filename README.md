# ani-fr

**ani-fr** est un outil Python pour regarder et télécharger des épisodes d’anime directement depuis le terminal. Il est simple, rapide et pratique pour les fans d’anime sur Linux.

---

## Installation

Clone le dépôt puis installe avec pip :

```bash
git clone https://github.com/DeiTsukiii/ani-fr.git
cd ani-fr
pip install --user -r requirements.txt
pip install --user .
```

Le script sera alors accessible avec la commande :

```bash
ani-fr
```

---

## Utilisation

```bash
ani-fr
```

---

## Dépendances

* git
* Python 3
* mpv

**Installation:**

* **Ubuntu / Debian** :

  ```bash
  sudo apt update
  sudo apt install python3 python3-pip mpv git -y
  ```
* **Fedora / Red Hat** :

  ```bash
  sudo dnf install python3 python3-pip mpv git -y
  ```
* **Arch Linux** :

  ```bash
  sudo pacman -S python python-pip mpv git
  ```

---

## Mise à jour

Lorsque votre version d'ani-fr n'est pas à jour, vous pouvez mettre à jour facilement depuis Git :

* **Si vous possédez encore le dossier du projet:**
  ```bash
  cd /chemin/vers/ani-fr
  git pull origin main
  pip install --user -r requirements.txt
  pip install --user . --upgrade
  ```

* **Sinon, si vous avez supprimé le dossier:**
  ```bash
  git clone https://github.com/DeiTsukiii/ani-fr.git
  cd ani-fr
  pip install --user -r requirements.txt
  pip install --user . --upgrade
  ```

Si vous ne souhaitez pas la mettre a jour et utiliser ani-fr dans une version obsolète vous pouvez utiliser la commande :

```bash
ani-fr --force
```

Vous pouvez voir votre version de ani-fr en faisant:
```bash
ani-fr --version
```