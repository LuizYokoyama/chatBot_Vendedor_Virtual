# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions



from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType

from rasa_sdk.events import ActionExecuted
from rasa_sdk.events import UserUttered

from actions.numeros import gn
import actions.grafo as g
from actions.cores import gc
from actions.produtos import gt
from unicodedata import normalize
import string
import json
import requests
import locale
import pandas as pd
import time
from datetime import timedelta
from datetime import datetime
from sqlalchemy import create_engine

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def mensagens(idAtual):
	'''Retorna uma lista com as mensagens de log do comando /log10'''
	# Postgres username, password, e database name
	POSTGRES_ADDRESS = 'localhost' 
	POSTGRES_PORT = '5432'
	POSTGRES_USERNAME = 'postgres' 
	POSTGRES_PASSWORD = 'chatbot' 
	POSTGRES_DBNAME = 'rasa' 
	postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'.format(
							username= POSTGRES_USERNAME,
							password= POSTGRES_PASSWORD,
							ipaddress= POSTGRES_ADDRESS,
							port= POSTGRES_PORT,
							dbname= POSTGRES_DBNAME))
	cnx = create_engine(postgres_str)
	ts = datetime.timestamp(datetime.fromtimestamp(time.time())- timedelta(minutes=10))
	df = pd.read_sql_query("SELECT * FROM events", cnx)
	df = df[df.timestamp > ts]
	df = df[df.sender_id == idAtual]

	#CRIAÇÃO DO DICIONÁRIO DA CONVERSA COM ID
	dci = {}
	i=0
	for ln in range(len(df['id'])):
			dci.update({i: json.loads(df.iat[ln,6])})
			i+=1
	slt = []
	x = ['action_listen', 'session_started', '/start', 'log10', 'user_featurization', 'rewind',
		 'action_session_start', 'action_log', '/log10', 'fim_do_log10', 'Log10:']
	for i in range(len(dci)):
		if 'text' in dci[i]:
				if dci[i]['text'] == '/log10':
					slt.append('/log10')
		if 'text' in dci[i]:
				if dci[i]['text'] == 'fim_do_log10':
					slt.append('fim_do_log10')
		if dci[i]['event'] not in x:
			if dci[i]['event'] == 'action':
				if 'name' in dci[i]:
					if dci[i]['name'] not in x:
						slt.append('  - action: '+str(dci[i]['name']))
			if dci[i]['event'] == 'bot':
				if 'metadata' in dci[i]:
					if 'utter_action' in dci[i]['metadata']:
						if dci[i]['metadata']['utter_action'].split('/')[0] in ['utter_chitchat', 'utter_faq']:
							slt.append('    Tipo: '+dci[i]['metadata']['utter_action'])
				if 'text' in dci[i]:
					if dci[i]['text'] not in x:
						slt.append('    - text: '+str(dci[i]['text']))
			if dci[i]['event'] == 'user':
				if 'parse_data' in dci[i]['event']:
					if 'response_selector' in dci[i]['event']['parse_data']:
						slt.append('  Tipo: '+str(dci[i]['event']['parse_data']['response_selector']['chitchat']['response']['intent_response_key']))
				if 'text' in dci[i]:
					if dci[i]['text'] not in x:
						slt.append('  examples: |  \n    - '+str(dci[i]['text']))
			if dci[i]['event'] == 'slot':
				if 'name' in dci[i]:
					slt.append('  - slot_was_set:    \n  - '+str(dci[i]['name'])+': '+str(dci[i]['value']))
			if 'parse_data' in dci[i]: 
				if dci[i]['parse_data']['intent']['name'] not in x:
					if 'intent' in dci[i]['parse_data']:
						if dci[i]['parse_data']['intent']['name'] not in x:
							slt.append('  - intent: '+str(dci[i]['parse_data']['intent']['name']))
			if 'parse_data' in dci[i]: 
				if dci[i]['parse_data']['entities']:
					for e in dci[i]['parse_data']['entities']:
						slt.append('    entities:  \n    - '+str( e['entity'])+': '+str( e['value']))
	r = []
	ret = []
	if slt:
		while not r:
			while slt:
				t = slt.pop()
				if t == 'fim_do_log10':
					break
				else:
					r.append(t)
			if not slt:
				break
			
		while not ret:
			while r:
				t = r.pop()
				if t == '/log10':
					break
				else:
					ret.append(t)
			if not r:
				break

	return ret

def listarTodosProdutos():
	'''Retorna uma string usada como mensagem do bot, com um produto em cada linha'''
	endpoint = 'Https://shopizer.multitrem.com/api/v1/search/'
	p = { "count": 100,  "query": "1",  "start": 0}
	r = requests.post(endpoint, json= p)
	qtd = r.json()['categoryFacets'][0]['productCount']
	ret = ''
	for p in r.json()['products']:
		ret += str(p['description']['name'])+'  \n'

	return ret

def listarProdutos(produto):
	'''Retorna uma lista de produtos com um produto em cada linha na posição 0,
	   quantidade de ítens na posição 1, tupla do produto na posição 2'''
	produto = normalize('NFKD', produto).encode('ASCII','ignore').decode('ASCII')  #retira acento
	produto = produto.lower()
	palavras = produto.split()
	palavra = []
	buscar = ''
	for i in palavras:
		if i[len(i)-1] == 's':
			if not i in ['lapis']:  # lista de produtos que terminam em s, mas não são plural
				i = i[:-1]  #remove o plural
		palavra.append(i)
		buscar += i + ' '
	
	endpoint = 'Https://shopizer.multitrem.com/api/v1/search/'
	p = { "count": 12,  "query": buscar,  "start": 0}
	r = requests.post(endpoint, json= p)
	if (r.status_code != 200):  #200 indica que achou produto
		return []
	qtd = r.json()['productCount']
	if qtd == 0:
		return []

	ret = ['']
	l = []
	l1 = []
	l2 = []
	l3 = []
	l4 = []
	l5 = []
	l6 = []
	i = 0
		
	for p in r.json()['products']:  # para retornar somente os produtos que contenham apenas todas as palavras pesquisadas
		if palavra[0] in normalize('NFKD', str(p['description']['name']).lower()).encode('ASCII','ignore').decode('ASCII'):
			l1.append([str(p['description']['name']), p['id'], p['quantity'], p['price'], 'a'])  # tupla do produto
			i += 1
	if len(palavra) >= 2:
		for p in l1:
			if palavra[1] in normalize('NFKD', p[0].lower()).encode('ASCII','ignore').decode('ASCII'):
				l2.append(p)  # tupla do produto
	if len(palavra) >= 3:
		for p in l2:
			if palavra[2] in normalize('NFKD', p[0].lower()).encode('ASCII','ignore').decode('ASCII'):
				l3.append(p)  # tupla do produto
	if len(palavra) >= 4:
		for p in l3:
			if palavra[3] in normalize('NFKD', p[0].lower()).encode('ASCII','ignore').decode('ASCII'):
				l4.append(p)  # tupla do produto
	if len(palavra) >= 5:
		for p in l4:
			if palavra[4] in normalize('NFKD', p[0].lower()).encode('ASCII','ignore').decode('ASCII'):
				l5.append(p)  # tupla do produto
	if len(palavra) >= 6:
		for p in l5:
			if palavra[5] in normalize('NFKD', p[0].lower()).encode('ASCII','ignore').decode('ASCII'):
				l6.append(p)  # tupla do produto
	
	if l6:
		l = l6
		i = len(l6)
	elif l5:
		l = l5
		i = len(l5)
	elif l4:
		l = l4
		i = len(l4)
	elif l3:
		l = l3
		i = len(l3)
	elif l2:
		l = l2
		i = len(l2)
	elif l1:
		l = l1
		i = len(l1)
	
	if i == 1:
		ret[0] = l[0][0]
	else:  # insere índice de letras nos produtos
		i = 0
		for p in l:
			ret[0] += string.ascii_lowercase[i] +') '+ p[0]+' por '+locale.currency(p[3], grouping=True, symbol='R$')+'  \n'
			p[4] = string.ascii_lowercase[i]
			i += 1
	ret.append(i)
	if l:
		ret.append(l)
	else:
		return []
	return ret

def coresDisponiveis(id):
	'''Retorna um dicionário das cores do produto no formato {'cor': id_cor}'''
	cores = {}
	endpoint = 'Https://shopizer.multitrem.com/api/v1/private/product/{id}/attributes'.format(id = id)
	r = requests.get(endpoint, auth=('admin@shopizer.com', 'chatbo#2'))
	if r.status_code == 200:
		for i in r.json()['attributes']:
			if i['option']['code'] == 'cor':
				cores.update({i['optionValue']['description']['name'].lower(): i['id']})
	return cores

def dizerCores(cores):
	'''Retorna uma string para o bot usar, com todas as cores disponíveis'''
	r = ''
	l = list(cores)
	i = len(l)
	for c in l:
		i -= 1
		if i == 1: 
		  r += c + ' e '
		elif i == 0:
		  r += c
		else:
		  r += c + ', '
	return r

def criar_dic(car):
	'''CRIA UM DICIONÁRIO DO CARRINHO'''
	endpoint = 'Https://shopizer.multitrem.com/api/v1/cart/'+car
	param = {}
	d = {}
	r = requests.get(endpoint, json= param)  # GET
	if (r.status_code == 200):  # o código 200 indica sucesso
		produtos= r.json()['products']
		for i in range(len(produtos)):
			if len(produtos[i]['cartItemattributes']) != 0:
				d.update({ produtos[i]['description']['name']: [ produtos[i]['id'], produtos[i]['quantity'], produtos[i]['price'], produtos[i]['cartItemattributes'][0]['optionValue']['name'] ]})  # id e qtd são int, price é float
			else:
				d.update({ produtos[i]['description']['name']: [ produtos[i]['id'], produtos[i]['quantity'], produtos[i]['price'], '']})  # id e qtd são int, price é float
		return d

def descreveCarrinho(d):
	'''Retorna uma string com a descrição formatada do carrinho'''
	c = ''
	if d:
		l = list(d)
		for p in l:
			precoR = locale.currency(d[p][2], grouping=True, symbol='R$')
			c += (p+' '+str(d[p][3])+' '+precoR+'  \n'+' Qtd: '+str(d[p][1])+'  \n')		
	return c

class ActionConsultarProduto(Action):
	'''Ação de consultar um produto para venda'''

	def name(self) -> Text:
		return "action_consultar_produto"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		produto = tracker.get_slot('produto')
		qtd = next(tracker.get_latest_entity_values('qtd'), None)
		corId = tracker.get_slot('corId')
		inf_ret = tracker.get_slot('inf_ret')
		inf_prod = tracker.get_slot('inf_prod')
		pid = tracker.get_slot('pid')
		lista_de_produtos = eval(str(tracker.get_slot('lista_de_produtos')))
		cor = next(tracker.get_latest_entity_values('cor'), None)
		produto_oferecido = tracker.get_slot('produto_oferecido')
		msg = tracker.latest_message['text']
		idCor = []
		ml = False
		pqtd = tracker.get_slot('pqtd')
		produto_encontrado = tracker.get_slot('produto_encontrado') 
		preco = tracker.get_slot('preco')  #tipo float
		precoR = tracker.get_slot('precoR')  # string R$
		pergTem = False
		
		if produto:
			produto = produto.lower()
			pn = normalize('NFKD', produto).encode('ASCII','ignore').decode('ASCII')  #retira acento
			palavras = pn.split()
			buscar = ''
			for i in palavras:
				if i[len(i)-1] == 's':
					i = i[:-1]  #remove o plural
				buscar += i + ' '
			buscar = buscar[:-1]  #remove o espaço no final
			if buscar in gt:
				dispatcher.utter_message(text= 'Me desculpe, mas não vendemos '+gt[buscar]+'.  \nPor enquanto temos somente produtos de papelaria.')
				return []
		if msg:
			msg = msg.lower()
			listaPerg = ['tem', 'têm', 'teria', 'teriam', 'vende', 'vendem', 'saber', 'sabe', 'estoque', 'disponível', 'disponivel']
			for i in listaPerg:
				if i in msg:
					pergTem = True
					break
			listaFrete = ['frete', 'envia', 'envie', 'entreg', 'despach']
			for i in listaFrete:
				if i in msg:
					dispatcher.utter_message(response= 'utter_faq/saber_tipos_de_entrega')
					return []
										
		if inf_ret:
			return [ActionExecuted("action_listen")] + [UserUttered("/ret_carrinho", { 
					"intent": {"confidence": 1, "name": "ret_carrinho"}, "entities": [] })]
		if inf_prod:
			return [ActionExecuted("action_listen")] + [UserUttered("/saber_caracteristicas", { 
					"intent": {"confidence": 1, "name": "saber_caracteristicas"}, "entities": [] })]
		
		if cor:
			cor = cor.lower()
		if corId:
			corId = eval(corId)
		if produto_encontrado or produto:
			if produto:
				if lista_de_produtos:
					if len(produto) == 1:  
						
						if lista_de_produtos[1] == 1:  # se só for informado apenas um produto, não há opções de escolha
							dispatcher.utter_message(text= 'Descule-me! Mas não havia opções de produtos para você escolher pela letra agora.')
							return []
						if produto not in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'l']:
							dispatcher.utter_message(text= 'Descule-me! Mas não entendi o que você quis dizer com esse '+produto)
							return []
						for i in lista_de_produtos[2]:  # procura pela letra da opção; se a letra não for encontrada, o produto será buscado depois pela falta de pid
							if produto in i[4]:
								produto_encontrado = i[0]
								pid = i[1]
								pqtd = i[2]
								preco = i[3]
								precoR = locale.currency(preco, grouping=True, symbol='R$')
								ml = True
					else:
						achou = False
						for i in lista_de_produtos[2]:  # verifica se o produto informado está na mesma lista anterior
							if produto in normalize('NFKD', i[0].lower()).encode('ASCII','ignore').decode('ASCII'):  #retira acento
								produto_encontrado = i[0]
								pid = i[1]
								pqtd = i[2]
								preco = i[3]
								precoR = locale.currency(preco, grouping=True, symbol='R$')
								ml = True
								achou = True
						if not achou:
							dispatcher.utter_message(response= 'utter_nao_temos')
							return [SlotSet("produto", None), SlotSet("pid", None), SlotSet("lista_de_produtos", None), SlotSet("produto_encontrado", None), SlotSet("pqtd", None), SlotSet("preco", None), SlotSet("precoR", None)]

				if not ml:   # se o produto informado não está na mesma lista anterior
					dispatcher.utter_message(response= 'utter_por_favor_aguarde_consulta')
					listaProdutos = listarProdutos(produto)
					if listaProdutos:
						if listaProdutos[1] > 1:
							if pergTem:
								dispatcher.utter_message(response= 'utter_temos_sim')
							dispatcher.utter_message(text= 'O sistema me retornou '+str(listaProdutos[1])+' produtos quando eu pesquisei por '+produto+'  \nPor favor, escolha somente um deles.')
							dispatcher.utter_message(text= listaProdutos[0]+'  \nSeria qual destes?')
							return [SlotSet("lista_de_produtos", listaProdutos)]
						elif listaProdutos[1] == 1:
							if listaProdutos[2][0]:
								produto_encontrado = listaProdutos[2][0][0]
								pid = listaProdutos[2][0][1]
								pqtd = listaProdutos[2][0][2]
								preco = listaProdutos[2][0][3]
								precoR = locale.currency(preco, grouping=True, symbol='R$')
							else:
								dispatcher.utter_message(response= 'utter_nao_temos')
								return [SlotSet("produto", None), SlotSet("pid", None), SlotSet("lista_de_produtos", None), SlotSet("produto_encontrado", None), SlotSet("pqtd", None), SlotSet("preco", None), SlotSet("precoR", None)]
					else:
						dispatcher.utter_message(response= 'utter_nao_temos')
						return [SlotSet("produto", None), SlotSet("pid", None), SlotSet("lista_de_produtos", None), SlotSet("produto_encontrado", None), SlotSet("pqtd", None), SlotSet("preco", None), SlotSet("precoR", None)]
			
			if pid:
				if pergTem:
					if pqtd > 0:
						dispatcher.utter_message(response= 'utter_temos_sim')
					else:
						dispatcher.utter_message(response= 'utter_nao_temos')
						return [SlotSet("produto", None), SlotSet("pid", None), SlotSet("produto_encontrado", None), SlotSet("pqtd", None), SlotSet("preco", None), SlotSet("precoR", None)]
				if cor:
					cores = coresDisponiveis(pid)
					if cores:
						if cor[len(cor)-1] == 's':
							cor = cor[:-1]  #remove o plural
						if cor in gc:
							cor = gc[cor]  # pega cor padronizada do grafo de cores para evitar erros
						
						if cor in cores:
							C = cores[cor]
							idCor = [C, pid, cor]
							dispatcher.utter_message(text= 'Eu encontrei a cor '+ cor +' disponivel para este produto!')
						else:
							dispatcher.utter_message(text= 'Me desculpe! Mas não encontrei a cor '+ cor +' para este produto no sistema.')
					else:
						dispatcher.utter_message(response= 'utter_sem_opcoes_de_cor')
			else:
				dispatcher.utter_message(text= 'Me desculpe, mas não consegui encontrar informações sobre '+ str(produto) +' no sistema.')
				return [SlotSet("produto", None), SlotSet("pid", None), SlotSet("produto_encontrado", None), SlotSet("pqtd", None), SlotSet("preco", None), SlotSet("precoR", None)]	
			
			if not idCor:
				idCor = corId
				
			if qtd:
				qtd = qtd.lower()  #para fazer a conversão de numero por extenso, é necessáro estar em minúsculas
				if qtd in gn:
					qtd = str(gn[qtd])  #converte numero por extenso em número inteiro usando o grafo numérico
				if qtd.isdigit():
					if int(qtd) == 0:
						dispatcher.utter_message(text= 'Desculpe-me, mas não entedi a quantidade.  \nDigite um número diferente de 0, por favor.')
						return [SlotSet('qtd', None), SlotSet('corId', str(idCor)), SlotSet("pid", pid), SlotSet("produto_encontrado", produto_encontrado), SlotSet("pqtd", pqtd), SlotSet("preco", preco), SlotSet("precoR", precoR)]
					elif int(qtd) < 0:
						dispatcher.utter_message(text= 'Desculpe-me, mas não entedi a quantidade.  \nDigite um número positivo, por favor.')
						return [SlotSet('qtd', None),  SlotSet('corId', str(idCor)), SlotSet("pid", pid), SlotSet("produto_encontrado", produto_encontrado), SlotSet("pqtd", pqtd), SlotSet("preco", preco), SlotSet("precoR", precoR)]
					if qtd == '1':  # só para diferenciar texto de resposta no singular ou plural
						dispatcher.utter_message(text= "Então, o produdo escolhido é  \n" + str(qtd)+ ' ' +str(produto_encontrado)+', por '+precoR)
					else:
						dispatcher.utter_message(text= "Então, os produtos escolhidos são  \n" + str(qtd)+ ' ' +str(produto_encontrado)+', por '+precoR+' cada.')
					if corId:
						if corId[1] == pid:  # caso a cor escolhida for para o mesmo produto ainda
							dispatcher.utter_message(text= 'Na cor '+corId[2])
					if pqtd >= int(qtd):
						if int(qtd) > 1:
							p = int(qtd) * float(preco)
							pR = locale.currency(p, grouping=True, symbol='R$')
							dispatcher.utter_message(text= "O total dos " + str(qtd)+ ' fica ' + pR )
						dispatcher.utter_message(text= 'A quantidade em estoque é de '+ str(pqtd) + ' unidades.')
						dispatcher.utter_message(response= 'utter_temos')
						return [SlotSet("qtd", qtd), SlotSet("pid", pid), SlotSet("produto", produto_encontrado),  SlotSet('corId', str(idCor)), SlotSet("produto_encontrado", produto_encontrado), SlotSet("pqtd", pqtd), SlotSet("preco", preco), SlotSet("precoR", precoR)]
					else:
						if int(pqtd) > 0:
							dispatcher.utter_message(text= 'Me desculpe, mas temos somente '+str(pqtd)+ ' em estoque!  \nPor favor, informe outra quantidade ou outro produto.')
							return [SlotSet('qtd', None), SlotSet('corId', str(idCor)), SlotSet("pid", pid),  SlotSet('corId', str(idCor)), SlotSet("produto_encontrado", produto_encontrado), SlotSet("pqtd", pqtd), SlotSet("preco", preco), SlotSet("precoR", precoR)]
						dispatcher.utter_message(response= 'utter_esgotado')
						return [SlotSet("pid", None), SlotSet("produto_encontrado", None), SlotSet("pqtd", None), SlotSet("preco", None), SlotSet("precoR", None)]
				else:
						dispatcher.utter_message(text= 'Desculpe-me, mas não entedi a quantidade.  \nEscreva somente os algarismos da quantidade, por favor.')
						return [SlotSet('qtd', None), SlotSet('corId', str(idCor)), SlotSet("pid", pid), SlotSet("produto_encontrado", produto_encontrado), SlotSet("pqtd", pqtd), SlotSet("preco", preco), SlotSet("precoR", precoR)]
			elif produto_encontrado:	
				if produto_oferecido:
					dispatcher.utter_message(text= 'De '+str(produto_encontrado))
				else:
					dispatcher.utter_message(text= 'Eu encontrei '+str(produto_encontrado))
				dispatcher.utter_message(text= 'seriam quantas unidades?')
				return [SlotSet("produto_oferecido", False), SlotSet("produto", produto_encontrado), SlotSet('corId', str(idCor)), SlotSet("pid", pid), SlotSet("produto_encontrado", produto_encontrado), SlotSet("pqtd", pqtd), SlotSet("preco", preco), SlotSet("precoR", precoR) ]
			dispatcher.utter_message(response= 'utter_nao_temos')
			return [SlotSet("pid", None), SlotSet("produto_encontrado", None), SlotSet("pqtd", None), SlotSet("preco", None), SlotSet("precoR", None)]
			
		else:
			dispatcher.utter_message(response= 'utter_pergunta_qual_produto')
			return []

		

class ActionAddCar(Action):
	'''ação de adicionar produto no carrinho de compras'''
	
	def name(self) -> Text:
		return "action_add_car"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		produto = tracker.get_slot('produto')
		qtd = tracker.get_slot('qtd')
		car = tracker.get_slot('carrinho')
		pid = tracker.get_slot('pid')
		corId = tracker.get_slot('corId')
		
		if corId:
			corId = eval(corId)
		
		if pid:
			pid = int(pid)
		d = {}
		if qtd:
			qtd = qtd.lower()
		
		if not produto:
			dispatcher.utter_message(response= 'utter_pergunta_qual_produto')
			return []		
		if qtd == None: 
			dispatcher.utter_message(text= 'Por gentileza, me informe a quantidade desejada.')
			return []
		
		if qtd in gn:
			qtd = str(gn[qtd])  # converte número por extenso em inteiro
		if qtd.isdigit():
			if int(qtd) == 0:
				dispatcher.utter_message(text= 'Desculpe-me, mas não entedi a quantidade.  \nDigite um número diferente de 0, por favor.')
				return [SlotSet('qtd', None)]
			elif int(qtd) < 0:
				dispatcher.utter_message(text= 'Desculpe-me, mas não entedi a quantidade.  \nDigite um número positivo, por favor.')
				return [SlotSet('qtd', None)]
		else:
			dispatcher.utter_message(text= 'Desculpe-me, mas não entendi a quantidade.')
			dispatcher.utter_message(text= 'Por favor, tente escrever somente o número.')
			return []

		#chamada a API
		if pid:
			param = {"product":pid,"quantity":int(qtd)}	
			if corId:
				if corId[1] == pid:  # caso a cor escolhida for para o mesmo produto ainda
					#param = { "attributes": '[{"id": 8}]',"product":pid,"quantity":int(qtd)}
					param = { "attributes": [{"id": corId[0]}],"product":pid,"quantity":int(qtd)}
		else:
			dispatcher.utter_message(response= 'utter_pergunta_qual_produto')
			return []	

		if not car:  # se não possuía carrinho
			endpoint = 'Https://shopizer.multitrem.com/api/v1/cart/'		
			r = requests.post(endpoint, json= param)  # POST
		else: 
			endpoint = 'Https://shopizer.multitrem.com/api/v1/cart/'+car
			r = requests.put(endpoint, json= param)  # PUT
		if (r.status_code == 201):  # o código 201 indica sucesso
			valorTotalCar = r.json()['total']
			valorR = locale.currency(valorTotalCar, grouping=True, symbol='R$')
			qdtCar = r.json()['quantity']
			car = r.json()['code']
			d= criar_dic(car)  # CRIA UM DICIONÁRIO DO CARRINHO
			carrinho = descreveCarrinho(d)
			
			dispatcher.utter_message(text= 'O seu carrinho possui agora')
			dispatcher.utter_message(text= carrinho)
			dispatcher.utter_message(text= 'A quantidade total de ítens é '+ str(qdtCar))
			dispatcher.utter_message(text= 'O valor total é '+ str(valorR))
			dispatcher.utter_message(response= 'utter_colocado_car')
		else:
			dispatcher.utter_message(text= 'Desculpe-me, mas ocorreu alguma falha no sistema ou o estoque do produto foi insuficiente.')
			dispatcher.utter_message(text= 'Então, não foi possível adicionar ao carrinho.')
			return [SlotSet("qtd", None)]  #Zera a qtd para o usuário poder informar nova qtd
		
		# CONSULTAR GRAFO DE CONHECIMENTO PARA OFERECER UM PRODUTO
		oferecer = g.consultaGrafo(produto)
		if oferecer:
			if oferecer not in d:
			
				#ANTES DE OFERECER O PRODUTO, CONSULTAR API SE TEM EM ESTOQUE
				listaProdutos = listarProdutos(oferecer)
				if listaProdutos:
					if listaProdutos[1] == 1:
						produto_encontrado = listaProdutos[2][0][0]
						pid = listaProdutos[2][0][1]
						pqtd = listaProdutos[2][0][2]
						preco = listaProdutos[2][0][3]
						precoR = locale.currency(preco, grouping=True, symbol='R$')
						
						if pqtd >= 1:
							dispatcher.utter_message(response = 'utter_oferecer')
							dispatcher.utter_message(text= 'Gostaria de levar '+ str(oferecer)+' também? Custa só '+ precoR+' cada.')
							
							return [SlotSet("produto", None), SlotSet("carrinho", car), SlotSet("produto_encontrado", str(oferecer)), SlotSet("produto_oferecido", True),
									SlotSet("lista_de_produtos", None), SlotSet("pqtd", pqtd), SlotSet("corId", None), SlotSet("qtd", None),  
											SlotSet("preco", preco), SlotSet("precoR", precoR), SlotSet("cor", None), SlotSet("pid", pid)]
			
		dispatcher.utter_message(response= 'utter_oque_mais')
		return [SlotSet("produto", None), SlotSet("carrinho", car), SlotSet("produto_encontrado", None), SlotSet("produto_oferecido", False),
									SlotSet("lista_de_produtos", None), SlotSet("pqtd", None), SlotSet("corId", None), SlotSet("qtd", None),  
											SlotSet("preco", None), SlotSet("precoR", None), SlotSet("cor", None), SlotSet("pid", None)]


class ActionRetCar(Action):
	'''ação de retirada de produto do carrinho de compras'''
	def name(self) -> Text:
		return "action_ret_car"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		produto = tracker.get_slot('produto')
		qtd = tracker.get_slot('qtd')
		car = tracker.get_slot('carrinho')
		d = {}
		produto_encontrado = ''
		pid = ''
		qtdAtualizada = 0
		
		if not produto:
			dispatcher.utter_message(text= 'Por favor, me informe qual produto quer retirar do carrinho.')
			return [SlotSet("inf_ret", True)]		# FLAG PARA O BOT SABER QUE QUANDO INFORMAR O PRODUTO, A AÇÃO SERÁ DE RETIRADA DO CARRINHO	
			
		if car:
			d= criar_dic(car)  # CRIA UM DICIONÁRIO DO CARRINHO
		if not d:  # se não possuía carrinho, ou está vazio
			dispatcher.utter_message(text= 'Desculpe-me, mas seu carrinho está vazio agora. Ou, então, eu já não tenho mais acesso a ele.')
			return []
		else: 
			l = list(d)
			produto = produto.lower()
			pn = normalize('NFKD', produto).encode('ASCII','ignore').decode('ASCII')  #retira acento
			palavras = pn.split()
			buscar = ''
							
			for j in l:
				for i in palavras:
					if i[len(i)-1] == 's':
						i = i[:-1]  #remove o plural
					if i in normalize('NFKD', j.lower()).encode('ASCII','ignore').decode('ASCII'):
						pid = d[j][0]
						produto_encontrado = j
						
			if not pid:
				dispatcher.utter_message(text= 'O seu carrinho possui agora  \n'+ descreveCarrinho(d))
				dispatcher.utter_message(response= 'utter_produto_ja_excluido')
				return [SlotSet("inf_ret", False)]
		

		endpoint = 'Https://shopizer.multitrem.com/api/v1/cart/'+car
		if not qtd:
			pqtd = d[produto_encontrado][1] 
			if pqtd != 1:  # se a qtd no carrinho for só 1, nem precisa perguntar a qtd
				dispatcher.utter_message(text= 'Por favor, escreva a quantidade a ser retirada do carrinho.  \nPara facilitar, escreva somente os números.')
				return [SlotSet("inf_ret", True)]  # FLAG PARA O BOT SABER QUE QUANDO INFORMAR A QUANTIDADE, A AÇÃO SERÁ DE RETIRADA DO CARRINHO	
		if qtd in gn:
			qtd = str(gn[qtd])  # converte número por extenso em inteiro
		if qtd:
			qtd = qtd.lower()
			if qtd.isdigit():
				if int(qtd) == 0:
					dispatcher.utter_message(text= 'Desculpe-me, mas não entedi a quantidade a ser retirada.  \nDigite um número diferente de 0, por favor.')
					return [SlotSet("inf_ret", True)]		# FLAG PARA O BOT SABER QUE QUANDO INFORMAR A QUANTIDADE, A AÇÃO SERÁ DE RETIRADA DO CARRINHO
				elif int(qtd) < 0:
					dispatcher.utter_message(text= 'Desculpe-me, mas não entedi a quantidade a ser retirada.  \nDigite um número positivo, por favor.')
					return [SlotSet("inf_ret", True)]		# FLAG PARA O BOT SABER QUE QUANDO INFORMAR A QUANTIDADE, A AÇÃO SERÁ DE RETIRADA DO CARRINHO
			else:
				dispatcher.utter_message(text= 'Desculpe-me, mas não entendi a quantidade a ser retirada.  \nPor favor, tente escrever somente o número.')
				return [SlotSet("inf_ret", True)]		# FLAG PARA O BOT SABER QUE QUANDO INFORMAR A QUANTIDADE, A AÇÃO SERÁ DE RETIRADA DO CARRINHO
		else: 
			dispatcher.utter_message(text= 'Por favor, informe a quantidade a ser retirada do carrinho.  \nPara facilitar, escreva somente os números.')
			return [SlotSet("inf_ret", True)]		# FLAG PARA O BOT SABER QUE QUANDO INFORMAR A QUANTIDADE, A AÇÃO SERÁ DE RETIRADA DO CARRINHO
		if type(qtd) == str:
			qtd= int(qtd)
		if qtd <= d[produto_encontrado][1]:
			qtdAtualizada = d[produto_encontrado][1] - int(qtd)
		param = {"product":pid,"quantity": qtdAtualizada}
		r = requests.put(endpoint, json= param)  # PUT
		if (r.status_code == 201):  # o código 201 indica sucesso
			c = r.json()
			if 'code' in c:  #se o carrinho ainda exite
				car = c['code']
				valorTotalCar = c['total']
				valorR = locale.currency(valorTotalCar, grouping=True, symbol='R$')
				qdtCar = c['quantity']
			else:
				dispatcher.utter_message(response= 'utter_produto_exluido')
				dispatcher.utter_message(text= 'Seu carrinho está vazio agora.')
				return [SlotSet("inf_ret", False)]
			
			d= criar_dic(car)  # CRIA UM DICIONÁRIO DO CARRINHO
			carrinho = descreveCarrinho(d)
			dispatcher.utter_message(text= 'O seu carrinho possui agora')
			dispatcher.utter_message(text= carrinho)
			dispatcher.utter_message(text= 'Quantidade total de ítens: '+ str(qdtCar))
			dispatcher.utter_message(text= 'Valor total: '+ valorR)
			dispatcher.utter_message(response= 'utter_produto_exluido')
			return [SlotSet("inf_ret", False)]
		else:
			dispatcher.utter_message(text= 'Desculpe-me, mas ocorreu alguma falha na conexão do sistema e eu não consegui acessar o carrinho.')
			dispatcher.utter_message(text= 'Então, não foi possível retirar do carrinho.')
			return [SlotSet("inf_ret", False)]
			 

class ActionFechar(Action):
	'''Ação de fechar o pedido de compra'''
	def name(self) -> Text:
		return "action_fechar"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		car = tracker.get_slot('carrinho')
		d= {}
		if not car:
			dispatcher.utter_message(text= 'Desculpe-me, mas seu carrinho está vazio agora. Ou, então, eu já não tenho mais acesso a ele.')
			return []
		
		dispatcher.utter_message(text= 'Ok, estou gerando um link para você acessar o site Multitrem e finalizar sua compra.')
		#chamada de API
		d = criar_dic(car)  # CRIA UM DICIONÁRIO DO CARRINHO, PARA ADICIONAR OS PRODUTOS AO GRAFO DE CONHECIMENTO
		g.inserirNoGrafo(d)  # ADICIONA CARRINHO DE COMPRAS AO GRAFO DE CONHECIMENTO
		
		dispatcher.utter_message(text= 'Esta é uma solução provisória de ter que clicar em dois links!')
		dispatcher.utter_message(text= 'Para completar sua compra, por favor, clique em sequência, nos dois links abaixo:')
		
		dispatcher.utter_message(text= 'Primeiro clique neste link: '+
		'Https://shopizer.multitrem.com/shop/cart/displayMiniCartByCode?shoppingCartCode='+car)
		dispatcher.utter_message(text= 'Pode fechar esta página que abre ao clicar neste primeiro link.')
		dispatcher.utter_message(text= 'Por último, clique neste link: '+
		'Https://shopizer.multitrem.com/shop/cart/shoppingCart.html')
		dispatcher.utter_message(text= 'Neste último link já é a página do seu carrinho no site.')
		dispatcher.utter_message(response= 'utter_fecha')

		return [SlotSet("carrinho", None)]


class ActionPromocao(Action):
	'''Ação de consultar promoções'''
	def name(self) -> Text:
		return "action_promocao"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		#chamada de API
		
		# senão tem promoção:
		dispatcher.utter_message(response= 'utter_sem_promocao')
		
		return []
		

class ActionCaracteristica(Action):
	'''Ação de consultar caracteristica de produto'''
	def name(self) -> Text:
		return "action_caracteristicas"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		produto = tracker.get_slot('produto')
		produto_encontrado = tracker.get_slot('produto_encontrado')

		if produto_encontrado:
			if not produto:
				produto = produto_encontrado
		if not produto:
			dispatcher.utter_message(text= 'Por favor, me informe qual produto.')
			return [SlotSet("inf_prod", True)]  # Flag para quando informar o produto, voltar aqui nas caracteristicas
		else:
			endpoint = 'Https://shopizer.multitrem.com/api/v1/search/'
			param = { "count": 1,  "query": produto,  "start": 0}
			r = requests.post(endpoint, json= param)
			if (r.status_code == 200):  #200 indica que achou produto
				if r.json()['products']:
					pid = r.json()['products'][0]['id']
					pqtd = r.json()['products'][0]['quantity']
					produto_encontrado = r.json()['products'][0]['description']['name']
					preco = r.json()['products'][0]['price']	
					precoR = locale.currency(preco, grouping=True, symbol='R$')
					caracteristicas = r.json()['products'][0]['description']['description']
					dispatcher.utter_message(text= 'Ok! Eu encontrei estas informações sobre '+ str(produto_encontrado) +' no sistema' )
					dispatcher.utter_message(text= 'O preço de cada é '+ precoR)
					dispatcher.utter_message(text= 'A quantidade em estoque é '+ str(pqtd))
					if caracteristicas:
						s = caracteristicas.replace('<div>', '  \n')
						s = s.replace('</div>', ' ')
						s = s.replace('<p>', '  \n')
						s = s.replace('</p>', ' ')
						dispatcher.utter_message(text= s)
					else:
						dispatcher.utter_message(text= 'Por enquanto, este produto não tem mais detalhetes cadastrados no sistema.')
					return [SlotSet("inf_prod", False)]	 # desatva a Flag de quando informar o produto, voltar aqui nas caracteristicas	
				else:
					dispatcher.utter_message(text= 'Me desculpe, mas não encontrei informações sobre '+ str(produto) +' no sistema.')
					return [SlotSet("inf_prod", False)]  # desatva a Flag de quando informar o produto, voltar aqui nas caracteristicas	
			else:
				dispatcher.utter_message(text= 'Me desculpe, mas não consegui encontrar informações sobre '+ str(produto) +' no sistema.' )
				return [SlotSet("inf_prod", False)]  # desatva a Flag de quando informar o produto, voltar aqui nas caracteristicas	


				
class ActionEnviarReclamacao(Action):
	'''Ação de enviar reclamação'''
	
	def name(self) -> Text:
		return "action_enviar_reclamacao"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		nome = tracker.get_slot('nome')
		texto_recl = tracker.get_slot('texto_recl')
		#texto_recl = tracker.latest_message['text']
		
		dispatcher.utter_message(text= 'Ok! Estou registrando sua reclamação.')
			
		
		#chamada de API
		
		
		return [SlotSet("texto_recl", None)]


class ActionSaberCores(Action):
	'''Ação de consultar cores de um produto'''
	def name(self) -> Text:
		return "action_saber_cores"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		produto = tracker.get_slot('produto')

		if not produto:
			dispatcher.utter_message(text= 'Por favor, me informe qual produto.')	
			return []
		else:
			endpoint = 'Https://shopizer.multitrem.com/api/v1/search/'
			param = { "count": 1,  "query": produto,  "start": 0}
			r = requests.post(endpoint, json= param)
			if (r.status_code == 200):  #200 indica que achou produto
				if r.json()['products']:
					pid = r.json()['products'][0]['id']
					produto_encontrado = r.json()['products'][0]['description']['name']
					cores = coresDisponiveis(pid)
					if cores:
						dispatcher.utter_message(text= 'Temos agora ' + dizerCores(cores)+ '  \nQual cor você quer?')
					else:
						dispatcher.utter_message(text= 'Infelizmente não econtrei opções de cores para este produto.')
					
					return [SlotSet("produto", produto_encontrado)]

			dispatcher.utter_message(text= 'Me desculpe, mas não consegui encontrar informações sobre '+ str(produto) +' no sistema.' )
			return []


class ActionRisos(Action):
	'''Ação de riso do bot'''
	def name(self) -> Text:
		return "action_rir"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		msg = tracker.latest_message['text']
		if msg:
			msg = msg.lower()
			if 'kk' in msg:
				dispatcher.utter_message(text= 'Kkkkkk')
			if 'rs' in msg:
				dispatcher.utter_message(text= 'Rsrsrs')
			if 'heh' in msg:
				dispatcher.utter_message(text= 'Hehehe')
			if 'hah' in msg:
				dispatcher.utter_message(text= 'Hahah')
		return []



class ActionLimparSlots(Action):
	'''Ação de limpar slots do bot'''
	def name(self) -> Text:
		return "action_limpar_slots"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
			 
		pid = tracker.get_slot('pid')
		produto = tracker.get_slot('produto')
		lista_de_produtos= tracker.get_slot('lista_de_produtos')
		produto_encontrado= tracker.get_slot('produto_encontrado')
		pqtd= tracker.get_slot('pqtd')
		preco= tracker.get_slot('preco')
		precoR = tracker.get_slot('precoR')
		produto_oferecido = tracker.get_slot('produto_oferecido')
		nome = tracker.get_slot('nome')
		texto_recl = tracker.get_slot('texto_recl')
		qtd = tracker.get_slot('qtd')
		cor = tracker.get_slot('cor')
		corId = tracker.get_slot('corId')
		carrinho = tracker.get_slot('carrinho')
		inf_prod = tracker.get_slot('piinf_prodd')
		inf_ret = tracker.get_slot('inf_ret')
		
		slots = ['\npid: ',pid, '\nproduto: ', produto, '\nlista_de_produtos: ', lista_de_produtos,
				'\nproduto_encontrado:', produto_encontrado, '\npqtd: ', pqtd, '\n: preco', preco, '\nprecoR: ', precoR,
				'\nproduto_oferecido: ', produto_oferecido, '\nnome: ', nome, '\ntexto_recl: ', texto_recl, '\nqtd: ', qtd,
				'\ncor: ', cor, '\ncorId: ', corId, '\ncarrinho: ', carrinho, '\ninf_prod: ', inf_prod, '\ninf_ret: ', inf_ret]
		for i in slots:
			print(i)
		print('slots limpos com sucesso!')
		slots_to_reset = ['pid', 'produto','lista_de_produtos', 'produto_encontrado', 'pqtd', 'preco', 'precoR', 'produto_oferecido', 'nome', 'texto_recl', 'qtd', 'cor', 'corId', 'carrinho', 'inf_prod', 'inf_ret']
		return [SlotSet(slot, None) for slot in slots_to_reset]

class ActionMostrarSlots(Action):
	'''Ação de limpar slots do bot'''
	def name(self) -> Text:
		return "action_mostrar_slots"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		pid = tracker.get_slot('pid')
		produto = tracker.get_slot('produto')
		lista_de_produtos= tracker.get_slot('lista_de_produtos')
		produto_encontrado= tracker.get_slot('produto_encontrado')
		pqtd= tracker.get_slot('pqtd')
		preco= tracker.get_slot('preco')
		precoR = tracker.get_slot('precoR')
		produto_oferecido = tracker.get_slot('produto_oferecido')
		nome = tracker.get_slot('nome')
		texto_recl = tracker.get_slot('texto_recl')
		qtd = tracker.get_slot('qtd')
		cor = tracker.get_slot('cor')
		corId = tracker.get_slot('corId')
		carrinho = tracker.get_slot('carrinho')
		inf_prod = tracker.get_slot('piinf_prodd')
		inf_ret = tracker.get_slot('inf_ret')
		print('\n\nExibindo Slots do bot:')
		slots = ['\npid: ',pid, '\nproduto: ', produto, '\nlista_de_produtos: ', lista_de_produtos,
				'\nproduto_encontrado:', produto_encontrado, '\npqtd: ', pqtd, '\npreco: ', preco, '\nprecoR: ', precoR,
				'\nproduto_oferecido: ', produto_oferecido, '\nnome: ', nome, '\ntexto_recl: ', texto_recl, '\nqtd: ', qtd,
				'\ncor: ', cor, '\ncorId: ', corId, '\ncarrinho: ', carrinho, '\ninf_prod: ', inf_prod, '\ninf_ret: ', inf_ret]
		for i in slots:
			print(i)
		return []

class ActionLog(Action):
	'''Ação de registrar o log da conversa'''
	def name(self) -> Text:
		return "action_log"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
		idAtual = tracker.sender_id
		origem = str(tracker.get_latest_input_channel())
		if origem == 'socketio':
			origem = 'Webchat'
		if idAtual in ['1466565959'] or origem == 'Webchat':
			print('Log realizado: ', idAtual, origem, str(datetime.now()))
			dispatcher.utter_message(text= 'Log10:')			
			with open("log.lg", "a",  encoding='UTF-8') as f:  # outro encoding: cp1252
				m = mensagens(idAtual)
				if m:
					f.write('\n\n'+str(datetime.now())+' - '+origem+': '+idAtual+'\n\n')
					for i in m:
						f.write(i+'\n')
						dispatcher.utter_message(text= i)
						
			f.closed
			dispatcher.utter_message(text= 'fim_do_log10')
		else:
			print('Tentativa de Log: ', idAtual, origem, str(datetime.now()))
			dispatcher.utter_message(text= 'Obrigado por sua colaboração!  \nMas esta é uma função restrita à desenvolvedores  \nNão é necessário você usá-la.')
		return []

class ActionlistarTodosProdutos(Action):
	'''Ação de listar os produtos disponíveis'''
	def name(self) -> Text:
		return "action_listar_produtos"

	def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
			
			dispatcher.utter_message(response= 'utter_por_favor_aguarde_consulta')
			r = listarTodosProdutos()
			if r:
				dispatcher.utter_message(text= 'Prontinho! Estou te enviando uma lista de produtos')
				dispatcher.utter_message(text= r)
			else:
				dispatcher.utter_message(text= 'Ixi! Aconteceu algum problema e eu não consegui achar os produtos do sistema.')

			return []


