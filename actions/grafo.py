
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import pickle

# INICIALIZAÇÃO DO GRAFO COM VALORES PARA TESTE
#grafo = {'lapis': {'caneta': 5, 'borracha': 2},
#		 'caneta': {'lapis': 5},
#		 'borracha': {'lapis': 2} }

grafo = {}


def salvarGf():

	a_file = open("data.grf", "wb")
	pickle.dump(grafo, a_file)
	a_file.close()

def carregarGf():
	global grafo
	a_file = open("data.grf", "rb")
	grafo = pickle.load(a_file)

#########################################################################################

##### CARREGA O GRAFO A PARTIR DO ARQUIVO
carregarGf()

#########################################################################################

class ActionTeste(Action):
	'''acao para a execucao de testes'''
	def name(self) -> Text:
		return "action_teste"

	def run(self, dispatcher: CollectingDispatcher,
			 tracker: Tracker,
			 domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


		print(tracker.sender_id)
		print(tracker.get_latest_input_channel())
		dispatcher.utter_message(text= 'Executando teste: ok')
		dispatcher.utter_message(image= "https://i.imgur.com/nGF1K8f.jpg")
		
		#salvarGf()
		#carregarGf()
		
	
		
		dispatcher.utter_message(text= str(grafo))
		
		#dispatcher.utter_message(text= str(consultaGrafo('lapis')))
		#dispatcher.utter_message(text= str(consultaGrafo('borracha')))
		
		return []


def addG(produto, juntoCom, recur= False):
	'''ADICIONA AO GRAFO DOIS PRODUTOS VENDIDOS JUNTOS'''
	global grafo
	
	if juntoCom == produto:
		return
	if juntoCom in grafo:
		if produto in grafo[juntoCom]:
			grafo[juntoCom][produto]= grafo[juntoCom][produto] + 1
		else:
			grafo[juntoCom].update({produto: 1})
	else:
		grafo.update({juntoCom: {produto: 1}})
		
	if not recur:
		addG(juntoCom, produto, True)
	return 


def consultaGrafo(produto):
	'''RETORNA O PRODUTO QUE FOI VENDIDO JUNTO MAIS VEZES'''
	global grafo
	
	if produto in grafo:
		gf = {v: k for k, v in grafo[produto].items()}
		return str(gf[sorted(gf).pop()])
				
	return 


def inserirNoGrafo(produtos):
	'''INSERE UM CARRINHO DE COMPRAS AO GRAFO'''
	global grafo
	
	if len(produtos) > 1:
		l1 = list(produtos)
		while l1:
			p1 = l1.pop()
			l2 = list(l1)
			while l2:
				addG(p1, l2.pop())
	
	salvarGf()
	return




