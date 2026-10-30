#!/usr/bin/env python3
"""Pattern évaluateur-optimiseur avec garde-fous, sur un LLM SIMULÉ.

Garde-fous montrés :
  1. contrôles déterministes AVANT tout juge (valeurs de la source, longueur) ;
  2. budget dur d'itérations ;
  3. détection de stagnation / oscillation (même sortie déjà vue -> arrêt) ;
  4. arrêt avec escalade et meilleur candidat, jamais d'acceptation par défaut.

Comparé à une variante naïve : une génération, un juge complaisant qui accepte
toute sortie non vide. Python 3.8+, aucune dépendance. Jeu : jeu_eval.json (synthétique).
"""
import json
import os
import re
import sys

VALEUR = re.compile(r"\d{4}-\d{2}-\d{2}|\d+(?:[.,]\d+)?")


class LLMSimule:
    """Rejoue les sorties scriptées d'un cas, une par appel (ignore le retour, comme un mauvais modèle)."""

    def __init__(self, sorties):
        self.sorties = sorties
        self.appels = 0

    def generer(self, retour=None):
        s = self.sorties[min(self.appels, len(self.sorties) - 1)]
        self.appels += 1
        return s


def controles_deterministes(texte, source, max_mots):
    """Retourne la liste des erreurs précises (vide = ok)."""
    erreurs = []
    attendues = set(VALEUR.findall(source))
    trouvees = set(VALEUR.findall(texte))
    for v in sorted(attendues - trouvees):
        erreurs.append("valeur manquante: " + v)
    for v in sorted(trouvees - attendues):
        erreurs.append("valeur absente de la source: " + v)
    n = len(texte.split())
    if n > max_mots:
        erreurs.append("trop long: %d mots > %d" % (n, max_mots))
    return erreurs


def boucle_avec_garde_fous(cas, max_mots, max_iter=3):
    llm = LLMSimule(cas["sorties"])
    vus = set()
    meilleur, meilleur_nb = None, None
    retour = None
    for i in range(1, max_iter + 1):
        sortie = llm.generer(retour)
        texte = sortie["texte"]
        if texte in vus:
            return {"statut": "escalade", "raison": "stagnation", "iterations": i,
                    "appels": llm.appels, "sortie": meilleur}
        vus.add(texte)
        erreurs = controles_deterministes(texte, cas["source"], max_mots)
        if meilleur_nb is None or len(erreurs) < meilleur_nb:
            meilleur, meilleur_nb = sortie, len(erreurs)
        if not erreurs:
            # Ici viendrait un juge LLM pour les critères non vérifiables par code.
            return {"statut": "accepte", "iterations": i, "appels": llm.appels, "sortie": sortie}
        retour = erreurs
    return {"statut": "escalade", "raison": "budget", "iterations": max_iter,
            "appels": llm.appels, "sortie": meilleur}


def naif(cas):
    llm = LLMSimule(cas["sorties"])
    sortie = llm.generer()
    statut = "accepte" if sortie["texte"].strip() else "escalade"  # juge complaisant
    return {"statut": statut, "iterations": 1, "appels": llm.appels, "sortie": sortie}


def metriques(resultats):
    n = len(resultats)
    acc = [r for r in resultats if r["statut"] == "accepte"]
    return {
        "taches": n,
        "succes": sum(1 for r in acc if r["sortie"]["correct"]),
        "erreurs_silencieuses": sum(1 for r in acc if not r["sortie"]["correct"]),
        "escalades": n - len(acc),
        "appels_llm_total": sum(r["appels"] for r in resultats),
        "appels_llm_max": max(r["appels"] for r in resultats),
    }


def main():
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jeu_eval.json")
    with open(chemin, encoding="utf-8") as f:
        jeu = json.load(f)
    max_mots = jeu["max_mots"]
    res_naif, res_boucle = [], []
    print("%-36s %-22s %s" % ("cas", "naïf", "boucle avec garde-fous"))
    for cas in jeu["cas"]:
        a, b = naif(cas), boucle_avec_garde_fous(cas, max_mots)
        res_naif.append(a)
        res_boucle.append(b)
        def lib(r):
            if r["statut"] == "accepte":
                return "accepté " + ("(correct)" if r["sortie"]["correct"] else "(FAUX)")
            return "escalade (%s, %d it.)" % (r.get("raison", "-"), r["iterations"])
        print("%-36s %-22s %s" % (cas["id"], lib(a), lib(b)))
    print("\nMétriques (jeu SYNTHÉTIQUE, LLM simulé : n'a aucune valeur de benchmark)")
    for nom, res in (("naïf", res_naif), ("boucle", res_boucle)):
        print("  %-7s %s" % (nom, json.dumps(metriques(res), ensure_ascii=False)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
