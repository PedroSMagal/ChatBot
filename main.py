import smtplib
from email.mime.text import MIMEText
import requests
from io import BytesIO
from PIL import Image
import google.generativeai as genai

# ==========================================
# 1. CONFIGURAÇÕES PRINCIPAIS
# ==========================================
CHAVE_API_GEMINI = "AIzaSyAtTg5r3ayXTAaNwMhiLjP4Z4iYQT9t_sI"


EMAIL_REMETENTE = "botdeliveryia@gmail.com"
SENHA_REMETENTE = "tevarrckzrgulknk'" 
EMAIL_DESTINO = "narudro2015@gmail.com"

URL_FRENTE = "https://raw.githubusercontent.com/PedroSMagal/ChatBot/refs/heads/main/cardapiofrente.png"
URL_TRAS = "https://raw.githubusercontent.com/PedroSMagal/ChatBot/refs/heads/main/cardapiotras.png"
URL_BAIRROS = "https://raw.githubusercontent.com/PedroSMagal/ChatBot/refs/heads/main/bairros.txt"

# ==========================================
# 2. FUNÇÃO DE ENVIO DE E-MAIL
# ==========================================
def enviar_recibo(resumo):
    print("\n[Sistema] Enviando pedido para a cozinha...")
    msg = MIMEText(resumo, 'plain')
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO
    msg['Subject'] = "NOVO PEDIDO - Degaslivery"
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_REMETENTE)
        server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINO, msg.as_string())
        server.quit()
        print("[Sistema] Pedido enviado com sucesso para o e-mail!")
    except Exception as erro:
        print(f"[Erro no E-mail] {erro}")

# ==========================================
# 3. LÓGICA PRINCIPAL DO BOT
# ==========================================
def main():
    print("="*50)
    print("       BEM-VINDO AO DEGASLIVERY BOT")
    print("="*50)
    print("[Sistema] Baixando cardápio e bairros do GitHub...")

    # Baixa os arquivos do GitHub direto para a memória
    img_frente = Image.open(BytesIO(requests.get(URL_FRENTE).content))
    img_tras = Image.open(BytesIO(requests.get(URL_TRAS).content))
    bairros_permitidos = requests.get(URL_BAIRROS).text

    # Configura a Inteligência Artificial
    genai.configure(api_key=CHAVE_API_GEMINI)
    modelo = genai.GenerativeModel('gemini-flash')

    # Regras de comportamento do Bot
    instrucoes = f"""
    Você é o Degaslivery, o atendente virtual da Pastelaria.
    Eu te enviei as imagens do nosso cardápio (frente e verso).
    
    Regras:
    1. Só venda o que estiver nas imagens. Vá somando o total.
    2. Pergunte se é para Entrega ou Retirada. 
    3. Se for entrega, pergunte o Bairro. Só entregamos nestes bairros: {bairros_permitidos}. Se não estiver na lista, recuse a entrega.
    4. Peça endereço completo e forma de pagamento.
    5. Quando o cliente confirmar o pedido final, coloque a tag [PEDIDO_FINALIZADO] seguida do resumo do pedido.
    """

    # Inicia a conversa passando as imagens e as regras
    chat = modelo.start_chat(history=[
        {"role": "user", "parts": [img_frente, img_tras, instrucoes]},
        {"role": "model", "parts": ["Entendido! Estou pronto para anotar os pedidos."]}
    ])

    print("Degaslivery: Olá! Sou o Degaslivery, seu atendente virtual. O que vai querer pedir hoje?")
    
    # Loop de conversa com o usuário
    while True:
        mensagem = input("\nVocê: ")
        resposta = chat.send_message(mensagem).text
        
        # Verifica se a IA colocou a tag de finalização
        if "[PEDIDO_FINALIZADO]" in resposta:
            resumo_limpo = resposta.replace("[PEDIDO_FINALIZADO]", "")
            print(f"\nDegaslivery: {resumo_limpo}")
            enviar_recibo(resumo_limpo)
            break
        else:
            print(f"\nDegaslivery: {resposta}")

    input("\nPressione ENTER para encerrar...")

# Ponto de partida do programa
if __name__ == "__main__":
    main()