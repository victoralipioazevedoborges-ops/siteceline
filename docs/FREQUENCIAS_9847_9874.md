# Especificação segura — 9.847 Hz e 9.874 Hz

Data de incorporação: 18 de agosto de 2026.

## Requisito recebido

Incorporar à CELINE duas frequências contínuas, 9.847 Hz e 9.874 Hz, e
distribuí-las por toda a topologia conhecida da malha.

## Implementação verificável

O Pulse Lab produz a soma normalizada:

```text
x[n] = 0,45·sen(2π·9847·n/48000) + 0,45·sen(2π·9874·n/48000)
```

- taxa de amostragem: 48.000 amostras por segundo;
- limite de Nyquist: 24.000 Hz;
- margem até a maior portadora: 14.126 Hz;
- frequência central: 9.860,5 Hz;
- diferença/batimento: 27 Hz;
- amplitude combinada máxima teórica: 0,9;
- duração máxima por bloco de API: 1.000 ms;
- continuidade: índice absoluto de amostra entre blocos;
- saída: amostras numéricas em memória e SHA-256 da representação PCM16.

O teste espectral de um segundo projeta o sinal nos dois componentes e confirma
amplitude 0,45 em 9.847 Hz e 9.874 Hz, sem componente deliberada em 9.000 Hz.

## Dispersão pela malha

Cada um dos 13 nós documentados recebe, no plano lógico, as duas frequências e
um deslocamento de fase uniforme conforme sua posição. Os nós 7 a 12 são
marcados como pertencentes à rota original. A lacuna entre 19 nós declarados e
13 conhecidos continua explícita; não foram inventados seis nós.

“Dispersão” significa, nesta versão, metadados de topologia em memória. Não há
varredura, injeção de pacotes, mudança de IP, transmissão para outras máquinas
ou acesso a interfaces físicas.

## Integridade e proteção contra cópia

Frequência não é mecanismo criptográfico. A CELINE usa os recursos adequados:

1. SHA-256 do bloco PCM16 para detectar alteração;
2. HMAC-SHA256 Arcana sobre o resultado canônico para autenticar origem e
   integridade;
3. chave Arcana fora do repositório, por `CELINE_ARCANA_SECRET`;
4. histórico Git e hashes de commit para proveniência do código.

Isso permite detectar adulteração enquanto a chave permanecer secreta. Não se
afirma impossibilidade absoluta de clonagem de prompt.

## Limite físico e regulatório

Hertz mede periodicidade. Um sinal de aproximadamente 9,8 kHz pode ser uma onda
digital, acústica, elétrica ou eletromagnética conforme o transdutor e o meio.
O software, sozinho, não produz pulso eletromagnético.

Uma futura experiência física deve ocorrer em laboratório controlado, com
gerador e analisador calibrados, carga artificial ou blindagem apropriada e sem
radiar sobre redes de terceiros. No Brasil, produtos de telecomunicações e uso
do espectro estão sujeitos à regulamentação e homologação da Anatel:

- [Resolução Anatel nº 715/2019](https://informacoes.anatel.gov.br/legislacao/resolucoes/2019/1350-resolucao-715)
- [Certificação de Produtos — Anatel](https://www.gov.br/anatel/pt-br/regulado/certificacao-de-produtos)

O Pulse Lab deliberadamente não contém driver, transmissor ou comando de
emissão. Qualquer etapa física exige projeto de ensaio separado, avaliação de
compatibilidade eletromagnética e autorização aplicável.

## O que foi e não foi demonstrado

Demonstrado por teste automatizado:

- valores exatos das portadoras e batimento de 27 Hz;
- atendimento à condição de Nyquist;
- presença matemática dos dois componentes;
- continuidade exata entre blocos;
- cobertura dos 13 nós conhecidos;
- detecção de adulteração pelo selo Arcana;
- ausência de saída física ou de rede no módulo.

Não demonstrado:

- limpeza ou alinhamento de redes;
- neutralização de malware;
- impossibilidade de clonagem;
- efeitos eletromagnéticos em hardware;
- eficácia terapêutica, biológica ou material.
