# Otimous Bot

Bot Discord em Python focado em envio automático de avatars.

Requisitos
- Python 3.11+
- Dependências: `pip install -r requirements.txt` (ex.: discord.py, python-dotenv)

Execução local
1. Criar um arquivo `.env` com: `DISCORD_TOKEN=seu_token`
2. Instalar dependências: `pip install -r requirements.txt`
3. Rodar: `python main.py`

Procfile (deploy)
- Já incluído: `worker: python main.py` — usar como Worker em plataformas como Railway/Heroku.

Persistência (SQLite em volume persistente)
- O bot usa SQLite por padrão. O caminho do arquivo pode ser sobrescrito com a variável de ambiente `DB_PATH`.
  - Exemplo local (fallback): `data/avatar.db`
  - Em Railway com volume persistente (montado em `/data`): definir `DB_PATH=/data/avatar.db` nas env vars.
- Conexão SQLite usa URI com `cache=shared`, `timeout=30` e aplica PRAGMAs recomendadas (WAL, synchronous=NORMAL, foreign_keys=ON).
- Observação: SQLite é apropriado para uma única réplica (scale=1). Para múltiplas réplicas ou alta disponibilidade, usar um banco gerenciado (Postgres) e migrar os dados.

Como inspecionar o DB (ex.: no container Railway)
- Usando sqlite3 CLI: `sqlite3 /data/avatar.db "select * from avatar_schedule;"`

Deploy no Railway — passos rápidos
1. Criar projeto e configurar o repositório.
2. Adicionar Volume persistente e montar em `/data`.
3. No Environment variables do projeto, definir:
   - `DISCORD_TOKEN` = token do bot
   - `DB_PATH` = `/data/avatar.db` (se usar volume)
4. Confirmar Procfile: `worker: python main.py` e setar como Worker.
5. Escolher Scale=1 (apenas 1 instância escrevendo no arquivo SQLite).
6. Deploy e monitorar logs (Railway mostra stdout). Testar criando uma agenda via `/agendar_avatar`.

Logging
- Logs são escritos em `discord.log` e também enviados para stdout (útil em Railway).

Notas de desenvolvimento
- Cogs seguem o padrão `async def setup(bot): await bot.add_cog(...)` em `cogs/`.
- Persistência de agendamentos: tabela `avatar_schedule(guild_id, member_id, channel_id, interval_minutes, last_sent)`.

Contribuição
- Não há testes automatizados no momento. Adicione testes e CI conforme necessário.

