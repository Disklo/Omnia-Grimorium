# Omnia Grimorium

## Descrição
Este projeto é um bot para servidores do Discord, projetado para auxiliar o jogo de sessões de RPG que usam o sistema "Taverna do Fim Dos Tempos", incluindo criação e gestão de fichas de personagens, rolagem de dados, gerenciamento de XP, e muito mais.

## Características Principais
- **Gestão de Fichas:** Criação, edição, visualização e exclusão de fichas de personagens.
- **Rolagem de Dados:** Suporte para rolar diferentes tipos de dados com ou sem modificadores, como `r.rolar 2d6+3`.
- **Iniciativa:** Ordena automaticamente a iniciativa dos personagens fornecidos.
- **Atribuição de XP:** Adiciona ou remove XP e ajusta automaticamente o nível dos personagens.
- **Comandos Diversos:** Calculadora, moeda, informações sobre itens e mais.

## Comandos
### Fichas
- `r.criar`: Cria uma nova ficha de personagem.
- `r.ficha <nome>`: Exibe uma ficha de personagem.
- `r.editar <nome>`: Edita uma ficha existente.
- `r.excluir <nome>`: Exclui uma ficha.
- `r.thumbnail <nome> <url>`: Adiciona uma imagem à ficha.
- `r.removerthumbnail <nome>`: Remove a imagem da ficha.

### Jogabilidade
- `r.rolar <quantidade>d<tipo>+/-<modificador>`: Rola dados. Exemplo: `r.rolar 3d4+2`.
- `r.moeda [quantidade]`: Lança uma ou mais moedas.
- `r.iniciativa <nomes>`: Organiza a ordem de iniciativa dos personagens.
- `r.xp <nome> <quantidade>`: Atribui ou remove XP de uma ficha.

### Utilitários
- `r.calcular <expressão>`: Calcula uma expressão matemática.
- `r.ping`: Verifica a latência do bot.
- `r.info <termo>`: Busca informações sobre um item ou personagem.
- `r.help [comando]`: Exibe ajuda para um comando específico.

## Dependências
- `discord.py`: Biblioteca para integração com Discord.
- `fuzzywuzzy`: Utilizado para buscas aproximadas.

## Instalação
1. Clone este repositório:
   ```bash
   git clone <url-do-repositorio>
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd <diretorio-do-projeto>
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como Usar
1. Crie um bot no portal do Discord Developer e obtenha o token.
2. Configure o token no arquivo `bot.py`.
3. Execute o bot:
   ```bash
   python bot.py
   ```
4. Adicione o bot ao seu servidor do Discord.

## Créditos
O bot é baseado no sistema de RPG "Taverna do Fim dos Tempos - Sistema v1.6", desenvolvido por Lucas Nascimento, com permissão do autor para propósitos não comerciais e educativos.

## Licença
Este projeto está licenciado sob a Licença MIT.

