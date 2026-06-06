# Contributing to OpenConquest

O projeto é desenvolvido ativamente com auxílio de IA (Vibe Coding Assistido). Para manter a integridade, siga estritamente este fluxo.

## Como Contribuir

Todo o trabalho deve ser isolado por **branch** baseada na `develop`.

```bash
git checkout develop
git checkout -b feature/nome-da-tarefa
```

Quando terminar:
```bash
pytest
git add .
git commit -m "Descrição clara da implementação"
git push -u origin feature/nome-da-tarefa
```

## Branches e Estrutura
- `main`: Código em produção, estável.
- `develop`: Código principal em desenvolvimento.
- `feature/*`: Novas funcionalidades.

Exemplos de branches:
- `feature/api-rooms`
- `feature/database-persistence`
- `feature/websocket-sync`
- `feature/frontend-shell`
- `feature/galaxy-map`

## Regras de Submissão
1. Leia o `README.md` e a documentação na pasta `docs/` antes de alterar código.
2. A arquitetura atual não deve ser reescrita sem necessidade.
3. A `game_engine` (backend) deve continuar pura, testável e sem conhecimento de rede ou banco.
4. Faça mudanças pequenas, testáveis, e **não quebre os testes existentes**.
