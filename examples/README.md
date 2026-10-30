# Exemple : évaluateur-optimiseur avec garde-fous

```bash
python3 examples/evaluateur_optimiseur.py          # compare naïf vs boucle
python3 -m unittest discover -s examples -v        # 7 tests
```

- `evaluateur_optimiseur.py` : boucle générateur → contrôles déterministes → retour, avec budget d'itérations, détection de stagnation et escalade.
- `jeu_eval.json` : jeu **synthétique** de 8 cas ; chaque cas scripte les sorties d'un LLM simulé et leur vérité terrain.
- `test_evaluateur_optimiseur.py` : tests unitaires.

Le cas `c07` est volontairement laissé en échec : l'inversion des parties passe les contrôles déterministes. C'est la limite assumée du pattern, là où un juge sémantique ou une revue humaine par échantillon est nécessaire. Les métriques affichées décrivent ce jeu jouet uniquement.
