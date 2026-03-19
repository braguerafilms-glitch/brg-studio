# BRG Studio — Guia de Deploy

## Arquitetura

```
Cliente (browser)
    │
    ├── brg-studio-final.html  ──→  Vercel (frontend, grátis)
    │
    └── /gerar (fetch)         ──→  Railway (backend Python, grátis)
                                        │
                                        └── HuggingFace API (key do cliente)
```

---

## 1. Deploy do Backend (Railway)

### 1.1 Cria conta
Acessa **railway.app** e cria uma conta gratuita (pode usar GitHub).

### 1.2 Sobe o projeto
1. Clica em **New Project → Deploy from GitHub repo**
2. Cria um repositório no GitHub com estes arquivos:
   - `backend_prod.py`
   - `requirements.txt`
   - `Procfile`
   - `railway.json`
3. Conecta o repo no Railway

### 1.3 Variáveis de ambiente
No Railway → seu projeto → **Variables**, adiciona:
```
ALLOWED_ORIGINS=https://seu-app.vercel.app
PORT=5000
```

### 1.4 Pega a URL do backend
Depois do deploy, Railway gera uma URL tipo:
`https://brg-studio-api.up.railway.app`

---

## 2. Deploy do Frontend (Vercel)

### 2.1 Prepara o arquivo
No `brg-studio-final.html`, antes do `init()`, adiciona:
```js
window._BRG_API = 'https://brg-studio-api.up.railway.app';
```
(substitui pela URL real do Railway)

### 2.2 Sobe no Vercel
1. Acessa **vercel.com**, cria conta
2. Arrasta o `brg-studio-final.html` direto na dashboard
3. Vercel gera uma URL tipo `https://brg-studio.vercel.app`
4. Pode conectar domínio próprio (ex: `brgstudio.app`) por ~$12/ano

---

## 3. Venda (Lemon Squeezy)

### 3.1 Cria conta
Acessa **lemonsqueezy.com** e cria uma conta.

### 3.2 Cria o produto
- Tipo: **Digital product**
- Preço: o que quiser (ex: R$97 venda única)
- Entrega: URL do app (`https://brgstudio.app`)
- Ativa email automático com o link após compra

### 3.3 Integração simples (opcional)
Pode proteger o app com uma senha simples — quem compra recebe a senha por email. Sem necessidade de sistema de login complexo para começar.

---

## 4. Custos mensais

| Serviço | Custo |
|---------|-------|
| Vercel (frontend) | Grátis |
| Railway (backend) | Grátis até $5 de uso |
| Domínio próprio | ~R$60/ano |
| Lemon Squeezy | 5% por venda |
| **Total fixo** | **~R$5/mês** |

---

## 5. Próximos passos para produto completo

- [ ] Sistema de licença por email (Lemon Squeezy webhooks)
- [ ] Página de vendas
- [ ] Limite de gerações por usuário (se quiser freemium)
- [ ] Analytics (Plausible ou Umami — gratuitos)
- [ ] Suporte via email ou WhatsApp

---

## Estrutura final de arquivos

```
brg-studio/
├── brg-studio-final.html   # Frontend completo
├── backend_prod.py          # API Python
├── requirements.txt         # Dependências Python
├── Procfile                 # Config Railway/Render
├── railway.json             # Config Railway
└── DEPLOY.md                # Este guia
```
