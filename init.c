/*
 * PyOS - Simulador de Sistema Operacional em C puro
 * Compilar: gcc -o pyos pyos.c
 * Executar: ./pyos
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>


 //CONSTANTES


#define MAX_PROCESSOS  10
#define MAX_NOME       32
#define MAX_RECURSOS    2
#define MAX_FILA        10
#define PID_INICIAL  1000

/* Estados */
#define PRONTO              0
#define EXECUTANDO          1
#define BLOQUEADO           2
#define BLOQUEADO_SEMAFORO  3
#define TERMINADO           4


 //ESTRUTURAS DE DADOS
 

/* Bloco Descritor de Processo (PCB) — requisito obrigatorio */
typedef struct {
    int  pid;                   /* inteiro sequencial              */
    char nome[MAX_NOME];        /* array de char com limite        */
    int  estado;                /* PRONTO/EXECUTANDO/BLOQUEADO/... */
    int  ciclos_restantes;      /* "peso" da tarefa                */
    int  esperando_recurso;     /* -1 = nao espera nenhum recurso  */
} PCB;

/* RAM simulada — array estatico (requisito obrigatorio) */
static PCB tabela[MAX_PROCESSOS];
static int num_procs   = 0;
static int pid_counter = PID_INICIAL;

/* Semaforos: 0 = Impressora, 1 = Disco */
static const char *rec_nome[MAX_RECURSOS] = { "Impressora", "Disco" };
static int sem_dono[MAX_RECURSOS];              /* PID do dono, -1 = livre */
static int sem_fila[MAX_RECURSOS][MAX_FILA];
static int sem_fila_n[MAX_RECURSOS];


 //FUNCOES AUXILIARES
 
static const char *estado_str(int e)
{
    switch (e) {
        case PRONTO:             return "PRONTO";
        case EXECUTANDO:         return "EXECUTANDO";
        case BLOQUEADO:          return "BLOQUEADO";
        case BLOQUEADO_SEMAFORO: return "BLQ_SEM";
        case TERMINADO:          return "TERMINADO";
    }
    return "???";
}

/* Busca processo pelo PID; retorna ponteiro ou NULL */
static PCB *get_proc(int pid)
{
    for (int i = 0; i < num_procs; i++)
        if (tabela[i].pid == pid)
            return &tabela[i];
    return NULL;
}

/* Remove processo do array e compacta */
static void remove_proc(int pid)
{
    for (int i = 0; i < num_procs; i++) {
        if (tabela[i].pid == pid) {
            for (int j = i; j < num_procs - 1; j++)
                tabela[j] = tabela[j + 1];
            num_procs--;
            return;
        }
    }
}

/* Move processo para o fim do array (Round Robin) */
static void move_fim(int pid)
{
    for (int i = 0; i < num_procs; i++) {
        if (tabela[i].pid == pid) {
            PCB tmp = tabela[i];
            for (int j = i; j < num_procs - 1; j++)
                tabela[j] = tabela[j + 1];
            tabela[num_procs - 1] = tmp;
            return;
        }
    }
}

/* Conta processos que nao estao TERMINADO */
static int count_ativos(void)
{
    int n = 0;
    for (int i = 0; i < num_procs; i++)
        if (tabela[i].estado != TERMINADO)
            n++;
    return n;
}


 //DETECCAO DE DEADLOCK (DFS no grafo de espera)


static int dl_ciclo[MAX_PROCESSOS];
static int dl_n = 0;

static int detectar_deadlock(void)
{
    /* Monta grafo: grafo[i][0] espera grafo[i][1] */
    int grafo[MAX_PROCESSOS][2];
    int ng = 0;

    for (int i = 0; i < num_procs; i++) {
        PCB *p = &tabela[i];
        if (p->estado == BLOQUEADO_SEMAFORO && p->esperando_recurso >= 0) {
            int dono = sem_dono[p->esperando_recurso];
            if (dono >= 0 && dono != p->pid)
                grafo[ng][0] = p->pid, grafo[ng][1] = dono, ng++;
        }
    }

    dl_n = 0;
    for (int s = 0; s < ng; s++) {
        int path[MAX_PROCESSOS], pn = 0;
        int vis[10000] = {0};
        int cur = grafo[s][0];

        while (1) {
            /* Ciclo detectado? */
            for (int k = 0; k < pn; k++) {
                if (path[k] == cur) {
                    dl_n = pn - k;
                    for (int m = 0; m < dl_n; m++)
                        dl_ciclo[m] = path[k + m];
                    return 1;
                }
            }
            if (vis[cur % 10000]) break;
            vis[cur % 10000] = 1;
            path[pn++] = cur;

            int prox = -1;
            for (int i = 0; i < ng; i++)
                if (grafo[i][0] == cur) { prox = grafo[i][1]; break; }
            if (prox < 0) break;
            cur = prox;
        }
    }
    return 0;
}


 //FUNCOES DO KERNEL
 

static void boot(void)
{
    srand((unsigned)time(NULL));
    for (int i = 0; i < MAX_RECURSOS; i++)
        sem_dono[i] = -1, sem_fila_n[i] = 0;

    printf("Iniciando PyOS Kernel v1.0 (C Edition)...\n");
    sleep(1);
    printf("Carregando modulos de memoria        [OK]\n");
    usleep(500000);
    printf("Iniciando escalonador de processos   [OK]\n");
    usleep(500000);
    printf("Bem-vindo ao terminal. Digite 'help' para comandos.\n\n");
}

/* spawn: cria novo PCB e insere na tabela */
static void spawn_process(const char *nome)
{
    /* OOM — limite fisico da RAM (requisito obrigatorio) */
    if (count_ativos() >= MAX_PROCESSOS) {
        printf("[Kernel] ERRO: Out of Memory! Limite de %d processos atingido.\n",
               MAX_PROCESSOS);
        return;
    }
    if (num_procs >= MAX_PROCESSOS) {
        printf("[Kernel] ERRO: Tabela cheia.\n");
        return;
    }

    PCB *p = &tabela[num_procs++];
    p->pid              = pid_counter++;
    strncpy(p->nome, nome, MAX_NOME - 1);
    p->nome[MAX_NOME-1] = '\0';
    p->estado           = PRONTO;
    p->ciclos_restantes = rand() % 5 + 2;   /* 2 a 6 ciclos */
    p->esperando_recurso = -1;

    printf("[Kernel] Processo '%s' criado com PID %d | ciclos=%d\n",
           p->nome, p->pid, p->ciclos_restantes);
}

/* cpu: 1 tick do escalonador Round Robin (requisito obrigatorio) */
static void escalonador_tick(void)
{
    /* Procura primeiro processo PRONTO */
    PCB *escolhido = NULL;
    for (int i = 0; i < num_procs; i++) {
        /* BLOQUEADO_SEMAFORO nunca recebe CPU (requisito bonus) */
        if (tabela[i].estado == PRONTO) {
            escolhido = &tabela[i];
            break;
        }
    }

    if (!escolhido) {
        int blq = 0;
        for (int i = 0; i < num_procs; i++)
            if (tabela[i].estado == BLOQUEADO ||
                tabela[i].estado == BLOQUEADO_SEMAFORO) blq++;
        if (blq)
            printf("[CPU] Ociosa. %d processo(s) bloqueado(s) aguardando.\n", blq);
        else
            printf("[CPU] Ociosa (Idle). Nenhum processo na fila de prontos.\n");
        return;
    }

    /* Chaveamento de contexto — entra na CPU */
    escolhido->estado = EXECUTANDO;
    printf("\n[CPU] Executando PID %d (%s)...\n",
           escolhido->pid, escolhido->nome);
    sleep(1);

    escolhido->ciclos_restantes--;

    if (escolhido->ciclos_restantes <= 0) {
        /* Terminou — estado TERMINADO, remove da tabela */
        printf("[Kernel] Processo PID %d finalizou e liberou a memoria.\n",
               escolhido->pid);
        remove_proc(escolhido->pid);
    } else {
        /* Preempcao Round Robin */
        escolhido->estado = PRONTO;
        move_fim(escolhido->pid);
        printf("[Kernel] Chaveamento de contexto. PID %d pausado e movido para o fim da fila.\n",
               escolhido->pid);
    }
}

/* block / unblock: E/S */
static void block_process(int pid)
{
    PCB *p = get_proc(pid);
    if (!p) { printf("[Kernel] ERRO: PID %d nao encontrado.\n", pid); return; }
    if (p->estado != PRONTO && p->estado != EXECUTANDO) {
        printf("[Kernel] ERRO: PID %d nao pode ser bloqueado (estado: %s).\n",
               pid, estado_str(p->estado));
        return;
    }
    p->estado = BLOQUEADO;
    printf("[Kernel] PID %d (%s) -> BLOQUEADO (aguardando E/S).\n", pid, p->nome);
}

static void unblock_process(int pid)
{
    PCB *p = get_proc(pid);
    if (!p) { printf("[Kernel] ERRO: PID %d nao encontrado.\n", pid); return; }
    if (p->estado != BLOQUEADO) {
        printf("[Kernel] ERRO: PID %d nao esta BLOQUEADO (estado: %s).\n",
               pid, estado_str(p->estado));
        return;
    }
    p->estado = PRONTO;
    printf("[Kernel] PID %d (%s) -> PRONTO (E/S concluida).\n", pid, p->nome);
}

/* lock / unlock: semaforo mutex (bonus hardcore) */
static void lock_resource(int pid, int ri)
{
    PCB *p = get_proc(pid);
    if (!p) { printf("[Kernel] ERRO: PID %d nao encontrado.\n", pid); return; }

    if (sem_dono[ri] < 0) {
        sem_dono[ri] = pid;
        printf("[Semaforo] PID %d adquiriu '%s'. [LOCKED]\n", pid, rec_nome[ri]);
    } else {
        printf("[Semaforo] '%s' ocupado pelo PID %d. PID %d -> BLOQUEADO_SEMAFORO.\n",
               rec_nome[ri], sem_dono[ri], pid);
        p->estado            = BLOQUEADO_SEMAFORO;
        p->esperando_recurso = ri;
        if (sem_fila_n[ri] < MAX_FILA)
            sem_fila[ri][sem_fila_n[ri]++] = pid;

        /* Verifica deadlock imediatamente apos o bloqueio */
        if (detectar_deadlock()) {
            printf("\n*** DEADLOCK DETECTADO! ***\n");
            printf("Espera circular entre PIDs:");
            for (int i = 0; i < dl_n; i++) printf(" %d", dl_ciclo[i]);
            printf("\nUse 'kill <pid>' para desfazer o impasse.\n\n");
        }
    }
}

static void unlock_resource(int pid, int ri)
{
    if (sem_dono[ri] != pid) {
        printf("[Semaforo] ERRO: PID %d nao e o dono de '%s'.\n", pid, rec_nome[ri]);
        return;
    }
    printf("[Semaforo] PID %d liberou '%s'. [UNLOCKED]\n", pid, rec_nome[ri]);

    if (sem_fila_n[ri] > 0) {
        int prox_pid = sem_fila[ri][0];
        for (int i = 0; i < sem_fila_n[ri] - 1; i++)
            sem_fila[ri][i] = sem_fila[ri][i + 1];
        sem_fila_n[ri]--;

        PCB *prox = get_proc(prox_pid);
        if (prox) {
            sem_dono[ri]             = prox_pid;
            prox->estado             = PRONTO;
            prox->esperando_recurso  = -1;
            printf("[Semaforo] PID %d (%s) adquiriu '%s' da fila.\n",
                   prox_pid, prox->nome, rec_nome[ri]);
        } else {
            sem_dono[ri] = -1;
        }
    } else {
        sem_dono[ri] = -1;
    }
}

/* kill: encerramento forcado */
static void kill_process(int pid)
{
    for (int ri = 0; ri < MAX_RECURSOS; ri++)
        if (sem_dono[ri] == pid)
            unlock_resource(pid, ri);
    remove_proc(pid);
    printf("[Kernel] Sinal SIGKILL enviado. PID %d destruido.\n", pid);
}

/* ps: lista formatada (requisito obrigatorio) */
static void cmd_ps(void)
{
    printf("\n%-6s | %-12s | %-12s | %s\n",
           "PID", "NOME", "ESTADO", "CICLOS RESTANTES");
    printf("-----------------------------------------------\n");
    for (int i = 0; i < num_procs; i++) {
        PCB *p = &tabela[i];
        printf("%-6d | %-12.12s | %-12s | %d\n",
               p->pid, p->nome, estado_str(p->estado), p->ciclos_restantes);
    }
    if (!num_procs)
        printf("Nenhum processo em execucao.\n");

    printf("\nRecursos:");
    for (int ri = 0; ri < MAX_RECURSOS; ri++) {
        if (sem_dono[ri] < 0) printf("  %s=[LIVRE]", rec_nome[ri]);
        else                   printf("  %s=[PID %d]", rec_nome[ri], sem_dono[ri]);
    }

    if (detectar_deadlock()) {
        printf("\n[!] DEADLOCK entre PIDs:");
        for (int i = 0; i < dl_n; i++) printf(" %d", dl_ciclo[i]);
    }
    printf("\n\n");
}

/* ============================================================
 * SHELL — laco principal (requisito obrigatorio)
 * ============================================================ */

static void shell(void)
{
    char  line[256];
    char *tok[16];
    int   argc;

    while (1) {
        printf("root@pyos:~# ");
        fflush(stdout);

        if (!fgets(line, sizeof(line), stdin)) {
            printf("\nDesligando...\n");
            break;
        }
        line[strcspn(line, "\n")] = '\0';

        /* Tokeniza com strtok (requisito obrigatorio) */
        argc = 0;
        char *t = strtok(line, " \t");
        while (t && argc < 16) { tok[argc++] = t; t = strtok(NULL, " \t"); }
        if (!argc) continue;

        /* Converte comando para minusculo */
        for (char *c = tok[0]; *c; c++)
            if (*c >= 'A' && *c <= 'Z') *c += 32;

        /* ---- Despacha comandos ---- */

        if (strcmp(tok[0], "exit") == 0) {
            printf("Desligando o sistema...\n");
            break;
        }

        else if (strcmp(tok[0], "help") == 0) {
            printf("Comandos disponiveis:\n");
            printf("  spawn <nome>           - Cria um novo processo\n");
            printf("  ps                     - Lista os processos ativos\n");
            printf("  cpu                    - Executa 1 ciclo do processador\n");
            printf("  kill <pid>             - Encerra um processo a forca\n");
            printf("  block <pid>            - Bloqueia processo (simula E/S)\n");
            printf("  unblock <pid>          - Desbloqueia processo (E/S concluida)\n");
            printf("  lock <pid> <recurso>   - Adquire semaforo (Impressora | Disco)\n");
            printf("  unlock <pid> <recurso> - Libera semaforo\n");
            printf("  clear                  - Limpa a tela\n");
            printf("  exit                   - Desliga o sistema\n");
        }

        else if (strcmp(tok[0], "clear") == 0) {
            printf("\033[H\033[J");
            fflush(stdout);
        }

        else if (strcmp(tok[0], "spawn") == 0) {
            if (argc < 2) { printf("Uso: spawn <nome>\n"); continue; }
            spawn_process(tok[1]);
        }

        else if (strcmp(tok[0], "ps") == 0) {
            cmd_ps();
        }

        else if (strcmp(tok[0], "cpu") == 0) {
            escalonador_tick();
        }

        else if (strcmp(tok[0], "kill") == 0) {
            if (argc < 2) { printf("Uso: kill <pid>\n"); continue; }
            kill_process(atoi(tok[1]));
        }

        else if (strcmp(tok[0], "block") == 0) {
            if (argc < 2) { printf("Uso: block <pid>\n"); continue; }
            block_process(atoi(tok[1]));
        }

        else if (strcmp(tok[0], "unblock") == 0) {
            if (argc < 2) { printf("Uso: unblock <pid>\n"); continue; }
            unblock_process(atoi(tok[1]));
        }

        else if (strcmp(tok[0], "lock") == 0) {
            if (argc < 3) { printf("Uso: lock <pid> <Impressora|Disco>\n"); continue; }
            int ri = -1;
            for (int i = 0; i < MAX_RECURSOS; i++)
                if (strcasecmp(tok[2], rec_nome[i]) == 0) { ri = i; break; }
            if (ri < 0) printf("Recurso invalido. Use: Impressora | Disco\n");
            else        lock_resource(atoi(tok[1]), ri);
        }

        else if (strcmp(tok[0], "unlock") == 0) {
            if (argc < 3) { printf("Uso: unlock <pid> <Impressora|Disco>\n"); continue; }
            int ri = -1;
            for (int i = 0; i < MAX_RECURSOS; i++)
                if (strcasecmp(tok[2], rec_nome[i]) == 0) { ri = i; break; }
            if (ri < 0) printf("Recurso invalido. Use: Impressora | Disco\n");
            else        unlock_resource(atoi(tok[1]), ri);
        }

        else {
            printf("bash: %s: comando nao encontrado. Digite 'help'.\n", tok[0]);
        }
    }
}


 //MAIN
 

int main(void)
{
    boot();
    shell();
    return 0;
}