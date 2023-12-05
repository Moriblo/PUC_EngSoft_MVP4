# =============================================================================
""" 1 - Carga Inicial.
"""
# =============================================================================
import os, sys, json
import pickle
import pandas as pd
import numpy as np
import sklearn

from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from flask import redirect, request, Flask, jsonify, make_response

from urllib.parse import unquote

from logger import setup_logger
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# ===============================================================================
""" 2 - Inicializa variáveis de Informações gerais de identificação do serviço.
"""
#  ==============================================================================
info = Info(title="API AvalFIMult", version="1.0.0")
app = OpenAPI(__name__, info=info)

home_tag = Tag(name="Documentação", description="Apresentação da documentação via Swagger.")
obra_tag = Tag(name="Rota em AvalFIMult", description="Avaliação de Viabilidade de Investimento em Fundos Multimercado")
doc_tag = Tag(name="Rota em AvalFIMult", description="Documentação da API tradutor no github")

# ==============================================================================
""" 3 - Inicializa "service_name" para fins de geração de arquivo de log.
"""
# ==============================================================================
service_name = "avalfimult"
logger = setup_logger(service_name)

# ==============================================================================
""" 4 - Configurações de "Cross-Origin Resource Sharing" (CORS).
# Foi colocado "supports_credentials=False" para evitar possíveis conflitos com
# algum tipo de configuração de browser. Mas não é a melhor recomendação por 
# segurança. Para melhorar a segurança desta API, o mais indicado segue nas 
# linhas abaixo comentadas.
#> origins_permitidas = ["FIMulti"]
#> Configurando o CORS com suporte a credenciais
#> CORS(app, origins=origins_permitidas, supports_credentials=True)
#> CORS(app, supports_credentials=True, expose_headers=["Authorization"])
#> Adicionalmente utilizar da biblioteca PyJWT
"""
# ==============================================================================
# app = Flask(__name__)
CORS(app, supports_credentials=False)

# ================================================================================
""" 5.1 - DOCUMENTAÇÂO: Rota "/" para geração da documentação via Swagger.
"""
# ================================================================================
@app.get('/', tags=[home_tag])

def home():
    """Redireciona para /openapi/swagger.
    """
    return redirect('/openapi/swagger')

# ================================================================================
""" 5.2 - DOCUMENTAÇÂO: Rota "/doc" para documentação via github.
"""
# ================================================================================
@app.get('/doc', tags=[doc_tag])
def doc():
    """Redireciona para documentação no github.
    """
    return redirect('https://github.com/Moriblo/PUC_EngSoft_MVP4')

# ==============================================================================++
""" 6 - Rota "/avalfimult" para tratar o fetch de `GET`.
"""
# ==============================================================================++
@app.get('/avalfimult', tags=[obra_tag])

def avalfimult():
    """Avaliação de Viabilidade de Investimento em Fundos Multimercado.
    """
    resgate = request.args.get('resgate')
    capta = request.args.get('capta')
    patliq = request.args.get('patliq')
    pattotal = request.args.get('pattotal')

    if not all(arg is not None and arg.replace('.', '', 1).isdigit() \
        for arg in [resgate, capta, patliq, pattotal]):
        message = "Os argumentos 'resgate', 'capta', 'patliq' e 'pattotal' \
            recebidos ou estão vazios ou não são números."
        return message, 400

    # Lê identificação da origem da solicitação de uso desta API
    # origin = request.headers.get('X-Origin')

    # Verifica se o parâmetro 'entrada' foi fornecido
    if resgate is None or capta is None or patliq is None or pattotal is None:
        message = f"Erro: Parâmetros incompletos - resgate: {resgate}, capta: {capta}, \
            patliq: {patliq}, pattotal: {pattotal}"
        return message
    else:
        # if not origin:
            # message = "Erro: Sem identificação da origem da chamada!"
            # print(message)
            # return message

        resgate = float(resgate)
        capta = float(capta)
        patliq = float(patliq)
        pattotal = float(pattotal)

        if patliq < 1000000:
            message = "Erro: patliq deve ser >= 1M !!!"
            return message
        path_pkl = "../modelos_ML/"
        modelo_pkl = "Pkl_Model_FIMulti_CART.pkl"
        scaler_pkl = "Pkl_Scaler_Standard.pkl"
        pathmodel = path_pkl + modelo_pkl
        pathscaler = path_pkl + scaler_pkl

        with open(pathmodel, "rb") as f:
            model = pickle.load(f)
        with open(pathscaler, "rb") as s:
            scaler = pickle.load(s)

        # Estabelece o vetor com os dados informados
        x_entrada = [[resgate, capta, patliq, pattotal]]
        entrada = scaler.transform(x_entrada) # Aplica a formatação do scaler no vetor

        # Aplica o modelo para os valores informados
        sugest = model.predict(entrada)

        # Converter o resultado (sugestão) em uma string
        sugest_str = str(sugest[0])
        if sugest_str != "0" and sugest_str != "1":
            message = "Erro: Nenhum resultado foi obtido!!!" + sugest_str
            return message
        elif sugest_str == "0":
            resultado = "Inviável"
        elif sugest_str == "1":
            resultado = "Viável"
        message = "O resultado obtido foi: " + resultado

        # Retornar com SUGESTÃO (Viável ou Inviável) para a aplicação no fundo de investimento
        print("Modelo utilizado: " + str(model))
        print("Formatação utilizada: " + str(scaler))
        print("Valores recebidos: ", "resgate:", resgate, "captação:", capta, \
            "Patrim. Liq.:", patliq, "Patrim. Total:", pattotal)
        print("Valores convertidos: ", entrada)
        print(message + " " + sugest_str)
        return sugest_str


# ===============================================================================
""" 7 - Garante a disponibilidade da API em "suspenso".
"""
# ===============================================================================
if __name__ == '__main__':
    app.run(port=5001, debug=True)