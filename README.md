# 🖥️ CSo - Simulador de Sistema Operacional em C

> Um simulador de sistema operacional desenvolvido em **C puro**, com foco em gerenciamento de processos, escalonamento e sincronização.

---

## 📌 Sobre o Projeto

O **CSo (C System OS)** é um simulador educacional que implementa conceitos fundamentais de sistemas operacionais, permitindo visualizar na prática:

* Gerenciamento de processos (PCB)
* Escalonamento de CPU (Round Robin)
* Controle de recursos com semáforos
* Detecção de deadlock
* Simulação de memória RAM
* Shell interativo via terminal

---

## ⚙️ Funcionalidades

* Criação e remoção de processos
* Estados de execução:

  * PRONTO
  * EXECUTANDO
  * BLOQUEADO
  * BLOQUEADO_SEMAFORO
  * TERMINADO
* Escalonamento Round Robin
* Controle de recursos:

  * Impressora
  * Disco
* Fila de espera por recursos
* Detecção automática de deadlock
* Interface interativa (shell)

---

## 🛠️ Tecnologias

* Linguagem C
* GCC (GNU Compiler)
* Linux / WSL

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/jonapro23/Cso.git
cd Cso
```

### 2. Compile o programa

```bash
gcc -o init init.c
```

### 3. Execute

```bash
./init
```

---

## 💻 Comandos Disponíveis

| Comando                  | Descrição              |
| ------------------------ | ---------------------- |
| `spawn <nome>`           | Cria um processo       |
| `ps`                     | Lista processos        |
| `cpu`                    | Executa 1 ciclo da CPU |
| `kill <pid>`             | Finaliza processo      |
| `block <pid>`            | Bloqueia processo      |
| `unblock <pid>`          | Desbloqueia processo   |
| `lock <pid> <recurso>`   | Solicita recurso       |
| `unlock <pid> <recurso>` | Libera recurso         |
| `clear`                  | Limpa tela             |
| `help`                   | Mostra comandos        |
| `exit`                   | Encerra sistema        |

---

## 🔄 Escalonamento

O sistema utiliza o algoritmo:

👉 **Round Robin**

* Cada processo recebe um tempo de CPU
* Se não terminar, retorna ao fim da fila
* Simula preempção real de sistemas operacionais

---

## 🔒 Recursos (Semáforos)

Recursos disponíveis:

* Impressora
* Disco

Cada recurso:

* Só pode ser usado por um processo por vez
* Possui fila de espera
* Pode gerar deadlock

---

## ⚠️ Deadlock

O sistema detecta automaticamente deadlocks através de análise de dependência entre processos.

---

## 🧠 Conceitos Aplicados

* Sistemas Operacionais
* Concorrência
* Sincronização
* Escalonamento de processos
* Estruturas de dados
* Grafos (detecção de ciclos)

---

## 🎯 Objetivo

Projeto criado para fins educacionais com foco em:

* Entender funcionamento interno de um sistema operacional
* Praticar programação em C
* Simular problemas reais como deadlock

---

## 👨‍💻 Autor

**Jonathan Freitas**
GitHub: https://github.com/jonapro23

---

## 📄 Licença

Uso educacional. Livre para estudo e melhorias 🚀

---
