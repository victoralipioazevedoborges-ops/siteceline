# CELINE

Núcleo Python local do ecossistema **CELINE**, acoplando a topologia GENESYS 1
aos módulos Luma, Arcana, Zion, Teazer, Pattern Guard e Pulse Lab.

## Estado funcional

- **CELINE**: orquestração e diagnóstico do ecossistema.
- **LUMA**: análise determinística local, pronta para receber um provedor de
  modelo em etapa posterior.
- **ARCANA**: desafio-resposta HMAC-SHA256, de uso único e com expiração.
- **ZION**: roteamento auditável entre as torres 7 e 12.
- **TEAZER**: abertura e encerramento explícito de sessões efêmeras locais.
- **PATTERN GUARD**: limite de corpo, limite de requisições, acesso loopback e
  auditoria com redação de campos sensíveis.
- **PULSE LAB**: sinal digital contínuo de 9.847/9.874 Hz, plano de dispersão
  pelos 13 nós conhecidos e selo de integridade Arcana, sem emissão física.

O MVP não usa bibliotecas de terceiros. A API escuta apenas em `127.0.0.1` por
padrão. Saídas externas são desabilitadas por padrão e só funcionam após a
habilitação individual de um destino fixo.

## Divergência preservada

O commit inicial declara **19 microchips**, mas fornece uma sequência de **13
elementos**. O núcleo reporta a lacuna de seis componentes e não inventa nomes
ou propriedades ausentes da fonte. O fluxo documentado entre as posições 7 e
12 permanece funcional.

## Pulse Lab: 9.847 e 9.874 Hz

O Pulse Lab soma duas senoides digitais de **9.847 Hz** e **9.874 Hz** com taxa
de amostragem de 48 kHz. A diferença produz batimento matemático de **27 Hz** e
a frequência central é 9.860,5 Hz. Blocos sucessivos preservam a fase porque o
gerador usa um índice absoluto de amostra.

O resultado existe somente como números em memória e hash PCM16. O módulo não
abre áudio, rádio, GPIO, USB, socket ou interface de rede. A dispersão é um
plano lógico para todos os 13 nós conhecidos; não é broadcast IP nem emissão
eletromagnética. A assinatura HMAC-SHA256 da Arcana comprova integridade e
origem local quando a chave está protegida, mas não torna um prompt incopiável.

Detalhes e critérios de ensaio: [`docs/FREQUENCIAS_9847_9874.md`](docs/FREQUENCIAS_9847_9874.md).

## Executar

Requer Python 3.11 ou superior.

```bash
python -m celine
```

A API ficará disponível em `http://127.0.0.1:8787`.

## Rotas

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/health` | Estado do ecossistema e diagnóstico da malha |
| GET | `/modules` | Módulos acoplados |
| GET | `/mesh` | Topologia e invariáveis |
| GET | `/audit` | Últimos eventos redigidos do Pattern Guard |
| GET | `/connectors` | Política e estado dos conectores, sem valores de credenciais |
| GET | `/pulse-lab` | Perfil matemático e plano de dispersão lógica |
| POST | `/luma` | Análise local de `prompt`, `objetivo`, `message` ou `command` |
| POST | `/documents/inspect` | Inspeciona qualquer arquivo localmente e somente em memória |
| POST | `/zion/route` | Simulação do roteamento sem devolver o conteúdo |
| POST | `/arcana/challenge` | Emissão de desafio efêmero |
| POST | `/arcana/verify` | Verificação de resposta HMAC |
| POST | `/teazer/session` | Abertura de sessão efêmera |
| POST | `/pulse-lab/simulate` | Gera bloco em memória e selo Arcana |
| DELETE | `/teazer/session/{id}` | Encerramento da sessão |

Exemplo:

```bash
curl http://127.0.0.1:8787/health
curl -X POST http://127.0.0.1:8787/luma \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"verificar o estado da Celine"}'
curl -X POST http://127.0.0.1:8787/pulse-lab/simulate \
  -H 'Content-Type: application/json' \
  -d '{"duration_ms":100}'
```

### Arquivos de qualquer extensão

O texto `documentos.tgz` dos exemplos é apenas ilustrativo: o arquivo precisa
existir no computador e o comando deve apontar para seu caminho real. Confira
primeiro onde ele está:

```bash
find "$HOME" -maxdepth 4 -type f -print
```

O modo mais simples não exige iniciar o servidor nem usar `curl`:

```bash
python -m celine --inspect-document "$HOME/Downloads/arquivo.dll"
```

Substitua o caminho acima por um dos caminhos devolvidos pelo `find`. Se o
arquivo estiver no diretório atual, use `./nome-real-do-arquivo.extensao`.

Envie o arquivo como corpo binário e informe apenas o nome no cabeçalho. A rota
aceita qualquer extensão, inclusive `.py`, `.dll`, imagens, PDFs e formatos
desconhecidos. Textos UTF-8 são devolvidos para análise; JSON é estruturado;
binários retornam tamanho, SHA-256, tipo sugerido, assinatura inicial e indicação
de Portable Executable. Nenhum arquivo é executado, carregado como biblioteca,
gravado, encaminhado a conectores ou incluído integralmente na auditoria.

ZIP, TGZ e `tar.gz` são abertos somente em memória e cada item recebe a mesma
análise. Pacotes não podem conter caminhos ascendentes, links, itens especiais
ou ZIP criptografado.

```bash
ARQUIVO="$HOME/Downloads/nome-real-do-arquivo.dll"
test -f "$ARQUIVO" || { echo "Arquivo não encontrado: $ARQUIVO"; exit 1; }
curl -X POST http://127.0.0.1:8787/documents/inspect \
  -H 'Content-Type: application/octet-stream' \
  -H "X-CELINE-Filename: $(basename "$ARQUIVO")" \
  --data-binary "@$ARQUIVO"
```

O erro `curl: Failed to open` acontece no próprio terminal, antes de qualquer
contato com a CELINE: ele significa que o caminho depois de `@` não existe ou
não pode ser lido pelo usuário atual.

O upload pode ter até 32 MiB; são aceitos até 200 itens em pacotes, com no máximo
8 MiB por item e 32 MiB descompactados no total. Para materiais sensíveis, remova
credenciais e dados pessoais antes do envio, mesmo sendo uma interface restrita
ao computador local.

> **Importante:** executar essa API no seu computador não transfere o arquivo
> para esta conversa nem para o ambiente de desenvolvimento do Codex. Para que
> eu analise o arquivo em uma interação, anexe-o diretamente à conversa ou
> coloque uma cópia dentro do repositório `/workspace/siteceline` e informe o
> caminho relativo. Não cole senhas, tokens, documentos pessoais ou segredos.

Para que os desafios Arcana sobrevivam a reinicializações, configure uma chave
local sem registrá-la no Git:

```bash
export CELINE_ARCANA_SECRET='uma-chave-local-longa-e-aleatoria'
```

## Conectores externos

A camada de conectores admite serviços cadastrados numa allowlist e bloqueia
explicitamente nomes, hosts, caminhos e payloads relacionados ao **Gemini**.
Ela também recusa HTTP remoto, redirecionamentos, caminhos fora da allowlist e
respostas acima do limite. Não existe encaminhamento automático de conteúdo.

Destinos predefinidos: OpenAI, Anthropic, GitHub, Google Drive e Ollama local.
Outros serviços podem ser cadastrados em código por `ConnectorSpec`, passando
pelas mesmas validações. Cada conector exige habilitação própria; quando
aplicável, a credencial fica somente em variável de ambiente.

Exemplo de habilitação explícita da OpenAI:

```bash
export CELINE_OPENAI_ENABLED=true
export OPENAI_API_KEY='defina-a-chave-fora-do-repositorio'
```

A requisição externa é uma chamada deliberada da aplicação, não uma rota HTTP
genérica exposta pela CELINE:

```python
from celine import CelineEcosystem

celine = CelineEcosystem()
result = celine.connector_request(
    "openai",
    "POST",
    "/responses",
    {"model": "modelo-autorizado", "input": "pedido explicitamente autorizado"},
)
```

Variáveis de habilitação e credencial:

| Serviço | Habilitação | Credencial |
|---|---|---|
| OpenAI | `CELINE_OPENAI_ENABLED` | `OPENAI_API_KEY` |
| Anthropic | `CELINE_ANTHROPIC_ENABLED` | `ANTHROPIC_API_KEY` |
| GitHub | `CELINE_GITHUB_ENABLED` | `GITHUB_TOKEN` |
| Google Drive | `CELINE_GOOGLE_DRIVE_ENABLED` | `GOOGLE_DRIVE_ACCESS_TOKEN` |
| Ollama local | `CELINE_OLLAMA_ENABLED` | não requerida |

## Testes

```bash
python -m unittest discover -s tests -v
```

## Limite técnico honesto

Esta entrega materializa uma **topologia de software executável e auditável**.
Ela não demonstra operação de microchips físicos, emissão eletromagnética,
anonimato absoluto ou uma rede P2P distribuída. Essas capacidades exigiriam
especificações, hardware, protocolos e testes próprios antes de qualquer
afirmação operacional.
