import re
from urllib.parse import unquote  # <--- AJOUT IMPORTANT

class AttackDetector:
    def __init__(self):
        # Dictionnaire des signatures d'attaques (Regex)
        self.attack_patterns = {
            "SQL_INJECTION": [
                r"UNION\s+SELECT",
                r"OR\s+'1'='1",
                r"Information_Schema",
                r"CONCAT\(",
            ],
            "XSS_CROSS_SITE_SCRIPTING": [
                r"<script>",
                r"javascript:",
                r"onerror=",
            ],
            "PATH_TRAVERSAL": [
                r"\.\./\.\./",
                r"/etc/passwd",
                r"/etc/shadow",
            ],
            "SCANNER_RECON": [
                r"nmap",
                r"nikto",
                r"sqlmap",
            ]
        }

    def analyze(self, log_line):
        """
        Analyse une ligne de log pour trouver une attaque.
        Retourne: (ip_source, type_attaque) ou None
        """
        # 1. Extraction de l'IP sur la ligne brute
        ip_match = re.search(r"^([0-9a-fA-F:.]+)", log_line)

        if not ip_match:
            return None

        ip_source = ip_match.group(1)

        # 2. DÉCODAGE DE L'URL
        # Transforme "%20" en espace, "%27" en guillemet, etc.
        decoded_line = unquote(log_line)

        # 3. Vérification des motifs sur la ligne DÉCODÉE
        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                # On cherche maintenant dans 'decoded_line'
                if re.search(pattern, decoded_line, re.IGNORECASE):
                    return {
                        "ip": ip_source,
                        "type": attack_type,
                        "payload": pattern
                    }

        return None
