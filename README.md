# Chat em rede com Sockets e Threads (Python)

Chat cliente-servidor feito com sockets TCP e threads, sem bibliotecas externas.

## Requisitos

- Python 3.8 ou mais recente (baixe em https://www.python.org/downloads/).
  No Windows, marque a opção **"Add Python to PATH"** durante a instalação.
- Para confirmar a instalação, abra o terminal e digite `python --version`
  (no Linux/Mac pode ser `python3 --version`).

## Estrutura do projeto

```
chat-redes-ufal/
├── src/
│   ├── server.py      # servidor: aceita conexões e cria uma thread por cliente
│   └── client.py      # cliente: thread de recebimento + leitura do teclado
├── docs/
│   └── relatorio.pdf  # relatório do projeto
├── README.md
└── .gitignore
```

## Como rodar

Abra um terminal **na pasta principal do projeto** (`chat-redes-ufal/`, onde está este README).

1. Inicie o servidor:

   ```
   python src/server.py
   ```

   Deve aparecer: `Server listening on port 5050.` Deixe esse terminal aberto.

2. Em **outro** terminal, também na pasta principal, inicie um cliente:

   ```
   python src/client.py
   ```

3. Digite um apelido e pressione Enter. Abra mais terminais e repita o passo 2
   para conectar outros usuários.

No Linux/Mac, troque `python` por `python3` se o primeiro não funcionar.

### Usando em computadores diferentes

1. No computador do servidor, descubra o IP com `ipconfig` (Windows) ou
   `ip addr` / `ifconfig` (Linux/Mac). Exemplo: `192.168.0.10`.
2. Nos outros computadores, conectados à mesma rede, rode:

   ```
   python src/client.py 192.168.0.10
   ```

3. Se não conectar, libere a porta 5050 no firewall do computador do servidor.

## Comandos do chat

| Comando | O que faz |
|---|---|
| texto qualquer | envia a mensagem para todos da sua sala |
| `/join <nome>` | entra em outra sala (cria se não existir) |
| `/msg <apelido> <texto>` | envia uma mensagem privada |
| `/users` | lista quem está online |
| `/rooms` | lista as salas e quantas pessoas há em cada |
| `/help` | mostra os comandos |
| `/quit` | desconecta |

Todos começam na sala `general`.

## Protocolo

A comunicação usa TCP na porta 5050. Cada mensagem é uma linha de texto em
UTF-8 terminada em `\n`. O cliente envia o que o usuário digita; o servidor
interpreta as linhas que começam com `/` como comandos e as demais como
mensagens para a sala.

## Para encerrar

Use `/quit` no cliente e `Ctrl+C` no terminal do servidor.