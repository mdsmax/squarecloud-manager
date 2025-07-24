O projeto foi desenvolvido para a competição oficial da [Square Cloud](https://squarecloud.app/).

---

## Funcionalidades e comandos
- `/painel` > Painel disponível para todos os usuários, permitindo a compra de serviços facilitada e gerenciamento das suas aplicações
- `/config` > Painel de configuração para o dono do Bot, permitindo a configuração e gerenciação de planos, usuários e aplicações.
- `/deletar` > Comando disponível para apenas o dono do Bot, apaga uma aplicação da SquareCloud e do banco de dados.
- `/deploy` > Comando disponível para apenas o dono do Bot, 'presenteia' um membro com um plano e serviço selecionado
- `/status` > Comandos disponível para apenas o dono do Bot, permite gerenciar facilmente todas as aplicações

---

## Informações das tecnologias usadas

- [Python](https://www.python.org/)
- [disnake](https://github.com/DisnakeDev/disnake)
- [squarecloud-api](https://pypi.org/project/squarecloud-api/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [mercado-pago-sdk](https://www.mercadopago.com.br/developers/pt/docs/sdks-library/landing)

---

## Instalação do projeto

```bash
git clone https://github.com/mdsmax/squarecloud-manager.git
cd squarecloud-manager
pip install -r requirements.txt
python main.py
```

Crie um arquivo `.env` com as variáveis:
```env
DISCORD_BOT_TOKEN=
SQUARECLOUD_TOKEN=
MERCADOPAGO_TOKEN=
OWNER_ID=
```

---

## Screenshots

![Painel de controle](https://cdn.discordapp.com/attachments/1398062739074846851/1398062746918064169/image.png?ex=6883fee5&is=6882ad65&hm=c09ad29d4f42932cb0c18be1455dce341896f57ab84530093215377b6f34397c&)

![Comprar serviço](https://cdn.discordapp.com/attachments/1398062739074846851/1398062792371863722/image.png?ex=6883fef0&is=6882ad70&hm=ff0080d50aa9b9dd4118b55d83a542163a959461f5fb3894a699d5f8e9594cc8&)

![Carrinho](https://cdn.discordapp.com/attachments/1398062739074846851/1398062846818123868/image.png?ex=6883fefd&is=6882ad7d&hm=f712805e576c66e46c6ff1899734f4783363b418bf2637eca65d75bce7e1b296&)

![Configurações](https://cdn.discordapp.com/attachments/1398062739074846851/1398062906863517868/image.png?ex=6883ff0b&is=6882ad8b&hm=047be9f8ea18f3209fdb540b00da67973c8177a325b3e7b926d6c47dca3ee48c&)

![Configurar serviço](https://cdn.discordapp.com/attachments/1398062739074846851/1398063296183144629/image.png?ex=6883ff68&is=6882ade8&hm=be50c60cf97a841247963db19bc8e61e0ee2ff031d872f1dc89e953046f24c81&)