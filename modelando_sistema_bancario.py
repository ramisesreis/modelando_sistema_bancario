import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, endereco, data_nascimento):
        super().__init__(endereco)
        self.data_nascimento = data_nascimento  
        self.nome = nome
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente, saldo_inicial=0):
        self._saldo = saldo_inicial
        self._agencia = "0001"
        self._cliente = cliente
        self._numero = numero
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @saldo.setter
    def saldo(self, valor):
        self._saldo = valor
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
          
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo
        if excedeu_saldo:
            print("Saldo insuficiente")
            
        elif valor > 0:
            self.saldo -= valor
            print("Saque realizado com sucesso.")
            return True
        else:
            print("Valor de saque inválido")

        return False
    
    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            print(f"Depósito de R${valor} realizado com sucesso.")
        else:
            print("Valor de depósito inválido")
            return False
        
        return True
        
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite_saques=3, limite=500):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("Valor do saque excede o limite da conta.")
        elif excedeu_saques:
            print("Número máximo de saques diários excedido.")
        elif valor > self.saldo:
            print("Saldo insuficiente.")
        else:
            return super().sacar(valor)
        
        return False

        
    def __str__(self):
        return f'''\ 
        Agência:\t {self.agencia}
        Conta Corrent:\t {self.numero}, 
        titular:\t {self.cliente.nome}
        '''

class Historico:
    def __init__(self):
        self._transacoes = []

    @property 
    def transacoes(self):
        return self._transacoes
    def adicionar_transacao(self, transacao):
        self.transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

            }
        )

class Transacao(ABC):
    @property
    @abstractmethod  
    def valor(self):
        pass
    
    @abstractmethod
    def registrar(self, conta):
        pass     

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):  
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)  

def menu():
    menu = """\n
    ===== Bem-vindo ao Sistema Bancário Otimizado! =====\n
    
    Selecione uma opção:
    [1] Extrato
    [2] Depositar
    [3] Sacar
    [4] Nova Conta
    [5] Listar Contas
    [6] Novo Usuário
    [7] Sair
    => """

    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes
    if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None   

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui conta.")
        return
    # FIXME: não permite cliente escolher conta
    return cliente.contas[0]

def exibir_extrato(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    
    if not cliente:
        print("Cliente não encontrado.")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("\n=== Extrato ===\n")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['data']}:\n{transacao['tipo']}:\nR$ {transacao['valor']:.2f}\n"
               
    print(extrato)
    print(f"\nSaldo:\nR$ {conta.saldo:.2f}\n")
    print("=== Fim do Extrato ===\n")

def depositar(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return

    valor = float(input("Digite o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        print("Cliente não possui conta.")
        return
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    
    if not cliente:
        print("Cliente não encontrado.")
        return

    valor = float(input("Digite o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Digite o CPF do usuário para vincular à conta: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado. Por favor, crie um cliente antes de criar uma conta.")
        return 
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta criada com sucesso!")
    
def listar_contas(contas):
    for conta in contas:
        print("=" * 30)
        print(textwrap.dedent(str(conta)))

def criar_cliente(clientes):
    cpf = input("Digite o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)
    if cliente:
        print("Já existe um cliente com esse CPF.")
        return
    
    nome = input("Digite o nome completo: ")
    data_nascimento = input("Digite a data de nascimento (DD/MM/AAAA): ")
    endereco = input("Digite o endereço completo: ")
    
    cliente = PessoaFisica(nome=nome, cpf=cpf, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(cliente)
    print("Cliente criado com sucesso!")
    return cliente


def criar_usuario(clientes):
    return criar_cliente(clientes)


def main():
    clientes = []
    contas = []
    
    while True:
        opcao = menu()

        if opcao == "1": # Extrato
            exibir_extrato(clientes)

        elif opcao == "2": # Depositar
            depositar(clientes)
            
        elif opcao == "3": # Sacar
            sacar(clientes)
              
        elif opcao == "4":
            numero_conta = len(contas) + 1  # O número da conta é o índice + 1
            criar_conta(numero_conta, clientes, contas)
                
        elif opcao == "5":  # Listar Contas
            listar_contas(contas)
        
        elif opcao == "6": # Novo Usuário
            criar_usuario(clientes)
                
        elif opcao == "7": # Sair
            print("Obrigado por usar o Sistema Bancário Otimizado. Até logo!")
            break

        else:
            print("Opção inválida. Por favor, tente novamente.")

main()