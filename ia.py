import json
import logging
import ollama

from datetime import date, timedelta
from config import MODELO_IA, OLLAMA_HOST

# Configuração do cliente Ollama

cliente_ollama = ollama.Client(host=OLLAMA_HOST)

# Configuração de log

logger = logging.getLogger(__name__)


# Função para criar o prompt
def criar_prompt(mensagem: str) -> str:
   
    hoje = date.today().isoformat()

    return f"""
Você é um assistente virtual da oficina Auto Fácil.

Sua tarefa é extrair informações de pedidos de agendamento.

Data atual: {hoje}

Extraia os seguintes campos:

- data: data solicitada ou expressão relativa.
- horario: horário solicitado no formato HH:MM.
- servico: serviço explicitamente solicitado.

REGRAS OBRIGATÓRIAS:

1. Nunca invente datas ou horários.
2. Se o cliente não informar a data, retorne null.
3. Se o cliente não informar o horário, retorne null.
4. Não utilize horários padrão ou disponíveis como
   substitutos para informações ausentes.
5. Para expressões relativas como "amanhã", "hoje"
   e "depois de amanhã", retorne a expressão original
   no campo data, sem calcular a data.
6. Expressões vagas como "final da semana" devem
   retornar null no campo data.
7. Se o serviço não estiver claramente identificado,
   retorne null.
8. Quando o cliente solicitar revisão, utilize
   exatamente "revisao" no campo servico.
9. Não complete informações por conta própria.

Retorne exclusivamente um JSON válido,
sem explicações, utilizando exatamente esta estrutura:

{{
    "data": null,
    "horario": null,
    "servico": null
}}

Mensagem do cliente:
{mensagem}
"""

# Função para consultar a IA
def consultar_ia(prompt: str) -> str:
  
    try:
        resposta = cliente_ollama.chat(
            model=MODELO_IA,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

        return resposta.message.content

    except Exception as erro:
        logger.exception("Erro ao se comunicar com o Ollama.")

        raise RuntimeError(
            "Não foi possível acessar o serviço de inteligência artificial."
        ) from erro

# Função para normalizar datas
def normalizar_data(mensagem: str) -> str | None:

    mensagem = mensagem.lower()
    hoje = date.today()

    expressoes_ambiguas = [
        "final da semana",
        "fim da semana",
        "durante a semana",
        "no começo da semana",
        "no início da semana",
        "na próxima semana",
        "semana que vem",
        "mais tarde",
        "algum dia"
    ]

    if any(expressao in mensagem for expressao in expressoes_ambiguas):
        return None

    if "depois de amanhã" in mensagem:
        return (hoje + timedelta(days=2)).isoformat()

    if "amanhã" in mensagem:
        return (hoje + timedelta(days=1)).isoformat()

    if "hoje" in mensagem:
        return hoje.isoformat()

    return None

# Função para interpretar a solicitação
def interpretar_solicitacao(mensagem: str) -> dict:
  
    if not mensagem or not mensagem.strip():
        raise ValueError("A mensagem não pode estar vazia.")

    prompt = criar_prompt(mensagem)

    resposta = consultar_ia(prompt)

    try:
        dados = json.loads(resposta)

    except json.JSONDecodeError as erro:
        logger.exception("O modelo retornou um JSON inválido.")

        raise ValueError(
            "Não foi possível interpretar a solicitação."
        ) from erro

    if not isinstance(dados, dict):
        raise ValueError("A resposta da IA possui formato inválido.")

    campos_obrigatorios = ["data", "horario", "servico"]

    if not all(campo in dados for campo in campos_obrigatorios):
        raise ValueError(
            "A resposta da IA não contém todos os campos obrigatórios."
        )

    data_calculada = normalizar_data(mensagem)

    dados["data"] = data_calculada

    if dados["servico"]:
        if dados["servico"].strip().lower() in ["revisão", "revisao"]:
            dados["servico"] = "revisao"

    return dados
