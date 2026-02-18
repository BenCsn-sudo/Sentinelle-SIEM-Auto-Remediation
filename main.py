import sys
import time
from modules.log_monitor import LogMonitor
from modules.detector import AttackDetector
from modules.active_response import IPBlocker  # <--- NOUVEAU

# Configuration
LOG_PATH = "/var/log/apache2/access.log"

# Couleurs
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def start_sentinelle():
    print(f"{GREEN}--- 🛡️ SENTINELLE v1.0 : Protection Active ---{RESET}")

    # Initialisation des modules
    monitor = LogMonitor(LOG_PATH)
    detector = AttackDetector()
    blocker = IPBlocker()  # Initialisation du bloqueur

    print(f"{YELLOW}[*] Surveillance des logs : {LOG_PATH}{RESET}")
    print(f"{YELLOW}[*] Pare-feu UFW prêt à intervenir.{RESET}")

    try:
        for log_line in monitor.monitor():
            # 1. Analyse
            alert = detector.analyze(log_line)

            if alert:
                # 2. ALERTE
                print(f"\n{RED}[!!!] MENACE DÉTECTÉE [!!!]{RESET}")
                print(f"{RED} -> TYPE   : {alert['type']}{RESET}")
                print(f"{RED} -> IP     : {alert['ip']}{RESET}")
                print(f" -> Payload : {alert['payload']}")

                # 3. RÉPONSE ACTIVE (Bannissement)
                blocker.block_ip(alert['ip'])

    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Arrêt de Sentinelle.{RESET}")
    except Exception as e:
        print(f"{RED}[ERREUR CRITIQUE] {e}{RESET}")

if __name__ == "__main__":
    start_sentinelle()
