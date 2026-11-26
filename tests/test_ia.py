from ia import interpretar_solicitacao

# Cenários para testar a interpretação do modelo.
cenarios = [
    {
        "nome": "Solicitação completa",
        "mensagem": "Quero revisão amanhã às 14h."
    },
    {
        "nome": "Solicitação incompleta",
        "mensagem": "Quero agendar uma revisão."
    },
    {
        "nome": "Solicitação ambígua",
        "mensagem": "Quero levar meu carro na oficina no final da semana."
    }
]


# Executa cada cenário e apresenta o resultado.
for cenario in cenarios:

    print("\n" + "=" * 50)
    print(f"TESTE: {cenario['nome']}")
    print("=" * 50)

    print(f"Mensagem: {cenario['mensagem']}")

    try:
        resultado = interpretar_solicitacao(cenario["mensagem"])

        print("\nResultado da IA:")
        print(resultado)

    except (RuntimeError, ValueError) as erro:
        print(f"\nErro: {erro}")

