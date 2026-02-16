from modules.log_monitor import LogMonitor

# Chemin vers les logs d'accès Apache (standard sur Debian/Ubuntu)
LOG_PATH = "/var/log/apache2/access.log"

def start_sentinelle():
    print("--- 🛡️ SENTINELLE : Active ---")

    try:
        # Initialisation du moniteur
        monitor = LogMonitor(LOG_PATH)

        # Boucle infinie qui attend chaque nouvelle ligne de log
        for log_line in monitor.monitor():
            print(f"[NOUVEAU LOG] {log_line}")

    except FileNotFoundError as e:
        print(f"[ERREUR] {e}")
    except PermissionError:
        print("[ERREUR] Permission refusée. Lancez avec 'sudo'.")

if __name__ == "__main__":
    start_sentinelle()
