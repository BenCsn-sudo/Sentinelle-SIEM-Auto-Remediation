import time
import os

class LogMonitor:
    def __init__(self, log_file):
        self.log_file = log_file
        self._check_file()

    def _check_file(self):
        if not os.path.exists(self.log_file):
            raise FileNotFoundError(f"Le fichier de log {self.log_file} n'existe pas.")

    def monitor(self):
        """
        Générateur qui lit le fichier en temps réel (façon tail -f)
        """
        print(f"[*] Surveillance démarrée sur : {self.log_file}")

        try:
            with open(self.log_file, 'r') as f:
                # On va directement à la fin du fichier pour ne lire que les NOUVEAUX logs
                f.seek(0, 2)

                while True:
                    line = f.readline()
                    if not line:
                        # Si pas de nouvelle ligne, on attend un peu
                        time.sleep(0.1)
                        continue

                    # On retourne la ligne nettoyée (sans les sauts de ligne)
                    yield line.strip()

        except KeyboardInterrupt:
            print("\n[!] Arrêt de la surveillance.")
