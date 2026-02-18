import subprocess
import datetime

class IPBlocker:
    def __init__(self):
        # Liste blanche : IPs qu'on ne bannit JAMAIS (localhost, VPN admin...)
        self.whitelist = ["127.0.0.1", "::1", "localhost"]

    def block_ip(self, ip_address):
        """
        Bloque une IP via UFW (Uncomplicated Firewall)
        """
        # 1. Vérification Whitelist (Safety First !)
        if ip_address in self.whitelist:
            print(f"\033[93m[AVERTISSEMENT] Tentative de bannissement sur IP Whitelistée ({ip_address}) - Action annulée.\033[0m")
            return False

        # 2. Exécution de la commande système
        # Commande équivalente à : sudo ufw deny from 192.168.x.x to any
        print(f"\033[91m[ACTION] Bannissement de l'IP : {ip_address}...\033[0m")

        try:
            cmd = ["ufw", "deny", "from", ip_address, "to", "any"]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)

            # On loggue l'action
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\033[92m[SUCCÈS] IP {ip_address} bannie définitivement par le Firewall à {timestamp}.\033[0m")
            return True

        except subprocess.CalledProcessError as e:
            print(f"\033[91m[ERREUR] Impossible de bannir l'IP : {e}\033[0m")
            return False
