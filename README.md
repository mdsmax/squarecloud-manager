Este projeto foi desenvolvido para a competição oficial da [Square Cloud](https://squarecloud.app/).

---

## Funcionalidades

- `/deploy` – Faz o deploy de uma aplicação configurada
- `/delete` – Exclui uma aplicação
- `/status` – Consulta o status de uma aplicação
- Deploy automático após pagamento via Mercado Pago (ou via modal simulando pagamento)
- Acesso controlado por cargo (opcional)
- Interface moderna usando Slash Commands, Botões e Modais

---

## Informações das tecnologias utilizadas

- [Python](https://www.python.org/)
- [disnake](https://github.com/DisnakeDev/disnake)
- [squarecloud-api](https://pypi.org/project/squarecloud-api/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [Mercado Pago SDK (opcional)](https://www.mercadopago.com.br/developers/pt/guides/payments/api/introduction)

---

## Instalação do projeto

```bash
git clone https://github.com/seu-usuario/square-manager-bot.git
cd square-manager-bot
pip install -r requirements.txt
python main.py
```

Crie um arquivo `.env` com  as variaveis:
```env
DISCORD_BOT_TOKEN=
SQUARECLOUD_TOKEN=
MERCADOPAGO_TOKEN=
OWNER_ID=
```