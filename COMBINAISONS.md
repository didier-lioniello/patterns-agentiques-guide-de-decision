# Combinaisons de production

En production, on compose les patterns. Chaque jonction est un nouveau point de panne : c'est là que les schémas simples ne montrent rien. Les trois architectures ci-dessous sont des **exemples de conception**, pas des retours d'expérience chiffrés.

## A. Support client : routage → LLM augmenté → évaluateur

```mermaid
flowchart TB
    IN["Message client"] --> subR
    subgraph subR["Routage"]
        R{"Classe + confiance"}
    end
    R -- "faible confiance" --> H["Agent humain"]
    R -- "FAQ" --> A1
    R -- "compte client" --> A2
    subgraph subA["LLM augmenté par route"]
        A1["RAG documentation"]
        A2["RAG + outils lecture compte<br/>lecture seule"]
    end
    A1 --> E
    A2 --> E
    subgraph subE["Évaluation"]
        E{"Citations retrouvées dans la source ?<br/>aucune promesse hors politique ?"}
    end
    E -- "ok" --> OUT["Réponse"]
    E -- "échec" --> H
```

| Jonction | Mode de panne | Parade |
|---|---|---|
| Routage → route | Mauvaise route, donc mauvais outils | Seuil de confiance ; les droits dépendent de la route |
| Outil compte → LLM | Injection dans un champ client (nom, note) | Données d'outil délimitées, outils en lecture seule |
| LLM → évaluation | Réponse plausible sans source | Correspondance exacte des citations, sinon humain |
| Global | Taux d'escalade qui dérive | Suivi hebdomadaire par route |

## B. Recherche multi-sources : orchestrateur → parallélisation → évaluateur-optimiseur

```mermaid
flowchart TB
    Q["Question de recherche"] --> O["Orchestrateur : plan de sous-questions"]
    O --> PV{"Plan <= N sous-questions ?"}
    PV -- "non" --> STOP["Rejet"]
    PV -- "oui" --> subP
    subgraph subP["Workers en parallèle"]
        W1["Sous-question 1"]
        W2["Sous-question 2"]
        W3["Sous-question n"]
    end
    subP --> S["Synthèse avec citations"]
    S --> subL
    subgraph subL["Boucle d'évaluation, budget 3 tours"]
        D{"Chaque affirmation a une source<br/>retrouvée mot pour mot ?"}
        J{"Juge : couverture de la question"}
        D -- "ok" --> J
    end
    D -- "non" --> S
    J -- "lacune" --> O
    J -- "ok" --> OUT["Rapport"]
```

| Jonction | Mode de panne | Parade |
|---|---|---|
| Orchestrateur | Sous-questions redondantes, coût multiplié | Plafond, dédoublonnage des sous-questions |
| Workers → synthèse | Fausse corroboration : deux sources reprennent la même origine | Compter les origines, pas les URL |
| Synthèse | Affirmation sans source, lissée par le style | Contrôle déterministe des citations |
| Boucle vers l'orchestrateur | Replanification sans fin | Budget global de tours et de tokens, partagé par toute la chaîne |

## C. Agent de code : routage → agent → contrôles déterministes → humain

```mermaid
flowchart LR
    T["Ticket"] --> R{"Type de ticket"}
    R -- "hors périmètre" --> H1["Humain"]
    R -- "bug reproductible" --> subA
    subgraph subA["Agent en bac à sable"]
        P["Choix d'action"] --> X["Édition, exécution"]
        X --> TST{"Tests"}
        TST -- "échec, budget restant" --> P
    end
    TST -- "budget épuisé" --> H1
    TST -- "succès" --> subC
    subgraph subC["Contrôles avant fusion"]
        L["Lint, typage, tests complets"]
        DIFF{"Diff dans le périmètre ?<br/>aucun test supprimé ?"}
        L --> DIFF
    end
    DIFF -- "non" --> H1
    DIFF -- "oui" --> PR["Pull request<br/>revue humaine obligatoire"]
```

| Jonction | Mode de panne | Parade |
|---|---|---|
| Agent → tests | L'agent « répare » en modifiant ou supprimant le test | Contrôle du diff : tests existants inchangés |
| Agent | Boucle sur le même échec | Détection de répétition, budget de tours |
| Bac à sable | Accès réseau ou secrets | Environnement isolé, sans secrets de production |
| Fusion | Merge automatique d'un correctif plausible mais faux | Revue humaine obligatoire, jamais de fusion par l'agent |

## Règle de composition
Un **budget unique** (tokens, temps, tours) pour toute la chaîne, pas un par composant : sinon les boucles imbriquées multiplient les plafonds entre eux.
