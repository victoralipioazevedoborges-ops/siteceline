# CELINE

Núcleo Python local do ecossistema **CELINE**, acoplando a topologia GENESYS 1
aos módulos Luma, Arcana, Zion, Teazer e Pattern Guard.

## Estado funcional

- **CELINE**: orquestração e diagnóstico do ecossistema.
- **LUMA**: análise determinística local, pronta para receber um provedor de
  modelo em etapa posterior.
- **ARCANA**: desafio-resposta HMAC-SHA256, de uso único e com expiração.
- **ZION**: roteamento auditável entre as torres 7 e 12.
- **TEAZER**: abertura e encerramento explícito de sessões efêmeras locais.
- **PATTERN GUARD**: limite de corpo, limite de requisições, acesso loopback e
  auditoria com redação de campos sensíveis.

O MVP não usa bibliotecas de terceiros. A API escuta apenas em `127.0.0.1` por
padrão. Saídas externas são desabilitadas por padrão e só funcionam após a
habilitação individual de um destino fixo.

## Divergência preservada

O commit inicial declara **19 microchips**, mas fornece uma sequência de **13
elementos**. O núcleo reporta a lacuna de seis componentes e não inventa nomes
ou propriedades ausentes da fonte. O fluxo documentado entre as posições 7 e
12 permanece funcional.

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
| POST | `/luma` | Análise local de `prompt`, `objetivo`, `message` ou `command` |
| POST | `/zion/route` | Simulação do roteamento sem devolver o conteúdo |
| POST | `/arcana/challenge` | Emissão de desafio efêmero |
| POST | `/arcana/verify` | Verificação de resposta HMAC |
| POST | `/teazer/session` | Abertura de sessão efêmera |
| DELETE | `/teazer/session/{id}` | Encerramento da sessão |

Exemplo:

```bash
curl http://127.0.0.1:8787/health
curl -X POST http://127.0.0.1:8787/luma \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"verificar o estado da Celine"}'
```

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
