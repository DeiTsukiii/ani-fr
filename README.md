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

* **Python 3**
  Vérifie si Python 3 est installé :

  ```bash
  python3 --version
  ```

  Si ce n’est pas le cas :

  * **Ubuntu / Debian** :

    ```bash
    sudo apt update
    sudo apt install python3 python3-pip -y
    ```
  * **Fedora / Red Hat** :

    ```bash
    sudo dnf install python3 python3-pip -y
    ```
  * **Arch Linux** :

    ```bash
    sudo pacman -S python python-pip
    ```

* **mpv**
  Vérifie si mpv est installé :

  ```bash
  mpv --version
  ```

  Si ce n’est pas le cas :

  * **Ubuntu / Debian** :

    ```bash
    sudo apt install mpv -y
    ```
  * **Fedora / Red Hat** :

    ```bash
    sudo dnf install mpv -y
    ```
  * **Arch Linux** :

    ```bash
    sudo pacman -S mpv
    ```
