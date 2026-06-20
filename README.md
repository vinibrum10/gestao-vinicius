# Gestão Vinicius

Aplicativo pessoal de planejamento semanal criado em Python, Streamlit e SQLite para organizar frentes de vida, tarefas, finanças, agenda manual e progresso.

## 1. Objetivo do projeto

O objetivo é ter uma central simples para planejar a semana com base em objetivos pessoais, escolher um foco principal, acompanhar tarefas por frente de vida, registrar finanças semanais e perceber frentes abandonadas antes que elas fiquem críticas.

## 2. Como instalar Python

1. Acesse https://www.python.org/downloads/windows/
2. Baixe a versão mais recente do Python 3.
3. Durante a instalação, marque a opção `Add Python to PATH`.
4. Confirme no terminal:

```powershell
py --version
```

## 3. Como criar ambiente virtual

Dentro da pasta do projeto, execute:

```powershell
py -m venv .venv
```

## 4. Como ativar ambiente virtual no Windows

```powershell
.venv\Scripts\activate
```

## 5. Como instalar dependências

```powershell
pip install -r requirements.txt
```

## 6. Como rodar o app

```powershell
streamlit run app.py
```

Também é possível executar com duplo clique no arquivo `run_app.bat`, depois que o ambiente virtual e as dependências estiverem prontos.

## 7. Como inicializar o banco

O banco `data/gestao_vinicius.db` é criado automaticamente quando o app inicia. As frentes iniciais também são carregadas automaticamente.

Para inicializar manualmente:

```powershell
py -c "from src.database import init_db; from src.seed import seed_initial_data; init_db(); seed_initial_data()"
```

## 8. Estrutura das pastas

```text
app.py
requirements.txt
README.md
.gitignore
run_app.bat
data/
  gestao_vinicius.db
src/
  database.py
  seed.py
  calculations.py
  services/
  pages/
tests/
  test_calculations.py
```

## 9. Como usar a primeira versão

1. Abra `Revisão de Domingo` e crie a semana.
2. Registre gasto, saldo, categoria mais pesada e observações financeiras.
3. Escolha o foco principal da semana.
4. Cadastre as tarefas principais.
5. Use `Tarefas Semanais` para atualizar status e concluir tarefas.
6. Use `Progresso` para registrar ações realizadas por frente.
7. Use `Agenda Manual` para cadastrar blocos de tempo.
8. Acompanhe tudo no `Painel da Semana`.

## 10. O que ficou fora do MVP

- Google Calendar.
- Google Cloud.
- Supabase.
- APIs externas.
- Login.
- Aplicativo mobile.
- Sincronização entre dispositivos.

## 11. Próximos passos futuros

- Melhorar edição completa de tarefas e blocos de agenda.
- Criar relatórios mensais mais detalhados.
- Adicionar exportação de dados.
- Criar backup automático do SQLite.
- Integrar calendário apenas quando o uso manual estiver validado.
- Criar autenticação apenas se houver necessidade real.

## 12. Como criar repositório GitHub futuramente

Quando quiser publicar no GitHub:

```powershell
git remote add origin URL_DO_REPOSITORIO
git branch -M main
git push -u origin main
```

Importante: nesta primeira versão o banco local `data/gestao_vinicius.db` faz parte do uso pessoal e não está ignorado. Se o repositório for público no futuro, remova o banco do Git, adicione `data/*.db` ao `.gitignore` e mantenha apenas um script de inicialização.
