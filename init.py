#imports
import time
import sys
import random
 
# ==========================================
# ESTRUTURAS DE DADOS DO KERNEL
# ==========================================
 
# Tabela global de processos (Nossa "RAM")
tabela_processos = []
 
pid_counter = 1000 # PIDs na vida real começam em 1000
 
# Nivel 5/6: Semaforos — controle de recursos compartilhados
# Dicionario: nome_do_recurso -> PID do dono (ou None se livre)
semaforos = {
    "Impressora": None,
    "Disco":      None,
}
 
# Fila de processos aguardando cada recurso: recurso -> [pid, pid, ...]
fila_recurso = {r: [] for r in semaforos}
 
# Nivel Supremo: Memoria compartilhada para IPC
# Dicionario: pid -> lista de mensagens escritas por outros processos
memoria_ipc = {}
 
 
class PCB:
    """Bloco Descritor de Processo (Process Control Block)"""
    def __init__(self, nome, prioridade="normal", pai=None):
        global pid_counter
        self.pid               = pid_counter
        self.nome              = nome
        self.estado            = "PRONTO"  # Estados: PRONTO, EXECUTANDO, BLOQUEADO, ZUMBI
        self.ciclos_restantes  = random.randint(2, 6) # Define o "peso" do processo (quantos ticks ele precisa)
        self.prioridade        = prioridade            # Nivel 4: high | normal | low
        self.pai               = pai                   # Nivel 8: PID do processo pai
        self.filhos            = []                    # Nivel 8: lista de PIDs filhos
        self.contexto          = {"PC": 0, "ACC": 0, "REG": [0, 0, 0]} # Salvo no chaveamento
        self.esperando_recurso = None                  # Nivel 5/6: recurso que o processo aguarda
        pid_counter += 1
 
 
# ==========================================
# FUNCOES DO KERNEL E ESCALONADOR
# ==========================================
 
def boot():
    """Simula a inicializacao do Sistema Operacional"""
    print("Iniciando PyOS Kernel v2.0...")
    time.sleep(1)
    print("Carregando modulos de memoria [OK]")
    time.sleep(0.5)
    print("Iniciando escalonador de processos [OK]")
    time.sleep(0.5)
    print("Inicializando semaforos de recursos [OK]")
    time.sleep(0.5)
    print("Inicializando memoria compartilhada IPC [OK]")
    time.sleep(0.5)
    print("Bem-vindo ao terminal. Digite 'help' para comandos.\n")
 
 
def spawn_process(nome, prioridade="normal", pai=None, contexto_clone=None):
    """Cria um novo processo e adiciona na tabela (RAM)"""
 
    # Nivel 1: Limite de Memoria — OOM
    ativos = [p for p in tabela_processos if p.estado != "TERMINADO"]
    if len(ativos) >= 5:
        print(f"[Kernel] ERRO: Memoria cheia! Limite de 5 processos atingido. (Out of Memory)")
        return None
 
    novo_processo = PCB(nome, prioridade=prioridade, pai=pai)
 
    # Nivel 8: fork() — clona o contexto do pai
    if contexto_clone:
        novo_processo.contexto         = dict(contexto_clone)
        novo_processo.ciclos_restantes = contexto_clone.get("ciclos_restantes", novo_processo.ciclos_restantes)
 
    tabela_processos.append(novo_processo)
 
    # Nivel 8: registra o filho na lista do pai
    if pai is not None:
        proc_pai = _get_processo(pai)
        if proc_pai:
            proc_pai.filhos.append(novo_processo.pid)
 
    print(f"[Kernel] Processo '{nome}' criado com PID {novo_processo.pid} | prioridade={prioridade} | ciclos={novo_processo.ciclos_restantes}")
    return novo_processo
 
 
def escalonador_tick(silencioso=False):
    """Simula um ciclo (quantum) do processador executando a fila"""
 
    # Nivel 4: Escalonamento por Prioridade — ordena a fila antes de pegar o proximo
    ordem = {"high": 0, "normal": 1, "low": 2}
    prontos = sorted(
        [p for p in tabela_processos if p.estado == "PRONTO"],
        key=lambda p: ordem.get(p.prioridade, 1)
    )
 
    if not prontos:
        if not silencioso:
            bloqueados = [p for p in tabela_processos if p.estado == "BLOQUEADO"]
            zumbis     = [p for p in tabela_processos if p.estado == "ZUMBI"]
            if bloqueados:
                print("[CPU] Ociosa. Ha processos BLOQUEADOS aguardando E/S ou recurso.")
            elif zumbis:
                print("[CPU] Ociosa. Ha processos ZUMBI — use 'wait [PID]' para coletar.")
            else:
                print("[CPU] Ociosa (Idle). Nenhum processo na fila de prontos.")
        return False
 
    # Pega o primeiro processo da fila (maior prioridade)
    processo_atual = prontos[0]
 
    # CHAVEAMENTO DE CONTEXTO: Entrando na CPU
    processo_atual.estado = "EXECUTANDO"
    processo_atual.contexto["PC"] += 1  # Simula avanco do Program Counter
 
    if not silencioso:
        print(f"\n[CPU] Executando PID {processo_atual.pid} ({processo_atual.nome}) | prioridade={processo_atual.prioridade}...")
    time.sleep(1) # Simula o tempo real da CPU processando a tarefa
 
    # Decrementa o trabalho necessario (simula que ele fez progresso)
    processo_atual.ciclos_restantes -= 1
 
    # Verifica se o processo terminou seu trabalho
    if processo_atual.ciclos_restantes <= 0:
        # Nivel 7: Processo vira ZUMBI ao inves de ser removido imediatamente
        processo_atual.estado = "ZUMBI"
        if not silencioso:
            print(f"[Kernel] Processo PID {processo_atual.pid} finalizou -> estado ZUMBI (aguarda wait() do pai PID {processo_atual.pai})")
    else:
        # CHAVEAMENTO DE CONTEXTO: Saindo da CPU por preempcao (acabou o tempo dele)
        processo_atual.estado = "PRONTO"
        # Tira do inicio da fila e coloca no final (Round Robin)
        tabela_processos.remove(processo_atual)
        tabela_processos.append(processo_atual)
        if not silencioso:
            print(f"[Kernel] Chaveamento de contexto. PID {processo_atual.pid} pausado e movido para o fim da fila.")
 
    return True
 
 
# Nivel 2: Comando run — Automador de Clock
def run_automatico():
    """Executa o escalonador em loop automatico ate a fila de prontos esvaziar (Timer Interrupt)"""
    prontos = [p for p in tabela_processos if p.estado == "PRONTO"]
    if not prontos:
        print("[run] Nenhum processo PRONTO para executar.")
        return
 
    print("[run] Iniciando execucao automatica (Timer Interrupt em loop)...\n")
    tick = 0
    while True:
        prontos = [p for p in tabela_processos if p.estado == "PRONTO"]
        if not prontos:
            break
        tick += 1
        print(f"--- Tick #{tick} ---")
        escalonador_tick(silencioso=False)
 
    print(f"\n[run] Execucao automatica encerrada. {tick} tick(s) executados.")
    zumbis = [p for p in tabela_processos if p.estado == "ZUMBI"]
    if zumbis:
        print(f"[run] {len(zumbis)} processo(s) ZUMBI aguardam coleta via 'wait [PID]'.")
 
 
# Nivel 3: Gargalo de E/S — block / unblock
def block_process(pid):
    """Bloqueia um processo simulando espera por periferico (E/S)"""
    p = _get_processo(pid)
    if not p:
        print(f"[Kernel] ERRO: PID {pid} nao encontrado.")
        return
    if p.estado not in ("PRONTO", "EXECUTANDO"):
        print(f"[Kernel] ERRO: PID {pid} nao pode ser bloqueado (estado atual: {p.estado}).")
        return
    p.estado = "BLOQUEADO"
    print(f"[Kernel] PID {pid} ({p.nome}) -> BLOQUEADO aguardando E/S.")
 
 
def unblock_process(pid):
    """Desbloqueia um processo apos conclusao de E/S"""
    p = _get_processo(pid)
    if not p:
        print(f"[Kernel] ERRO: PID {pid} nao encontrado.")
        return
    if p.estado != "BLOQUEADO":
        print(f"[Kernel] ERRO: PID {pid} nao esta BLOQUEADO (estado atual: {p.estado}).")
        return
    p.estado = "PRONTO"
    p.esperando_recurso = None
    print(f"[Kernel] PID {pid} ({p.nome}) -> PRONTO (E/S concluida).")
 
 
# Nivel 5: Semaforos — lock / unlock
def lock_resource(pid, recurso="Impressora"):
    """Solicita acesso exclusivo a um recurso via Semaforo (Mutex)"""
    p = _get_processo(pid)
    if not p:
        print(f"[Kernel] ERRO: PID {pid} nao encontrado.")
        return
    if recurso not in semaforos:
        print(f"[Kernel] ERRO: Recurso '{recurso}' desconhecido. Disponiveis: {list(semaforos.keys())}")
        return
 
    if semaforos[recurso] is None:
        # Recurso livre: concede acesso imediatamente
        semaforos[recurso] = pid
        print(f"[Semaforo] PID {pid} adquiriu '{recurso}'. [LOCKED]")
    else:
        # Recurso ocupado: bloqueia o processo e coloca na fila de espera
        dono = semaforos[recurso]
        print(f"[Semaforo] '{recurso}' esta ocupado pelo PID {dono}. PID {pid} -> BLOQUEADO e entra na fila.")
        p.estado = "BLOQUEADO"
        p.esperando_recurso = recurso
        fila_recurso[recurso].append(pid)
 
        # Nivel 6: Detecta deadlock apos cada bloqueio
        ciclo = _detectar_deadlock()
        if ciclo:
            print(f"\n[DEADLOCK] !!! IMPASSE DETECTADO !!!")
            print(f"[DEADLOCK] Espera circular entre os PIDs: {ciclo}")
            print(f"[DEADLOCK] Use 'kill [PID]' para desfazer o impasse.\n")
 
 
def unlock_resource(pid, recurso="Impressora"):
    """Libera um recurso e acorda o proximo processo da fila de espera"""
    if recurso not in semaforos:
        print(f"[Kernel] ERRO: Recurso '{recurso}' desconhecido. Disponiveis: {list(semaforos.keys())}")
        return
    if semaforos[recurso] != pid:
        print(f"[Kernel] ERRO: PID {pid} nao e o dono de '{recurso}' (dono atual: {semaforos[recurso]}).")
        return
 
    print(f"[Semaforo] PID {pid} liberou '{recurso}'. [UNLOCKED]")
 
    # Acorda o proximo processo da fila de espera (se houver)
    if fila_recurso[recurso]:
        proximo_pid = fila_recurso[recurso].pop(0)
        proximo     = _get_processo(proximo_pid)
        if proximo:
            semaforos[recurso]        = proximo_pid
            proximo.estado            = "PRONTO"
            proximo.esperando_recurso = None
            print(f"[Semaforo] PID {proximo_pid} ({proximo.nome}) saiu da fila e adquiriu '{recurso}'.")
        else:
            semaforos[recurso] = None
    else:
        semaforos[recurso] = None
 
 
# Nivel 6: Deteccao de Deadlock
def _detectar_deadlock():
    """Verifica espera circular no grafo de alocacao de recursos"""
    # Monta grafo: pid_esperando -> pid_dono_do_recurso
    grafo = {}
    for p in tabela_processos:
        if p.estado == "BLOQUEADO" and p.esperando_recurso:
            dono = semaforos.get(p.esperando_recurso)
            if dono and dono != p.pid:
                grafo[p.pid] = dono
 
    # Detecta ciclo com DFS
    visitados = set()
    em_ciclo  = set()
 
    def dfs(pid, caminho):
        if pid in caminho:
            em_ciclo.update(caminho[caminho.index(pid):])
            return
        if pid in visitados or pid not in grafo:
            return
        visitados.add(pid)
        dfs(grafo[pid], caminho + [pid])
 
    for pid in list(grafo.keys()):
        if pid not in visitados:
            dfs(pid, [])
 
    return list(em_ciclo)
 
 
# Nivel 7: Zumbi — wait()
def wait_process(pid):
    """Coleta um processo ZUMBI, liberando sua entrada na tabela de processos"""
    p = _get_processo(pid)
    if not p:
        print(f"[Kernel] ERRO: PID {pid} nao encontrado.")
        return
    if p.estado != "ZUMBI":
        print(f"[Kernel] ERRO: PID {pid} nao esta no estado ZUMBI (estado atual: {p.estado}).")
        return
    tabela_processos.remove(p)
    if pid in memoria_ipc:
        del memoria_ipc[pid]
    print(f"[Kernel] wait() — PID {pid} ({p.nome}) coletado e removido da RAM. Memoria liberada.")
 
 
# Nivel 8: fork()
def fork_process(pid_pai):
    """Clona um processo pai gerando um filho com o contexto identico (syscall fork)"""
    pai = _get_processo(pid_pai)
    if not pai:
        print(f"[Kernel] ERRO: PID {pid_pai} nao encontrado.")
        return
 
    contexto_clone = {
        "PC":               pai.contexto["PC"],
        "ACC":              pai.contexto["ACC"],
        "REG":              list(pai.contexto["REG"]),
        "ciclos_restantes": pai.ciclos_restantes,
    }
 
    filho = spawn_process(
        nome           = f"{pai.nome}_fork",
        prioridade     = pai.prioridade,
        pai            = pid_pai,
        contexto_clone = contexto_clone,
    )
    if filho:
        print(f"[fork()] PID {pid_pai} ({pai.nome}) -> filho PID {filho.pid} criado com contexto clonado.")
        print(f"         Contexto: PC={filho.contexto['PC']}, ACC={filho.contexto['ACC']}, REG={filho.contexto['REG']}")
 
 
# Nivel Supremo: IPC — write / read / shm
def ipc_write(pid, mensagem):
    """Escreve uma mensagem na area de memoria compartilhada do processo"""
    p = _get_processo(pid)
    if not p:
        print(f"[Kernel] ERRO: PID {pid} nao encontrado.")
        return
    if pid not in memoria_ipc:
        memoria_ipc[pid] = []
    memoria_ipc[pid].append(mensagem)
    print(f"[IPC] PID {pid} escreveu na memoria compartilhada: \"{mensagem}\"")
 
 
def ipc_read(pid):
    """Le as mensagens da area de memoria compartilhada de um processo"""
    p = _get_processo(pid)
    if not p:
        print(f"[Kernel] ERRO: PID {pid} nao encontrado.")
        return
    msgs = memoria_ipc.get(pid, [])
    if not msgs:
        print(f"[IPC] Memoria compartilhada do PID {pid} esta vazia.")
    else:
        print(f"[IPC] Mensagens na memoria do PID {pid} ({p.nome}):")
        for i, m in enumerate(msgs, 1):
            print(f"      [{i}] {m}")
 
 
def ipc_status():
    """Exibe o estado completo da memoria compartilhada (IPC)"""
    if not memoria_ipc:
        print("[IPC] Memoria compartilhada vazia.")
        return
    print("[IPC] === Estado da Memoria Compartilhada ===")
    for pid, msgs in memoria_ipc.items():
        p    = _get_processo(pid)
        nome = p.nome if p else "???"
        print(f"  PID {pid} ({nome}): {msgs}")
 
 
# Auxiliar — busca processo por PID
def _get_processo(pid):
    for p in tabela_processos:
        if p.pid == pid:
            return p
    return None
 
 
# ==========================================
# INTERFACE COM O USUARIO (SHELL)
# ==========================================
 
def shell():
    """O laco principal que aguarda comandos do usuario"""
    global tabela_processos
 
    while True:
        try:
            # O Prompt do nosso SO
            comando = input("root@pyos:~# ").strip().lower().split()
 
            # Evita erro se o usuario apertar Enter vazio
            if not comando:
                continue
 
            acao = comando[0]
 
            if acao == "exit":
                print("Desligando o sistema...")
                break
 
            elif acao == "help":
                print("Comandos disponiveis:")
                print("  spawn [nome] [prioridade]  - Cria um novo processo (prioridade: high | normal | low)")
                print("  ps                         - Lista os processos ativos")
                print("  cpu                        - Executa 1 ciclo do processador (Escalonador)")
                print("  run                        - Executa o escalonador em loop ate a RAM esvaziar")
                print("  kill [PID]                 - Encerra um processo a forca")
                print("  block [PID]                - Bloqueia processo simulando espera de E/S")
                print("  unblock [PID]              - Desbloqueia processo (E/S concluida)")
                print("  lock [PID] [recurso]       - Solicita recurso via Semaforo (Impressora | Disco)")
                print("  unlock [PID] [recurso]     - Libera recurso do Semaforo")
                print("  wait [PID]                 - Coleta processo ZUMBI da RAM")
                print("  fork [PID]                 - Clona processo pai (syscall fork)")
                print("  write [PID] [mensagem]     - Escreve na memoria compartilhada do processo (IPC)")
                print("  read [PID]                 - Le mensagens da memoria compartilhada (IPC)")
                print("  shm                        - Exibe toda a memoria compartilhada")
                print("  clear                      - Limpa a tela")
                print("  exit                       - Desliga o sistema")
 
            elif acao == "clear":
                print("\033[H\033[J", end="") # Codigo ANSI para limpar terminal
 
            elif acao == "spawn":
                nome       = comando[1] if len(comando) > 1 else f"proc_{random.randint(10,99)}"
                prioridade = comando[2].lower() if len(comando) > 2 else "normal"
                if prioridade not in ("high", "normal", "low"):
                    print("Uso correto: spawn [nome] [prioridade]   prioridade: high | normal | low")
                else:
                    spawn_process(nome, prioridade=prioridade)
 
            elif acao == "ps":
                print(f"\n{'PID':<6} | {'NOME':<12} | {'ESTADO':<10} | {'PRIORIDADE':<10} | {'CICLOS':<6} | {'PAI':<6} | FILHOS")
                print("-" * 75)
                for p in tabela_processos:
                    pai    = str(p.pai)    if p.pai    is not None else "-"
                    filhos = str(p.filhos) if p.filhos else "-"
                    print(f"{p.pid:<6} | {p.nome[:12]:<12} | {p.estado:<10} | {p.prioridade:<10} | {p.ciclos_restantes:<6} | {pai:<6} | {filhos}")
                if not tabela_processos:
                    print("Nenhum processo em execucao.")
                # Exibe estado dos recursos
                print()
                print(f"Recursos:", end="")
                for r, dono in semaforos.items():
                    status = "LIVRE" if dono is None else f"PID {dono}"
                    print(f"  {r}=[{status}]", end="")
                # Verifica e avisa sobre deadlock
                ciclo = _detectar_deadlock()
                if ciclo:
                    print(f"\n[!] DEADLOCK detectado entre PIDs: {ciclo}")
                print("\n")
 
            elif acao == "kill":
                if len(comando) > 1:
                    try:
                        alvo = int(comando[1])
                        # Libera recursos que o processo possa estar segurando
                        for recurso, dono in list(semaforos.items()):
                            if dono == alvo:
                                unlock_resource(alvo, recurso)
                        tabela_processos = [p for p in tabela_processos if p.pid != alvo]
                        if alvo in memoria_ipc:
                            del memoria_ipc[alvo]
                        print(f"[Kernel] Sinal SIGKILL enviado. PID {alvo} destruido.")
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: kill [PID]")
 
            elif acao == "cpu":
                escalonador_tick()
 
            # Nivel 2
            elif acao == "run":
                run_automatico()
 
            # Nivel 3
            elif acao == "block":
                if len(comando) > 1:
                    try:
                        block_process(int(comando[1]))
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: block [PID]")
 
            elif acao == "unblock":
                if len(comando) > 1:
                    try:
                        unblock_process(int(comando[1]))
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: unblock [PID]")
 
            # Nivel 5
            elif acao == "lock":
                if len(comando) > 1:
                    try:
                        pid     = int(comando[1])
                        recurso = comando[2].capitalize() if len(comando) > 2 else "Impressora"
                        lock_resource(pid, recurso)
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: lock [PID] [recurso]   recurso: Impressora | Disco")
 
            elif acao == "unlock":
                if len(comando) > 1:
                    try:
                        pid     = int(comando[1])
                        recurso = comando[2].capitalize() if len(comando) > 2 else "Impressora"
                        unlock_resource(pid, recurso)
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: unlock [PID] [recurso]   recurso: Impressora | Disco")
 
            # Nivel 7
            elif acao == "wait":
                if len(comando) > 1:
                    try:
                        wait_process(int(comando[1]))
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: wait [PID]")
 
            # Nivel 8
            elif acao == "fork":
                if len(comando) > 1:
                    try:
                        fork_process(int(comando[1]))
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: fork [PID]")
 
            # Nivel Supremo
            elif acao == "write":
                if len(comando) > 2:
                    try:
                        pid      = int(comando[1])
                        mensagem = " ".join(comando[2:])
                        ipc_write(pid, mensagem)
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: write [PID] [mensagem]")
 
            elif acao == "read":
                if len(comando) > 1:
                    try:
                        ipc_read(int(comando[1]))
                    except ValueError:
                        print("Erro: O PID deve ser um numero inteiro.")
                else:
                    print("Uso correto: read [PID]")
 
            elif acao == "shm":
                ipc_status()
 
            else:
                print(f"bash: {acao}: comando nao encontrado. Digite 'help'.")
 
        # Intercepta o Ctrl+C para nao "quebrar" o simulador com erro feio
        except KeyboardInterrupt:
            print("\nPor favor, use 'exit' para sair do PyOS.")
 
 
# ==========================================
# INICIO DO SISTEMA
# ==========================================
 
if __name__ == "__main__":
    boot()
    shell()
 
