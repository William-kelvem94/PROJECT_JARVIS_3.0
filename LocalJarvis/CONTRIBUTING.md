# Contribuindo para o LocalJarvis

Obrigado por considerar contribuir! Siga estas diretrizes:

## Como Contribuir

1. Fork o repositório.
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`).
3. Faça commit das mudanças (`git commit -m 'Adiciona nova funcionalidade'`).
4. Push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

## Estilo de Código

- Use PEP 8 para Python.
- Adicione comentários claros.
- Inclua testes para novas funcionalidades.

## Testes Automatizados

- Todos os novos recursos devem incluir testes em `tests/`.
- Para rodar os testes em ambiente Docker:

```powershell
# Execute dentro do container core
docker exec -it localjarvis_core_1 pytest tests/
```

- Certifique-se de que todos os testes passem antes de abrir um Pull Request.

## Dicas para Plugins

- Plugins devem ser modulares, com interface `process(self, text)`.
- Use logging avançado (`utils/logger.py`) para depuração.
- Documente exemplos de uso no README ou docstring do plugin.

## Reportar Bugs

Abra uma issue com:
- Descrição do bug.
- Passos para reproduzir.
- Comportamento esperado.

## Licença

Contribuições estão sob a licença MIT.
