#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[*] Démarrage du Hardening Serveur Linux...${NC}"

# 1. Sécurisation des fichiers critiques
echo -e "${GREEN}[+] Vérification des permissions fichiers critiques...${NC}"

# /etc/shadow ne doit être lisible que par root
chmod 600 /etc/shadow
if [ $? -eq 0 ]; then
    echo -e "    -> /etc/shadow sécurisé (600)"
else
    echo -e "${RED}    -> Erreur sur /etc/shadow${NC}"
fi

# /etc/passwd doit être lisible par tous mais inscriptible que par root
chmod 644 /etc/passwd
echo -e "    -> /etc/passwd sécurisé (644)"

# 2. Sécurisation SSH (Désactivation Root Login & Password Auth)
# Attention : Assure-toi d'avoir ta clé SSH configurée avant de lancer ça sur un vrai serveur distant !
SSH_CONFIG="/etc/ssh/sshd_config"

echo -e "${GREEN}[+] Durcissement de la configuration SSH...${NC}"

if [ -f "$SSH_CONFIG" ]; then
    # Sauvegarde de config
    cp $SSH_CONFIG "$SSH_CONFIG.bak"
    
    # Désactiver le login root
    sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' $SSH_CONFIG
    sed -i 's/^#PermitRootLogin prohibit-password/PermitRootLogin no/' $SSH_CONFIG
    
    # Désactiver l'authentification par mot de passe (Optionnel pour le test, décommente si tu as des clés)
    # sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' $SSH_CONFIG
    
    echo -e "    -> Login Root désactivé."
    echo -e "    -> Backup de config créé ($SSH_CONFIG.bak)"
    
    # Redémarrage du service SSH pour appliquer
    service ssh restart
    echo -e "    -> Service SSH redémarré."
else
    echo -e "${RED}[!] Fichier de config SSH introuvable !${NC}"
fi

# 3. Configuration Firewall de base (UFW)
echo -e "${GREEN}[+] Configuration du Pare-feu UFW...${NC}"
# On installe UFW si pas présent
apt-get install ufw -y > /dev/null

# On autorise SSH (sinon on se bloque dehors !)
ufw allow ssh
# On autorise le Web
ufw allow http
ufw allow https

# On active le pare-feu
# Note: 'echo y' permet de valider automatiquement la confirmation
echo "y" | ufw enable

echo -e "${GREEN}[*] Hardening terminé. Le serveur est plus robuste.${NC}"
