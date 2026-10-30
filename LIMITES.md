# Ce que ce guide ne promet pas

- **Aucun chiffre de performance réel.** Coûts et latences du tableau sont qualitatifs et relatifs. Les chiffres de l'exemple viennent d'un LLM simulé sur un jeu synthétique.
- **Pas de garantie qu'un juge LLM détecte les erreurs.** Il partage souvent les angles morts du générateur ; c'est pourquoi les contrôles déterministes passent avant.
- **Pas de protection complète contre l'injection de prompt.** Les parades décrites (contenu marqué comme donnée, privilèges minimaux, validation hors LLM des actions sensibles) réduisent le risque sans l'éliminer.
- **Pas d'agent « qui s'améliore tout seul ».** Sans jeu d'évaluation figé, modifier ses propres prompts en production, c'est de la dérive.
- **Le multi-agents n'est pas un argument en soi.** Chaque composant en plus doit être justifié par une mesure contre l'alternative plus simple.
- **L'arbre de décision est un point de départ**, pas un algorithme : un cas réel peut justifier une autre branche, à condition de le mesurer.
- **Les diagrammes sont des architectures de référence**, pas des workflows prêts à importer dans un outil donné.
