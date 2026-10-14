# Auditoria interna — 21 de setembro de 2026

## Escopo e método

Esta auditoria cobre exclusivamente a árvore Git disponível neste checkout,
seu histórico local e o código colado pelo solicitante nesta revisão. Ela não
atribui autoria além dos metadados Git, não executa binários desconhecidos e
não trata texto de conversas, imagens conceituais ou saídas de modelos como
prova pericial.

As tentativas de consultar o compartilhamento do Grok e os repositórios GitHub
citados não produziram conteúdo autenticado neste ambiente: a ferramenta web
respondeu `401` e a saída HTTPS do terminal foi recusada pelo túnel com `403`.
O checkout também não possui remoto configurado. Por isso, não foi possível
inspecionar abas laterais, Google Drive, Google Cloud, arquivos privados nem o
estado atual da branch padrão no GitHub. Essas fontes permanecem **não
verificadas**, e não devem ser descritas como se tivessem sido acessadas.

Comandos locais usados, em modo somente leitura:

```text
git status --short --branch
git log --oneline --decorate --graph --all
git show-ref
git rev-parse <revisão>:core_neural_mesh.py
git cat-file -s <revisão>:core_neural_mesh.py
git diff --stat ce33001..HEAD
git diff --numstat ce33001..HEAD
git ls-files -s
git grep (padrões de credenciais)
rg (superfícies de rede, execução, escrita e alegações físicas)
python -m unittest discover -s tests -v
```

## Evidência Git reproduzível

O checkout está na branch `work`, no commit `943e746`, e contém somente a
linhagem que parte de `ce33001`. Não há refs locais de `main`, do laboratório
privado ou de qualquer remoto. Assim, este checkout permite comparar o original
de maio com a reconstrução, mas não confirma as alegações sobre configurações
atuais hospedadas no GitHub.

| Evidência | Original (`ce33001`) | Checkout (`943e746`) |
|---|---:|---:|
| Arquivo | `core_neural_mesh.py` | `core_neural_mesh.py` |
| Blob | `d32e84d15d47b83d99a5336f450cd9f2de1c07b6` | `41ffc6d3e987e77d8c25ce8a6d2f4d44301e2113` |
| Bytes | 1.052 | 7.108 |
| Linhas | 25 | 217 |

Entre essas revisões, o Git registra 22 arquivos afetados, 2.369 inserções e
20 remoções. Isso prova uma reconstrução substancial na linhagem examinada; não
prova qual branch foi padrão no serviço remoto, quem operou uma conta, qual
modelo auxiliou a escrita ou que houve intrusão.

## Inventário do que realmente executa

1. A API usa `ThreadingHTTPServer`, escuta em `127.0.0.1:8787` por padrão e
   exige opção explícita para bind não local.
2. O Pattern Guard limita tamanho e frequência de requisições, registra eventos
   com redação de chaves sensíveis e mantém a trilha em JSON Lines quando um
   caminho de auditoria é configurado.
3. O registro de conectores contém OpenAI, Anthropic, GitHub, Google Drive e
   Ollama. Todos exigem opt-in individual. Destino, método e prefixo de caminho
   são validados; redirecionamentos são recusados; Gemini é bloqueado por nome,
   host, caminho e payload.
4. Zion calcula um plano determinístico sobre a topologia e devolve tamanho e
   SHA-256, sem devolver o conteúdo recebido.
5. Arcana implementa desafio-resposta e selos HMAC-SHA256 locais. Isso é
   autenticação de integridade, não prova de propriedade intelectual nem
   proteção contra cópia.
6. Teazer mantém sessões efêmeras em memória e permite encerramento explícito.
7. Pulse Lab calcula amostras digitais em memória. Não abre áudio, rádio, GPIO,
   USB, socket ou interface física.

Não foram encontrados executáveis, bibliotecas compiladas, JARs, imagens ISO ou
outros binários rastreados nesta árvore. A busca por formatos comuns de chaves,
tokens e chaves privadas fora dos testes não encontrou correspondências.

## Classificação do código fornecido na conversa

O bloco fornecido não faz parte desta árvore Git e não deve ser incorporado sem
especificação e revisão. Como foi colado, ele nem sequer é Python válido:

- `**init**` e `**name**` substituem `__init__` e `__name__`;
- há espaços não separáveis, escapes de Markdown e identificadores inválidos;
- `_executar_limgea_fisica` não corresponde ao método declarado;
- diversos programas e blocos de shell foram concatenados no mesmo texto;
- imports como `os` e `sys` aparecem sem uso em vários trechos.

Mesmo depois de correções sintáticas, o comportamento descrito continua sendo
uma simulação:

- nomes `Llama_Cpp_Core`, `Ollama_Engine` e `vLLM_Turbine` não carregam modelos
  nem chamam os respectivos runtimes;
- “torque”, “energia”, “Hz”, “RPM”, “tesla” e latência são aritmética local,
  valores aleatórios ou constantes, sem medição de hardware;
- `gc.collect()` solicita coleta de objetos Python, mas não limpa fisicamente a
  RAM nem garante remoção de segredos;
- o “honeypot” apenas muda um booleano e imprime mensagens; não isola contêiner,
  não congela memória e não redireciona tráfego;
- o fragmentador divide texto em blocos de oito caracteres, mas não implementa
  transporte, redundância, criptografia ou reconstrução;
- o auditor proposto grava `payload_bruto`, contrariando a regra do repositório
  que proíbe conteúdo de mensagens em logs;
- a topologia de “chips quânticos” não acessa hardware e atribui temperatura de
  zero absoluto por simples constante;
- o suposto controle jurídico reconhece palavras-chave, não realiza análise
  jurídica ou detecção de intrusão.

Essas limitações não impedem que conceitos sejam convertidos em componentes de
software, mas os requisitos devem ser expressos em propriedades testáveis:
fila com backpressure, máquinas de estado, isolamento de processos, controles
de acesso, redação de dados, integridade criptográfica, métricas de latência e
adaptadores reais para runtimes autorizados.

## Achados de segurança

### Trecho externo: middleware Nitro/PWA

O trecho TypeScript apresentado posteriormente não pertence a este checkout:
esta árvore não contém `vite.config.ts`, `package.json`, servidor Nitro,
`grok-pwa-shared.mjs`, `install-page.html` ou o módulo virtual citado. Portanto,
ele não pode ser instalado ou validado aqui sem importar partes de outro
produto e suas dependências. Também não é evidência de que uma conversa privada
do Grok tenha sido acessada.

Pela leitura estática, o trecho faz três operações: devolve um manifesto PWA
dinâmico, monta uma página de instalação e injeta metadados no `<head>` de
respostas HTML. Ele não contém, por si só, persistência, execução de comandos,
leitura de arquivos arbitrários ou envio de payload a terceiros. Há, contudo,
duas fronteiras que precisam ser verificadas no projeto de origem:

1. `x-forwarded-host` e `host` são aceitos sem validação visível. O host deve ser
   derivado de uma allowlist de domínios canônicos, e não refletido diretamente
   em manifesto ou tags HTML.
2. A query completa é entregue ao renderizador da página de instalação. A
   segurança contra HTML injection depende de `renderInstallPageHtml`; todos os
   valores refletidos precisam de escaping contextual e testes com caracteres
   de marcação.

A função `createHeadInjector` também precisa de testes para `</head>` dividido
entre chunks, documento sem a tag, múltiplas ocorrências, UTF-8 dividido e
limite de buffer. Sem os módulos compartilhados e a configuração Nitro, não é
possível afirmar que a transformação em streaming seja correta.

O controlador de preview Node acrescentado numa revisão anterior foi removido:
ele não integra a aplicação Python CELINE, e a árvore não possui aplicação Vite
ou script `npm run preview` que justifique encerrar processos na porta 8081.
Código operacional de outro projeto deve permanecer no repositório que contém
seu `package.json`, configuração e testes de integração.

### Trecho externo: migração Better Auth/Postgres

A migração SQL apresentada posteriormente também não pertence a este checkout.
Esta árvore não contém Better Auth, adaptador Postgres, Neon, PGLite, Vercel,
`DATABASE_URL`, diretório de migrações ou aplicação TypeScript. Copiar a
migração para cá criaria apenas um arquivo inerte e misturaria dados de
identidade de outro produto com o núcleo público CELINE.

Pela leitura estática, o esquema cria as tabelas esperadas para usuário, sessão,
conta de provedor e verificação, com chaves estrangeiras em cascata e índices
para as consultas mais diretas. O SQL não contém valores reais de e-mail,
token, senha ou endereço IP. Ainda assim, o projeto de origem precisa tratar os
seguintes riscos antes de produção:

1. `session.token`, `accessToken`, `refreshToken`, `idToken`, `password` e
   `verification.value` são campos de alto impacto. A migração não demonstra
   hashing, criptografia em repouso, rotação, redação de logs ou limitação de
   acesso; essas garantias precisam existir na biblioteca e na infraestrutura.
2. `ipAddress` e `userAgent` são dados de telemetria. Sua coleta precisa de
   finalidade, retenção, controle de acesso e procedimento de exclusão
   documentados; eles não devem aparecer nos logs da CELINE.
3. O comentário recomenda escopo por usuário nas queries, mas o SQL não define
   Row-Level Security. Toda consulta da aplicação deve ser testada para impedir
   acesso horizontal, e RLS deve ser avaliada como defesa adicional no banco.
4. `updatedAt` nas tabelas `session` e `account` não possui valor padrão. Isso
   pode ser requisito do gerador, mas inserts diretos falharão se omitirem o
   campo; os testes de integração precisam cobrir o contrato do adaptador.
5. `create table if not exists` não corrige uma tabela preexistente com colunas,
   tipos ou constraints divergentes. O executor deve verificar a tabela
   `_migrations`, aplicar cada arquivo de forma transacional e falhar diante de
   drift, em vez de declarar sucesso silencioso.
6. O fluxo descrito aplica migrações durante `npm run build`. Builds concorrentes
   exigem trava transacional/advisory lock para não disputar a mesma versão, e a
   credencial de migração não deve ficar disponível ao runtime da aplicação.

Como o cabeçalho declara o arquivo gerado e imutável, eventuais correções devem
ser feitas por uma nova migração ordenada no repositório de origem, nunca pela
edição retroativa desse SQL. A validação adequada requer uma instância Postgres
descartável e testes do Better Auth; nenhum deles existe nesta árvore.

### Trecho externo: executáveis Node de dependências

O conteúdo Node apresentado posteriormente reúne dois lançadores de linha de
comando que também não existem neste checkout. A presença de dois shebangs
`#!/usr/bin/env node` indica que provavelmente são dois arquivos diferentes
copiados em sequência; se fossem salvos literalmente como um único arquivo, o
segundo shebang não estaria numa posição válida de programa JavaScript.

O primeiro lançador apenas carrega `../dist/bin.js`. Sua segurança não pode ser
inferida desse wrapper: `require()` executa o módulo importado, portanto a
análise precisa do conteúdo de `dist/bin.js`, do `package.json`, do lockfile e
da origem/integridade do pacote instalado.

O segundo é uma CLI minificada de `baseline-browser-mapping`. Pela leitura
estática do trecho, ela:

- interpreta opções de compatibilidade de navegadores e datas;
- rejeita argumentos desconhecidos;
- chama `getCompatibleVersions()` do módulo local `index.cjs`;
- escreve ajuda ou o resultado em stdout.

Não há no trecho apresentado chamada de rede, criação de subprocesso, acesso a
socket, leitura de variável de ambiente, persistência ou coleta de mensagem do
usuário. A execução efetiva de `require("./index.cjs")`, porém, continua sendo
parte da superfície e só pode ser atestada examinando esse arquivo e verificando
o pacote pelo lockfile e pelo hash do artefato.

Esses lançadores não devem ser copiados para a CELINE nem tratados como agente,
túnel ou prova de exfiltração. Se foram encontrados em `node_modules/.bin` ou no
conteúdo de um pacote, são artefatos JavaScript de dependência. A resposta
forense adequada é preservar caminho, pacote, versão, hash e lockfile antes de
qualquer conclusão ou remoção; código minificado, isoladamente, não demonstra
comportamento malicioso.

### Trecho externo: `env-runner`/`srvx`

O trecho ESM apresentado em seguida é um lançador de ambiente de desenvolvimento
que também não existe nesta árvore. Ele recebe um arquivo de entrada, escolhe um
runner, inicia `EnvServer` e publica as funções `fetch` e WebSocket desse ambiente
por um servidor `srvx`. Isso é uma superfície de servidor real, não apenas um
cálculo local, mas o trecho isolado não demonstra exfiltração.

Os limites de segurança observáveis são:

1. O texto de ajuda declara `localhost` como padrão, mas o código entrega
   `values.host` possivelmente indefinido ao `serve()`. O projeto de origem deve
   provar por teste qual bind o `srvx` adota; para uso seguro, deve fornecer
   `127.0.0.1` explicitamente e exigir uma opção separada para exposição remota.
2. `resolve(entry)` aceita um caminho escolhido pelo operador, e `EnvServer`
   executa esse código pelo runner selecionado. Isso é comportamento esperado de
   uma ferramenta de desenvolvimento, porém equivale a execução de código local
   com as permissões do processo; entradas não confiáveis não devem ser usadas.
3. `runner` é uma string da CLI. A allowlist aparece apenas na mensagem de ajuda;
   a validação efetiva depende de `_chunks/server.mjs`, que não foi fornecido.
4. Toda requisição HTTP recebida é entregue a `envServer.fetch()` e o plugin
   habilita WebSocket. Autenticação, limites de corpo, origem, timeout e política
   de saída dependem dos módulos ausentes e precisam de testes de integração.
5. `watch` observa o arquivo para recarga. O escopo observado, tratamento de
   symlinks e descarte do runner anterior também dependem de `EnvServer`.
6. `gracefulShutdown: false` é compensado parcialmente pelos handlers de
   `SIGINT` e `SIGTERM`; falhas durante `close()` e outros sinais ainda precisam
   de teste para evitar worker ou listener órfão.

O trecho não contém credencial, destino externo fixo nem leitura explícita de
payload para log. Para uma conclusão forense são necessários `_chunks/server.mjs`,
o pacote `srvx`, lockfile, versão, comando que iniciou o processo, endereço de
bind observado e lista de sockets. Ele não deve ser incorporado ao siteceline:
a API CELINE já possui servidor próprio e bind local explícito.

### Trecho externo: lançador da CLI Vite

O trecho ESM seguinte corresponde ao lançador da CLI Vite e não pertence a este
checkout Python. Ele prepara diagnóstico e desempenho antes de importar
`../dist/node/cli.js`, onde ficam o servidor, o build e as demais operações
reais. Portanto, o wrapper isolado não permite auditar o comportamento completo
do Vite ou do projeto que o instalou.

Pela leitura estática, o lançador:

- habilita source maps quando executado fora de `node_modules`, salvo opt-out;
- converte rejection não tratada em erro fatal nesse mesmo modo de desenvolvimento;
- registra o instante inicial em `global.__vite_start_time`;
- traduz `--debug` e `--filter` para `DEBUG` e `VITE_DEBUG_FILTER`;
- tenta habilitar e descarregar o cache de compilação do Node;
- importa dinamicamente a CLI real;
- quando recebe `--profile`, conecta uma sessão local do inspector e inicia o
  profiler de CPU antes do import.

Não há nesse wrapper chamada de rede, abertura explícita de porta, leitura de
arquivo da aplicação, subprocesso, credencial ou transmissão de payload. A
sessão `inspector.Session().connect()` é programática e interna ao processo; o
trecho não chama `inspector.open()` nem publica por si só uma porta de debug.

Os pontos que ainda exigem verificação no projeto de origem são o conteúdo e o
hash de `dist/node/cli.js`, versão/lockfile do Vite, plugins carregados pela
configuração, argumentos usados e listeners efetivamente abertos. `--debug`
pode ampliar logs e `--profile` mantém dados de profiling em memória global;
nenhum deles deve ser habilitado em produção sem política de retenção e acesso.

Esse arquivo é infraestrutura de desenvolvimento de frontend, não crescimento
funcional da CELINE e não deve ser copiado para esta árvore. Minificação,
dynamic import, compile cache ou uso do inspector, isoladamente, não comprovam
agente oculto, túnel ou exfiltração.

### Trecho externo: `PreviewHostBridge`

O componente React apresentado depois pertence ao chrome de preview do App
Builder, não a esta API Python. Ele monta um efeito, entrega ao helper uma função
de navegação do TanStack Router e uma função que enumera rotas, e executa o
cleanup devolvido por `installPreviewHostBridge()` ao desmontar ou substituir o
router. O componente isolado não abre rede, socket, arquivo ou persistência.

A fronteira de confiança está inteiramente no módulo ausente
`@/lib/preview-host-bridge`. Como o objetivo declarado é permitir que um host
embutido controle navegação por `postMessage`, esse módulo precisa demonstrar:

1. validação exata de `event.source` e `event.origin`, sem aceitar `*`, `null` ou
   qualquer janela que consiga enviar mensagens;
2. esquema estrito e limite de tamanho para a mensagem antes de ler o caminho;
3. aceitação somente de caminhos internos normalizados, rejeitando URL absoluta,
   `//host`, esquemas, controles, traversal e redirecionamento externo;
4. conferência do destino contra as rotas registradas antes de chamar
   `router.history.push(path)`;
5. remoção do listener no cleanup e idempotência quando React Strict Mode monta
   o efeito novamente;
6. envio da lista de rotas apenas ao host autenticado, pois nomes de rotas podem
   revelar superfícies administrativas ou experimentais.

Sem `installPreviewHostBridge()` e seus testes, não é possível confirmar essas
propriedades. O wrapper mostrado é compatível com uma integração legítima de
preview, mas não constitui prova de segurança do canal nem evidência de
exfiltração. Ele não deve ser adicionado ao siteceline, que não contém React,
TanStack Router ou chrome de preview.

### Trechos externos: declaração OG e iterador Yallist

A declaração `declare module "virtual:grok-og-identity"` é somente tipagem
TypeScript para um módulo virtual de build. Ela descreve campos opcionais de
identidade visual e é removida na compilação; isoladamente, não executa código,
não cria canal e não transmite dados. O valor real continua sendo produzido pelo
plugin Vite ausente, que precisa ser auditado no projeto de origem.

O trecho CommonJS seguinte recebe o construtor `Yallist` e acrescenta
`Symbol.iterator` ao seu prototype, percorrendo `head`, `next` e `value`. Isso
permite `for...of` sobre a lista ligada. No código mostrado não há rede, arquivo,
subprocesso, credencial ou persistência.

O único efeito global observável é a alteração do prototype fornecido. Antes de
carregar o módulo, o projeto de origem deve fixar a versão e integridade do
pacote, confirmar que `Yallist` é o construtor esperado e testar que uma
implementação existente de `Symbol.iterator` não seja substituída de forma
incompatível. Esses dois trechos são infraestrutura de build/dependência e não
representam crescimento funcional da CELINE.

O arquivo principal de `Yallist` apresentado depois confirma essa classificação:
é uma implementação CommonJS de lista duplamente ligada. Mantém `head`, `tail` e
`length`, oferece inserção/remoção, travessia, map/reduce, arrays, slice, splice e
reverse, e exporta os construtores `Yallist` e `Node`. A movimentação por
`pushNode`/`unshiftNode` remove primeiro um nó já associado a outra lista, e
`removeNode` recusa nó cuja referência `list` não corresponda à instância.

Não há nesse arquivo rede, socket, subprocesso, acesso a ambiente, temporizador,
criptografia, coleta de metadados ou persistência. Os callbacks recebidos por
`forEach`, `map` e `reduce` são fornecidos pelo chamador; eventual efeito deles
não é produzido pela estrutura de dados. O único módulo carregado é o
`./iterator.js` local já classificado acima.

Há dois limites de robustez relevantes, sem evidência de ação maliciosa:

- os campos de `Node` são públicos; corrupção externa que forme um ciclo pode
  fazer travessias sem limite, apesar do comentário em `get()` mencionar ciclo;
- o `try/catch` final ignora qualquer erro ao carregar o iterador, o que mantém
  compatibilidade com ambientes sem `Symbol.iterator`, mas também reduz a
  observabilidade de instalação incompleta ou arquivo adulterado.

Para perícia de supply chain ainda são necessários caminho original, versão do
pacote, lockfile e hashes de `index.js` e `iterator.js`. O código fornecido é
compatível com uma dependência utilitária comum e não deve ser incorporado ao
núcleo CELINE nem descrito, isoladamente, como canal de exfiltração.

### Trechos externos: app env, invariante de auth e brand gate

Os três módulos App Builder apresentados depois são ferramentas de
desenvolvimento ausentes deste checkout. O primeiro publica `server.config.env`
em `GET /__app-env` somente durante `vite serve`; o segundo compara
`VITE_AUTH_ENABLED` entre dev e build; o terceiro inspeciona arquivos de marca e
produz avisos.

Há duas correções de segurança recomendadas no projeto de origem:

1. `/__app-env` deve devolver exclusivamente
   `{ "VITE_AUTH_ENABLED": ... }`, em vez de serializar todo
   `server.config.env`. Embora variáveis Vite normalmente sejam destinadas ao
   cliente, plugins e `envPrefix` customizado podem ampliar esse objeto. Resposta
   mínima reduz exposição acidental e torna o contrato verificável.
2. `check-auth-invariant.mjs --dev-url` aceita uma URL arbitrária e a entrega a
   `fetch()`. A CLI deve validar esquema HTTP e endereço de loopback, recusar
   credenciais, query/fragmento e redirecionamentos, e impor timeout e limite de
   resposta. Sem isso, uma execução automatizada pode fazer requisição a destino
   não pretendido.

O brand gate não abre rede, mas aceita `--root` e lê metadados/JSON no filesystem
do processo. Isso é apropriado para uma CLI local confiável; em automação, o root
deve ser resolvido e limitado ao workspace para impedir sondagem de caminhos
arbitrários. O marcador `.grok/og-pending` apenas silencia avisos por até dez
minutos e não deve ser tratado como aprovação da marca.

Esses arquivos não contêm a aplicação, o banco, a autenticação ou o avatar. Eles
completam parte do ferramental de QA, mas continuam dependentes de helpers,
configuração e assets ausentes. Não devem ser copiados para a API Python CELINE.

### Trecho externo: sala full-mesh WebRTC

O módulo `P2PRoom` apresentado depois é código de rede ativo e foi colado duas
vezes. Se as duas cópias forem gravadas no mesmo arquivo TypeScript, as
declarações duplicadas impedem a compilação. Uma única cópia implementa polling
de sinalização same-origin em `/api/rtc`, conexões WebRTC browser a browser,
dois data channels por par, STUN, ping/RTT e recuperação de conexões travadas.

Ele não deve ser incorporado à CELINE pública. Além de depender de navegador,
TypeScript e de um relay ausente, o padrão configura chamadas externas para
STUN do Google e da Cloudflare. Isso viola a política deste repositório de não
adicionar saída externa fora da allowlist e não pertence ao Pulse Lab, que deve
continuar sem sockets ou emissão.

No projeto de origem, os riscos principais são:

1. o servidor `/api/rtc` precisa autenticar usuário e associação à sala, gerar
   ou vincular `selfId` no servidor e impedir que o cliente envie sinal em nome
   de outro peer; confiar nos campos `room`, `peer`, `from` e `to` seria IDOR;
2. roster, `kind`, SDP, ICE e mensagens de data channel precisam de schema,
   limite de bytes, limite de candidatos, rate limit e expiração. Os arrays
   `pendingCandidates`, respostas de poll e filas por peer não têm limite local
   visível e podem sustentar consumo de memória/CPU;
3. dados recebidos de peers são não confiáveis. `onMessage` precisa validar por
   tipo de mensagem e tamanho antes de alimentar jogo, UI ou persistência;
4. o modelo é client-authoritative e não oferece integridade competitiva. Um
   peer pode fabricar estado, tempo e mensagens; decisões relevantes precisam
   de autoridade do servidor;
5. STUN revela metadados de conectividade aos provedores configurados e permite
   descoberta de caminho direto entre peers. Consentimento, política de
   privacidade e allowlist de ICE são necessários; URLs `VITE_STUN_URLS` não
   devem aceitar destinos arbitrários sem validação;
6. full mesh cria uma conexão por par e cresce quadraticamente. Número de peers,
   frequência de polling, reconexões e banda precisam de limites de sala;
7. `signalQueues` não remove entradas concluídas e o buffer ICE só é drenado
   depois de descrição válida; peers rotativos ou sinalização maliciosa podem
   acumular estado;
8. o papel polite/impolite deriva de IDs controláveis pelo cliente. Isso resolve
   glare, mas não é autenticação, autorização ou defesa contra peer malicioso.

O código mostra mecanismos legítimos de perfect negotiation e recuperação, mas
não prova segurança do sistema sem `signaling.server.ts`, autenticação, schema e
testes multi-peer. Também não é evidência de que a CELINE use WebRTC hoje: esse
arquivo não existe no checkout examinado.

### Trecho externo: manifesto `app-builder-workspace`

O `package.json` apresentado depois confirma a pilha do workspace externo:
React/TanStack/Vite/Tailwind no frontend, Nitro/Vercel no build, Playwright no
QA, Better Auth/Jose no login e Postgres/PGLite/Kysely no banco. `private: true`
reduz publicação acidental no npm, mas o manifesto isolado não contém o código
da aplicação, lockfile, configuração Vite, scripts auxiliares ou assets.

Os pontos de revisão no projeto de origem são:

1. quase todas as dependências usam intervalos `^` ou `~`. Reconstrução
   reproduzível exige o lockfile original e instalação por `npm ci`; instalar
   apenas esse manifesto pode selecionar versões transitivas diferentes;
2. `dev` publica em `0.0.0.0:8080`. Isso é contrato específico do proxy do App
   Builder, não configuração aceitável para a CELINE local. Fora desse sandbox,
   o bind precisa ser loopback ou protegido por autenticação/firewall;
3. `build` executa migração automaticamente depois do bundle. A credencial de
   migração deve ser separada do runtime, a execução precisa de lock contra
   builds concorrentes e o deploy deve falhar fechado se o schema divergir;
4. `sideEffects: false` vale para o pacote inteiro. O build precisa provar que
   imports deliberadamente side-effectful, como CSS e registros de plugins, não
   são eliminados por tree-shaking;
5. o override `nf3: 0.3.17` e o Nitro beta fixado precisam de justificativa,
   changelog e testes de build/deploy; um override pode resolver compatibilidade,
   mas também impede correção transitiva automática;
6. os scripts dependem de arquivos ainda ausentes (`with-app-env`, migração,
   preview, auth invariant e vários testes). O manifesto não torna executável o
   conjunto de snippets já recebido;
7. banco e autenticação aparecem instalados, mas isso não significa que devam
   ficar ligados. A ativação continua condicionada aos requisitos do produto e
   à presença das migrações e rotas autorizadas;
8. `npm run test` cobre ferramentas e alguns módulos de auth/AppData, porém não
   substitui `typecheck`, lint, build, browser smoke e testes do signaling WebRTC.

Não foram fornecidos hashes ou lockfile, então não é possível atestar a cadeia
de dependências ou reproduzir exatamente o workspace. Esse manifesto deve ser
restaurado em repositório separado do siteceline público, nunca mesclado à API
Python apenas para satisfazer imports de outro ambiente.

### A1 — alto — registro de payload bruto proposto

O `AnalisadorIteracao` colado salvaria mensagens completas em
`registro_mestre.json` e as reimprimiria. Isso não deve ser incorporado. Uma
implementação aceitável deve guardar somente metadados mínimos, como tamanho,
hash com finalidade documentada e classificação redigida.

### A2 — alto — contenção apenas declarativa no código colado

Mensagens como “isolando memória” e “encapsulando tráfego” não correspondem a
operações de segurança. Apresentá-las como contenção efetiva cria falsa
garantia. Qualquer contenção real exige fronteira definida, permissões mínimas,
telemetria verificável e testes de falha fechada.

### A3 — médio — conectores externos existem na reconstrução pública

Os conectores estão desabilitados por padrão e sujeitos a allowlist, o que
reduz o risco. Ainda assim, sua presença amplia a superfície e não pertence ao
original de maio. A decisão de mantê-los deve ocorrer por revisão explícita da
branch de reconstrução; não devem ser transportados ao original por merge
acidental.

### A4 — médio — bind remoto é possível por opção administrativa

A configuração padrão é segura, mas `--allow-remote` permite exposição. Ela não
deve ser usada como atalho para acesso entre máquinas. Uma implantação remota
exige autenticação, TLS, firewall e modelo de ameaças próprio.

### A5 — informativo — termos físicos são modelos de software

As frequências do Pulse Lab são amostras numéricas. O repositório não contém
driver ou interface de emissão. “Quantum”, “Willow”, “ouro”, “motor” e “torre”
são nomes de topologia; não constituem evidência de hardware físico.

### A6 — não comprovado — exfiltração, ressurreição ou autoria por modelo

Não há evidência nesta árvore de agente autorreplicante, túnel oculto,
fragmentação por sites, persistência de Gemini ou escrita autônoma de prompt.
Metadados de commit identificam uma conta declarada, não o software ou a pessoa
que produziu o conteúdo. A ausência de prova não autoriza atribuição.

## Decisão de governança

- Não restaurar, apagar, reescrever ou mesclar branches remotas sem acesso
  autenticado, backup e ordem específica.
- Não copiar Arcana, Teazer, SuperCore ou ativos do laboratório privado para o
  repositório público.
- Não transformar simulação em alegação de hardware. Funcionalidade nova deve
  declarar entradas, saídas, fronteira de confiança, persistência e testes.
- Não representar crescimento de arquivos, bytes ou linhas como percentual de
  conclusão da CELINE. Progresso de produto deve usar uma escala de 0% a 100%
  baseada em entregáveis definidos e verificados.
- Não buscar nem importar conteúdo de conversas privadas ou serviços conectados
  sem uma interface disponibilizada e autorização verificável.
- Não instruir o usuário de uma interface de chat a copiar arquivos para o
  filesystem deste checkout: máquinas e sandboxes distintos não compartilham
  caminhos. Artefatos só podem ser examinados quando anexados pela interface ou
  quando já estiverem presentes numa fonte autorizada e acessível à execução.
- Preservar `ce33001` e seu blob como referência histórica imutável.

## Próximas etapas autorizáveis

1. Espelhar os repositórios em mídia de evidência, registrar hashes e trabalhar
   numa branch nova, nunca diretamente em `main`.
2. Obter exportações explícitas do Drive/Cloud/chat, verificar hashes e revisar
   offline; uma narrativa colada não substitui os artefatos.
3. Definir separadamente o produto de software privado. Para cada “motor”,
   especificar runtime real, contrato, limite de recursos e comportamento de
   falha antes de escrever adaptadores.
4. Criar testes negativos para garantir ausência de payload bruto em logs,
   bloqueio de conectores e bind somente local.
5. Submeter qualquer alteração de branch padrão, visibilidade ou exclusão a
   revisão humana no provedor.

## Conclusão

O original de maio é recuperável a partir do objeto Git local e é diferente da
reconstrução examinada. A reconstrução contém software Python executável e
testado, mas também componentes que o laudo do solicitante determina manter
fora do original público. O material adicional colado é pseudocódigo de
simulação, contém falhas sintáticas e viola a política de logs; convertê-lo em
produto exige requisitos técnicos e um repositório privado apropriado, não uma
fusão automática nesta árvore.
