# Regras do repositório CELINE

## Segurança e governança

- Não inserir chaves, tokens, senhas, CPF, e-mail pessoal ou conteúdo de mensagens no código ou nos logs.
- Manter o servidor restrito a `127.0.0.1` por padrão.
- Não adicionar chamadas externas fora do registro allowlist ou habilitá-las por padrão.
- Bloquear Gemini por nome, host, caminho e modelo/payload; não contornar essa política.
- Nunca expor um proxy HTTP genérico, seguir redirecionamentos externos ou registrar corpos de requisição/resposta.
- Preservar a trilha de auditoria do Pattern Guard e a redação de campos sensíveis.
- Não representar uma simulação de software como prova de operação de hardware físico.
- O Pulse Lab deve permanecer estritamente em memória: sem áudio, rádio, GPIO, USB, sockets ou emissão física.
- Não afirmar que frequências limpam redes, alinham sistemas ou impedem clonagem sem ensaio independente reproduzível.
- Não alterar ou mesclar diretamente em `main`; usar branch e revisão.

## Validação

- Executar `python -m unittest discover -s tests -v` antes de publicar alterações.
- Acrescentar testes para toda nova rota, política de segurança ou transformação de dados.
