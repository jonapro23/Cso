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

------------------------------------------------------------

🖥️ CSo - Operating System Simulator in C

A simple operating system simulator built in pure C, focusing on process management, CPU scheduling, synchronization, and deadlock detection.

📌 About the Project

CSo (C System OS) is an educational simulator that demonstrates core operating system concepts in practice:

Process management (PCB)
CPU scheduling (Round Robin)
Resource control using semaphores
Deadlock detection
Simulated RAM
Interactive shell (terminal-based)
⚙️ Features
Process creation and termination
Process states:
READY
RUNNING
BLOCKED
SEMAPHORE_BLOCKED
TERMINATED
Round Robin scheduling
Resource management:
Printer
Disk
Resource waiting queues
Automatic deadlock detection
Interactive shell interface
🛠️ Technologies
C Programming Language
GCC (GNU Compiler)
Linux / WSL
🚀 How to Run
1. Clone the repository
git clone https://github.com/jonapro23/Cso.git
cd Cso
2. Compile the program
gcc -o init init.c
3. Run
./init
💻 Available Commands
Command	Description
spawn <name>	Create a new process
ps	List processes
cpu	Execute one CPU cycle
kill <pid>	Force terminate a process
block <pid>	Block a process (I/O simulation)
unblock <pid>	Unblock a process
lock <pid> <resource>	Acquire a resource
unlock <pid> <resource>	Release a resource
clear	Clear the screen
help	Show commands
exit	Shutdown system
🔄 Scheduling

The system uses:

👉 Round Robin Algorithm

Each process gets CPU time
If it doesn't finish, it goes to the end of the queue
Simulates real preemptive scheduling
🔒 Resources (Semaphores)

Available resources:

Printer
Disk

Each resource:

Can be used by only one process at a time
Has a waiting queue
Can lead to deadlock
⚠️ Deadlock Detection

The system automatically detects deadlocks using a wait-for graph approach.

Example:

P1 → waiting for P2
P2 → waiting for P1

Output:

*** DEADLOCK DETECTED! ***
🧠 Concepts Applied
Operating Systems
Process Scheduling
Concurrency
Synchronization
Data Structures
Graph Theory (cycle detection)
🎯 Purpose

This project was developed for educational purposes to:

Understand how operating systems work internally
Practice C programming
Simulate real-world problems like deadlock
👨‍💻 Author

Jonathan Freitas
GitHub: https://github.com/jonapro23

📄 License

Educational use.
Feel free to study, modify, and improve 🚀

⭐ Contributions

Contributions are welcome!

Fork the repository
Create a new branch
Make your changes
Submit a Pull Request
