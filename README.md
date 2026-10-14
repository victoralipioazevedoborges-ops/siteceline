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
python3 -m celine
```

A API ficará disponível em `http://127.0.0.1:8787`.

Execute os comandos a partir do clone deste repositório na própria máquina. O
caminho `/workspace/siteceline` pertence somente a ambientes de automação e não
deve ser copiado literalmente para um terminal pessoal.

### Entregar outro workspace para análise

Este ambiente não enxerga diretórios criados no computador do operador. Quando
a interface não aceitar anexos, use um repositório Git **separado** como meio de
transferência. Não copie o App Builder para este repositório da CELINE.

No Linux, crie o workspace e registre os arquivos existentes assim:

```bash
mkdir -p "$HOME/celine-app-builder"
cd "$HOME/celine-app-builder"
git init -b importacao
printf '.env\n.env.*\nnode_modules/\n*.pem\n*.key\n*.p12\n*.pfx\n' > .gitignore
# Copie ou recupere os arquivos do App Builder para esta pasta.
git add .
git status --short
git commit -m 'chore: importar workspace para análise'
```

Antes de publicar, examine `git status --short` e remova credenciais, cookies,
sessões, bancos com dados pessoais e exportações de mensagens. Depois crie um
repositório remoto vazio no provedor Git escolhido e execute, substituindo a
URL pelo endereço real fornecido pelo provedor:

```bash
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin importacao
```

Por fim, envie nesta conversa somente a URL do repositório e o nome da branch
(`importacao`). O repositório precisa estar acessível para leitura; não envie
token ou senha no chat. Se o material não puder ser tornado acessível com
segurança, envie primeiro apenas a listagem sanitizada produzida por
`git status --short` e os arquivos de configuração não secretos em blocos de
texto identificados pelo caminho relativo.

#### Criar uma cópia comprimida no Ubuntu

Para código-fonte, `tar.xz` costuma ocupar menos espaço que ZIP, embora leve
mais tempo para comprimir. Execute o comando a partir da pasta que contém o
workspace; assim, o arquivo gerado não é incluído dentro dele:

```bash
cd "$HOME"
tar \
  --exclude='celine-app-builder/.git' \
  --exclude='celine-app-builder/node_modules' \
  --exclude='celine-app-builder/.env' \
  --exclude='celine-app-builder/.env.*' \
  --exclude='celine-app-builder/dist' \
  --exclude='celine-app-builder/build' \
  --exclude='celine-app-builder/.cache' \
  -I 'xz -9e -T0' \
  -cf celine-app-builder.tar.xz celine-app-builder/
```

Confira tamanho, conteúdo e integridade antes de copiar ou publicar:

```bash
du -h "$HOME/celine-app-builder.tar.xz"
tar -tJf "$HOME/celine-app-builder.tar.xz" | less
xz --test "$HOME/celine-app-builder.tar.xz"
sha256sum "$HOME/celine-app-builder.tar.xz" \
  > "$HOME/celine-app-builder.tar.xz.sha256"
```

Para descomprimir em outra pasta:

```bash
mkdir -p "$HOME/celine-restaurada"
tar -xJf "$HOME/celine-app-builder.tar.xz" \
  -C "$HOME/celine-restaurada" --strip-components=1
```

O arquivo comprimido é apenas uma cópia local; ele não se torna acessível a
este ambiente automaticamente. Para análise remota, publique os fontes
sanitizados pelo fluxo Git acima. Não use Base64 para economizar espaço: a
codificação aumenta o volume e não substitui criptografia.

### Diagnóstico de comunicação local

Em outra aba do terminal, verifique a comunicação com a API sem consultar
serviços externos:

```bash
python3 -m celine.diagnostics
```

O comando acessa exclusivamente `/health` em um endereço de loopback, limita a
resposta a 64 KiB e informa apenas disponibilidade, status HTTP, estado da
CELINE e se algum conector externo foi habilitado. Ele recusa destinos remotos,
credenciais na URL e outras rotas. Esse diagnóstico cobre a API local; ele não
testa nem controla a conexão do navegador com um serviço de bate-papo.

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
python3 -m unittest discover -s tests -v
```

## Limite técnico honesto

Esta entrega materializa uma **topologia de software executável e auditável**.
Ela não demonstra operação de microchips físicos, emissão eletromagnética,
anonimato absoluto ou uma rede P2P distribuída. Essas capacidades exigiriam
especificações, hardware, protocolos e testes próprios antes de qualquer
afirmação operacional.
