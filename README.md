# chatBot_Vendedor_Virtual
ChatBot de um vendedor virtual com Processamento de Linguagem Natural, Machine Learning e Grafos de Connhecimento desenvolvido no meu Trabalho de Conclusão de Curso.
O chatbot acessa a API Shopizer padrão REST/HTTPS para consultar produtos em um site e realizar vendas. 

Este chatbot foi desenvolvido com o framework Rasa Open Source versão 2.5: https://rasa.com/docs/rasa/2.x/installation
Os requisitos a serem instalados estão disponíveis no arquivo requirements.txt

Recomendo o uso de um ambiente virtual no Anaconda Prompt (Anaconda 3).

Antes de executar será necessário realizar o treinamento do modelo de IA do Rasa através do comando: rasa train

Também é necessário configurar o arquivo credentials.yml para que o chatbot possa se comunicar com aplicativos de mensagens como o Telegram.

É necessário atualizar todos os endpoints de requisições REST, no arquivo /actions/actions.py, para endereços de algum site que faça uso do Shopizer, pois o site até então utilizado pode não estar mais disponível.

Exemplo de atuação deste chatbot através do aplicativo Telegram:


![image](https://user-images.githubusercontent.com/95327592/144303779-3fef1a17-521c-4380-9688-a005dfc9f740.png)

![image](https://user-images.githubusercontent.com/95327592/144303855-b28f2ed9-fbb8-494f-aa25-b0ba196842eb.png)

