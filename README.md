# chatBot_Vendedor_Virtual
ChatBot de um vendedor virtual com Processamento de Linguagem Natural, Machine Learning e Grafos de Connhecimento desenvolvido no meu Trabalho de Conclusão de Curso, disponibilizado neste link: https://drive.google.com/file/d/1oxfse_Iw41N6fTdJWWjJOZCWw44x5T66/view?usp=sharing

Além de vender, este chatbot também é capaz de aprender a oferecer outros produtos que costumam ser comprados juntos e a identificar tipos de produtos graças aos seus modelos de Grafos de Conhecimento.


O chatbot acessa a API Shopizer padrão REST/HTTPS para consultar produtos em um site e realizar vendas. 

Este chatbot foi desenvolvido com o framework Rasa Open Source versão 2.5 e pode não ser compatível com versões mais recentes.
Para mais informações sobre como usar e instalar o Rasa 2.5 acesse o site oficial:
https://rasa.com/docs/rasa/2.x/installation

Os requisitos a serem instalados estão disponíveis no arquivo requirements.txt

Recomendo o uso de um ambiente virtual no Anaconda Prompt (Anaconda 3).

Antes de executar será necessário realizar o treinamento do modelo de IA do Rasa através do comando no Anaconda Prompt: rasa train

Também é necessário configurar o arquivo credentials.yml para que o chatbot possa se comunicar com aplicativos de mensagens como, por exemplo, o Telegram. Um código exemplo com este chatbot sendo acessado através do Widget Webchat está disponível no arquivo index.html. Lembrando que o Telegram requer conexão segura https e a realização do cadastro do bot através do BotFather do Telegram. Já para o Whatsapp é necessário se conseguir um cadastro no Twilio, por exemplo.

É necessário configurar o arquivo endpoints.yml com as credenciais do banco de dados PostgreSQL para que os diálogos sejam registrados no banco de dados. Já no arquivo /actions/actions.py também é necessário as credenciais do PostgreSQL para que o chatbot possa extrair os diálogos para arquivos de log que podem ser usados para gerar novos dados de treinamento para o Machine Learning.

Pode ser necessário atualizar todos os endpoints de requisições REST, no arquivo /actions/actions.py, para endereços de algum site que faça uso do Shopizer, pois o site até então utilizado e que foi gentilmente cedido para testes pode não estar mais disponível.

Com tudo pronto, basta colocar o chatbot em execução através do comando no Anaconda Prompt:
rasa run --cors "*" --enable-api

Caso não possua um servidor com IP próprio é possivel, por exemplo usar o Ngrok para testar o chatbot: https://ngrok.com/  Ngrok é um programa de linha de comando que permite criar um túnel de conexão segura a partir do seu localhost e publicá-lo na internet.

Exemplo de atuação deste chatbot através do aplicativo Telegram:


![image](https://user-images.githubusercontent.com/95327592/144303779-3fef1a17-521c-4380-9688-a005dfc9f740.png)

![image](https://user-images.githubusercontent.com/95327592/144303855-b28f2ed9-fbb8-494f-aa25-b0ba196842eb.png)


Exemplo de atuação deste chatbot através do Webchat:

![image](https://user-images.githubusercontent.com/95327592/144308327-54304a11-761b-4c3a-bb49-6789a5082473.png)


