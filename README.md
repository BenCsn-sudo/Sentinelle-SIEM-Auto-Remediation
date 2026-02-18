# 🛡️ Sentinelle : SIEM & Auto-Remédiation (Blue Team)

**Sentinelle** est une sonde de défense active (Mini-SOAR) conçue pour surveiller, détecter et bloquer les intrusions en temps réel sur un serveur Linux.

Contrairement à une analyse de logs classique ("post-mortem"), Sentinelle agit en **temps réel** (Live Forensics) et applique des contre-mesures automatiques via le pare-feu, transformant la détection passive en défense active.

---

## 🏗️ Architecture Technique

Le projet adopte une approche modulaire pour séparer la gestion système, l'analyse et la réponse.

```text
Sentinelle/
├── config/         # Fichiers de configuration (seuils, whitelists)
├── logs/           # Stockage des alertes de sécurité générées
├── modules/        # Cœur du programme Python
│   ├── log_monitor.py      # Ingestion temps réel (équivalent tail -f)
│   ├── detector.py         # Moteur d'analyse (Regex & Decoding)
│   └── active_response.py  # Module de riposte (Pilotage UFW)
├── scripts/        # Scripts Bash d'administration
│   └── hardening.sh        # Script de durcissement préventif
└── main.py         # Point d'entrée et orchestrateur

```

---

## 🔧 Phase 1 : Hardening (Durcissement Système)

Avant même de lancer la surveillance, le serveur doit être "durci" pour réduire sa surface d'attaque native. C'est la base de la défense en profondeur.

* **Fichier :** `scripts/hardening.sh`
* **Langage :** Bash
* **Outils :** `chmod`, `sed`, `ufw`

### 🔒 Actions réalisées par le script :

1. **Verrouillage des fichiers critiques (`/etc/shadow`)**
* **Action :** Application des permissions `600` (lecture/écriture uniquement pour root).
* **Sécurité :** Empêche un utilisateur non privilégié de lire les hachages de mots de passe pour tenter un craquage hors-ligne.


2. **Sécurisation SSH (`sshd_config`)**
* **Action :** `PermitRootLogin no`.
* **Sécurité :** Le compte `root` est la cible n°1 des bots. Le désactiver oblige l'attaquant à deviner un nom d'utilisateur valide avant même d'attaquer le mot de passe.


3. **Pare-feu UFW (Uncomplicated Firewall)**
* **Action :** Activation du Firewall et politique "Deny All" par défaut.
* **Sécurité :** Seuls les ports strictement nécessaires (22/SSH et 80/HTTP) sont ouverts. Tout le reste est bloqué.



---

## 👁️ Phase 2 : Surveillance Temps Réel (Log Monitor)

C'est l'œil de la Sentinelle. Ce module ingère les flux de données brutes instantanément.

* **Fichier :** `modules/log_monitor.py`
* **Concept :** Ingestion de flux (Stream Processing)

### 🔍 Zoom Technique : Optimisation Python

Ce script recrée le comportement de la commande UNIX `tail -f` mais de manière optimisée pour Python :

#### 1. Le positionnement (`f.seek`)

```python
f.seek(0, 2) # (Offset: 0, Whence: Fin du fichier)

```

Au démarrage, le script ignore l'historique (qui peut peser des Go) pour se placer immédiatement à la fin du fichier. Il ne traite que les **nouveaux événements**.

#### 2. Les Générateurs (`yield`)

```python
yield line.strip()

```

L'utilisation de `yield` transforme la fonction en **générateur**. Au lieu de charger tout le fichier en mémoire RAM, le script traite les lignes une par une. Cela rend Sentinelle extrêmement léger, même sur un serveur modeste.

---

## 🧠 Phase 3 : Moteur de Détection (Threat Detection)

Une fois le log ingéré, il doit être compris. Ce module utilise l'analyse sémantique pour repérer les attaques.

* **Fichier :** `modules/detector.py`
* **Technologie :** Expressions Régulières (`regex`) & Encodage URL.

### 🔍 Zoom Technique : La logique d'analyse

Le détecteur effectue un traitement en 3 étapes critiques pour éviter les faux négatifs :

#### 1. Normalisation & Décodage

Les attaquants masquent souvent leurs payloads en les encodant. Une attaque `OR '1'='1` devient `OR%20%271%27%3D%271` dans les logs bruts.

```python
# Transformation de "%20" en " " (Espace)
decoded_line = unquote(log_line)

```

Sentinelle décode l'URL **avant** l'analyse. C'est ce qui rend la détection robuste face aux tentatives d'évasion basiques.

#### 2. Pattern Matching (Signatures)

Le moteur compare la ligne nettoyée à une base de signatures Regex :

* **SQL Injection (SQLi) :** `UNION SELECT`, `OR '1'='1`.
* **XSS :** Balises `<script>`, attributs `onerror=`.
* **Path Traversal (LFI) :** Tentatives de remontée `../../etc/passwd`.
* **Reconnaissance :** Détection des outils de scan (Nmap, Nikto, Sqlmap).

---

## 🛡️ Phase 4 : Auto-Remédiation (Active Response)

C'est la différence entre un IDS (Détection) et un IPS (Prévention). Sentinelle agit physiquement sur le réseau pour neutraliser la menace.

* **Fichier :** `modules/active_response.py`
* **Technologie :** Interaction système via `subprocess`.

### 🔍 Zoom Technique : Le bannissement

#### 1. Interaction avec le Pare-feu

Python ne peut pas bloquer une IP nativement. Il pilote l'outil système :

```python
cmd = ["ufw", "deny", "from", ip_address, "to", "any"]
subprocess.run(cmd, check=True)

```

L'attaquant est coupé du réseau instantanément (Couche 3/4).

#### 2. Sécurité (Whitelist / Fail-Safe)

```python
self.whitelist = ["127.0.0.1", "::1", "localhost"]
if ip_address in self.whitelist:
    return False

```

**Mécanisme vital :** Avant toute action, le script vérifie si l'IP est dans une liste blanche. Cela empêche le système de bannir ses propres administrateurs ou l'interface locale en cas de faux positif, évitant un Déni de Service auto-infligé.

---

## 🚀 Installation & Utilisation

### Prérequis

* Linux (Debian/Ubuntu recommandé pour `apt` et `ufw`).
* Python 3.8+.
* Apache2 (Cible de test) : `sudo apt install apache2`.

### 1. Installation et Hardening

```bash
# Cloner le repo
git clone https://github.com/VOTRE-USERNAME/Sentinelle.git
cd Sentinelle

# Rendre les scripts exécutables
chmod +x scripts/hardening.sh

# Lancer le durcissement (Requiert Root)
sudo ./scripts/hardening.sh

```

### 2. Démarrage de la Sonde

```bash
# Sudo est nécessaire pour lire /var/log/apache2/access.log
sudo python3 main.py

```

---

## ⚔️ Démonstration (Proof of Concept)

Pour tester l'efficacité de Sentinelle, ouvrez un second terminal (l'attaquant) et lancez les commandes suivantes :

### Test 1 : Path Traversal

Tentative d'accès aux fichiers système sensibles.

```bash
curl "http://localhost/index.php?page=../../../../etc/passwd"

```

🚨 **Résultat :** Alerte `PATH_TRAVERSAL` détectée.

### Test 2 : Injection SQL (SQLi)

Tentative de contournement d'authentification (encodée pour simuler un navigateur réel).

```bash
curl "http://localhost/login.php?user=admin%27%20OR%20%271%27=%271"

```

🚨 **Résultat :** Alerte `SQL_INJECTION` détectée grâce au moteur de décodage.

### Test 3 : Bannissement Actif

*Note : Si vous testez depuis `localhost` (127.0.0.1), l'action sera bloquée par la sécurité Whitelist.*

**Sortie console attendue :**

```text
[!!!] MENACE DÉTECTÉE [!!!]
 -> TYPE    : SQL_INJECTION
 -> IP      : 127.0.0.1
 -> Payload : OR\s+'1'='1
[AVERTISSEMENT] Tentative de bannissement sur IP Whitelistée (127.0.0.1) - Action annulée.

```

---

*Projet réalisé dans un cadre éducatif pour démontrer les concepts de Blue Teaming, de développement d'outils de sécurité et de DevSecOps.*
