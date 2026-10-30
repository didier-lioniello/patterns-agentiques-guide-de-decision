"""Tests (unittest, sans dépendance) : python3 -m unittest discover -s examples"""
import json
import os
import unittest

import evaluateur_optimiseur as eo

ICI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ICI, "jeu_eval.json"), encoding="utf-8") as f:
    JEU = json.load(f)
CAS = {c["id"]: c for c in JEU["cas"]}
M = JEU["max_mots"]


class Tests(unittest.TestCase):
    def test_controle_valeur_inventee(self):
        e = eo.controles_deterministes("Facture pour 880 EUR", "Facture pour 830 EUR", M)
        self.assertIn("valeur manquante: 830", e)
        self.assertIn("valeur absente de la source: 880", e)

    def test_budget_jamais_depasse(self):
        for c in JEU["cas"]:
            r = eo.boucle_avec_garde_fous(c, M, max_iter=3)
            self.assertLessEqual(r["appels"], 3)

    def test_oscillation_detectee(self):
        r = eo.boucle_avec_garde_fous(CAS["c05-oscillation"], M)
        self.assertEqual((r["statut"], r["raison"]), ("escalade", "stagnation"))

    def test_budget_epuise(self):
        r = eo.boucle_avec_garde_fous(CAS["c06-jamais-bon"], M)
        self.assertEqual((r["statut"], r["raison"]), ("escalade", "budget"))

    def test_correction_apres_retour(self):
        r = eo.boucle_avec_garde_fous(CAS["c03-montant-invente"], M)
        self.assertEqual(r["statut"], "accepte")
        self.assertTrue(r["sortie"]["correct"])
        self.assertEqual(r["iterations"], 2)

    def test_limite_assumee_inversion_des_parties(self):
        # Le contrôle déterministe ne voit pas l'inversion des parties : erreur silencieuse
        # attendue, c'est le rôle d'un juge ou d'une revue humaine.
        r = eo.boucle_avec_garde_fous(CAS["c07-faux-mais-verifiable-nulle-part"], M)
        self.assertEqual(r["statut"], "accepte")
        self.assertFalse(r["sortie"]["correct"])

    def test_boucle_moins_d_erreurs_silencieuses_que_naif(self):
        n = eo.metriques([eo.naif(c) for c in JEU["cas"]])
        b = eo.metriques([eo.boucle_avec_garde_fous(c, M) for c in JEU["cas"]])
        self.assertLess(b["erreurs_silencieuses"], n["erreurs_silencieuses"])


if __name__ == "__main__":
    unittest.main()
