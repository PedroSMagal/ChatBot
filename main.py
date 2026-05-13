import smtplib
from email.mime.text import MIMEText
import requests
from io import BytesIO
from PIL import Image
from google import genai

# ==========================================
# 1. CONFIGURAÇÕES PRINCIPAIS
# ==========================================

CHAVE_API_GEMINI = "AIzaSyCMY5r-l4q6JEeQzP17bmFolhd9CoJWQYM"

EMAIL_REMETENTE = "botdeliveryia@gmail.com"
SENHA_REMETENTE = "tevarrckzrgulknk"
EMAIL_DESTINO = "narudro2015@gmail.com"

URL_FRENTE = "https://raw.githubusercontent.com/PedroSMagal/ChatBot/refs/heads/main/cardapiofrente.png"
URL_TRAS = "https://raw.githubusercontent.com/PedroSMagal/ChatBot/refs/heads/main/cardapiotras.png"
URL_BAIRROS = "https://raw.githubusercontent.com/PedroSMagal/ChatBot/refs/heads/main/bairros.txt"

MODELO_GEMINI = "models/gemini-2.5-flash"

# ==========================================
# 2. ENVIO DE E-MAIL
# ==========================================

def enviar_recibo(resumo):

    print("\n[Sistema] Enviando pedido para a cozinha...")

    msg = MIMEText(resumo, 'plain', 'utf-8')

    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO
    msg['Subject'] = "NOVO PEDIDO - Degaslivery"

    try:

        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.starttls()

        server.login(
            EMAIL_REMETENTE,
            SENHA_REMETENTE
        )

        server.sendmail(
            EMAIL_REMETENTE,
            EMAIL_DESTINO,
            msg.as_string()
        )

        server.quit()

        print("[Sistema] Pedido enviado com sucesso!")

    except Exception as erro:

        print(f"[ERRO EMAIL] {erro}")

# ==========================================
# 3. BAIXAR ARQUIVOS
# ==========================================

def baixar_arquivos():

    print("[Sistema] Baixando cardápio e bairros do GitHub...")

    try:

        resposta_frente = requests.get(URL_FRENTE)
        resposta_tras = requests.get(URL_TRAS)
        resposta_bairros = requests.get(URL_BAIRROS)

        img_frente = Image.open(
            BytesIO(resposta_frente.content)
        )

        img_tras = Image.open(
            BytesIO(resposta_tras.content)
        )

        bairros = resposta_bairros.text

        return img_frente, img_tras, bairros

    except Exception as erro:

        print(f"[ERRO DOWNLOAD] {erro}")

        return None, None, None

# ==========================================
# 4. EXTRAIR CARDÁPIO PARA TEXTO
# ==========================================

def extrair_cardapio(client, img_frente, img_tras):

    print("[Sistema] Extraindo cardápio das imagens...")

    prompt = """
Extraia TODO o conteúdo dessas imagens de cardápio.

Organize:
- Categorias
- Produtos
- Preços

Retorne em texto simples e organizado.

NÃO invente produtos.
NÃO invente preços.
"""

    try:

        resposta = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=[
                prompt,
                img_frente,
                img_tras
            ]
        )

        print("[Sistema] Cardápio convertido para texto.")

        return resposta.text

    except Exception as erro:

        print(f"[ERRO EXTRAÇÃO CARDÁPIO] {erro}")

        return None

# ==========================================
# 5. GERAR PROMPT FIXO
# ==========================================

def criar_prompt_sistema(cardapio_texto, bairros):

    prompt = f"""
Você é o Degaslivery, atendente virtual de uma pastelaria.

CARDÁPIO OFICIAL:

{cardapio_texto}

BAIRROS PERMITIDOS:

{bairros}

REGRAS OBRIGATÓRIAS:

1. Venda APENAS produtos do cardápio.

2. Nunca invente:
- produtos
- preços
- promoções

3. Vá somando o total do pedido.

4. Pergunte:
- entrega
- retirada

5. Se for entrega:
- pergunte o bairro

6. Se o bairro NÃO estiver na lista:
- recuse educadamente

7. Peça:
- endereço completo
- forma de pagamento

8. Quando o cliente confirmar:
- escreva exatamente:
[PEDIDO_FINALIZADO]

9. Após a tag:
- gere um resumo completo
- inclua total
- inclua endereço
- inclua forma de pagamento

10. Seja objetivo e educado.
"""

    return prompt

# ==========================================
# 6. FUNÇÃO PRINCIPAL
# ==========================================

def main():

    print("=" * 50)
    print("       BEM-VINDO AO DEGASLIVERY BOT")
    print("=" * 50)

    # ==========================================
    # BAIXA ARQUIVOS
    # ==========================================

    img_frente, img_tras, bairros = baixar_arquivos()

    if not img_frente:

        print("[Sistema] Falha ao baixar arquivos.")
        return

    # ==========================================
    # CONFIGURA GEMINI
    # ==========================================

    try:

        client = genai.Client(
            api_key=CHAVE_API_GEMINI
        )

        print("[Sistema] API Gemini conectada.")

    except Exception as erro:

        print(f"[ERRO API] {erro}")
        return

    # ==========================================
    # EXTRAI CARDÁPIO UMA ÚNICA VEZ
    # ==========================================

    cardapio_texto = extrair_cardapio(
        client,
        img_frente,
        img_tras
    )

    if not cardapio_texto:

        print("[Sistema] Falha ao processar cardápio.")
        return

    # ==========================================
    # CRIA PROMPT FIXO
    # ==========================================

    prompt_sistema = criar_prompt_sistema(
        cardapio_texto,
        bairros
    )

    # ==========================================
    # HISTÓRICO
    # ==========================================

    historico = []

    print("\nDegaslivery: Olá! Sou o Degaslivery, seu atendente virtual.")
    print("O que vai querer pedir hoje?")

    # ==========================================
    # LOOP PRINCIPAL
    # ==========================================

    while True:

        mensagem = input("\nVocê: ")

        if mensagem.lower() in ["sair", "exit", "fechar"]:

            print("\nDegaslivery: Atendimento encerrado.")
            break

        historico.append(f"Cliente: {mensagem}")

        conversa = "\n".join(historico)

        try:

            print("[Sistema] Enviando mensagem para o Gemini...")

            resposta = client.models.generate_content(
                model=MODELO_GEMINI,
                contents=[
                    prompt_sistema,
                    conversa
                ]
            )

            texto_resposta = resposta.text

        except Exception as erro:

            print(f"\n[ERRO GEMINI] {erro}")
            continue

        historico.append(
            f"Atendente: {texto_resposta}"
        )

        # ==========================================
        # FINALIZAÇÃO
        # ==========================================

        if "[PEDIDO_FINALIZADO]" in texto_resposta:

            resumo = texto_resposta.replace(
                "[PEDIDO_FINALIZADO]",
                ""
            )

            print(f"\nDegaslivery: {resumo}")

            enviar_recibo(resumo)

            print("\n[Sistema] Atendimento finalizado.")

            break

        else:

            print(f"\nDegaslivery: {texto_resposta}")

    input("\nPressione ENTER para encerrar...")

# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":
    main()
