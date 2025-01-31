import discord
from discord.ext import commands
from random import shuffle
from random import choice
from random import randint
import typing
from json import load
from json import dump
from funcoes import ver_ficha
from funcoes import checar_autor
from funcoes import buscar
from funcoes import editar_campo
from funcoes import editar_lista

intents = discord.Intents().all()
client = commands.Bot(command_prefix= 'r.', intents=intents)
bot = discord.Client()
client.remove_command("help")
intents.message_content = True

@client.event
async def on_ready():
    print ('O bot foi iniciado.')

@client.command(aliases=['coin'], invoke_without_command=True)
async def moeda(ctx, quant: typing.Optional[int] = 1):
    if quant <= 0:
        await ctx.send("Por favor, insira um número positivo de jogadas.")
        return
    resultados = [choice(['Cara', 'Coroa']) for _ in range(quant)]
    resultado_texto = ', '.join(resultados)
    await ctx.send(f"Resultado{'s' if quant > 1 else ''}: {resultado_texto}")

@client.command(aliases=["dado", "roll"])
async def rolar(ctx, string: str):
    try:
        # Separa a quantidade de dados e o tipo de dado
        quant_str, dado_str = string.split('d') if 'd' in string else ('1', string)
        quant = int(quant_str) if quant_str else 1
        # Verifica se há modificador
        if '+' in dado_str:
            dado, mod_str = dado_str.split('+')
            mod = int(mod_str)
        elif '-' in dado_str:
            dado, mod_str = dado_str.split('-')
            mod = -int(mod_str)
        else:
            dado = dado_str
            mod = 0
        dado = int(dado)
        # Rola os dados
        rolls = [randint(1, dado) for _ in range(quant)]
        total = sum(rolls)
        # Formata a mensagem de resultado
        resultado_texto = ', '.join(map(str, rolls))
        if mod > 0:
            await ctx.send(f"Resultado{'s' if quant > 1 else ''}: {resultado_texto}\n**Total: {total} + {mod} = {total + mod}**")
        else:
            await ctx.send(f"Resultado{'s' if quant > 1 else ''}: {resultado_texto}\n**Total: {total}**")
    except ValueError:
        await ctx.send("Formato inválido. Use algo como '2d6+3' ou 'd20'.")

@client.command(aliases=['calculate', 'calculo', 'cálculo', 'calculadora', 'calcular'], invoke_without_command=True)
async def calc(ctx, operation:str):
    await ctx.send(eval(operation))

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command()
async def ficha(ctx, *nomes):
    autor = ctx.message.author
    channel = ctx.channel
    chave = " ".join(nomes)
    personagens = buscar("fichas.json", chave)
    opcoes = []
    if len(personagens) > 1:
        opcoes = "\n".join([f"[{i + 1}] {nome}" for i, nome in enumerate(personagens)])
        await channel.send(f"Digite o número correspondente ao personagem que deseja visualizar:\n{opcoes}")
        def check(msg):
            return msg.author == autor and msg.channel == channel and msg.content.isdigit() and 1 <= int(msg.content) <= len(personagens)
        try:
            resposta = await client.wait_for('message', check=check, timeout=120.0)
            personagem_escolhido = personagens[int(resposta.content) - 1]
        except Exception:
            await channel.send("Tempo esgotado ou entrada inválida. Tente novamente.")
            return
    else:
        personagem_escolhido = personagens[0]
    # Buscar e mostrar a ficha
    ficha_embed = ver_ficha("fichas.json", personagem_escolhido)
    if ficha_embed:
        await channel.send(embed=ficha_embed)
    else:
        await channel.send("Erro ao carregar a ficha do personagem, ou personagem não encontrado.")

@client.command()
async def criar(ctx):
    autor = ctx.message.author
    channel = ctx.channel
    # Lista de campos necessários para a ficha
    campos = [
        ("nome", "Digite o nome"),
        ("classe", "Digite a classe"),
        ("grupo", "Digite o grupo"),
        ("nível", "Digite o nível (Até dois dígitos. Ex.: 10)"),
        ("xp", "Digite o XP (Até 105. Ex.: 25)"),
        ("vitalidade", "Digite a vitalidade"),
        ("energia", "Digite a energia"),
        ("raça", "Digite a raça"),
        ("agilidade", "Digite a agilidade"),
        ("habilidade", "Digite a habilidade"),
        ("força", "Digite a força"),
        ("sabedoria", "Digite a sabedoria"),
        ("percepção", "Digite a percepção"),
        ("sorte", "Digite a sorte"),
        ("equipamentos", "Digite os equipamentos (Ex.: Poção de vida, Espada)"),
        ("mochila", "Digite o conteúdo da mochila (Ex.: Poção de mana, Adaga)"),
        ("habilidades", "Digite as habilidades (Ex.: Criação, Afiamento)"),
        ("habilidade natural", "Digite a habilidade natural")
    ]
    fichas = {}
    try:
        with open("fichas.json", "r", encoding='utf-8') as file:
            fichas = load(file)
    except FileNotFoundError:
        pass
    # Função para solicitar entrada do usuário
    async def solicitar_entrada(prompt):
        await channel.send(prompt)
        while True:
            msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
            return msg.content
    # Coletar dados da ficha
    ficha = {}
    for campo, prompt in campos:
        if campo == "nível":
            while True:
                nivel = await solicitar_entrada(prompt)
                if nivel.isdigit() and 0 <= int(nivel) <= 20:
                    ficha[campo] = int(nivel)
                    break
                await channel.send("Valor inválido. Digite um novo valor.")
        elif campo == "xp":
            while True:
                xp = await solicitar_entrada(prompt)
                if xp.isdigit() and 0 <= int(xp) <= 105:
                    ficha[campo] = int(xp)
                    break
                await channel.send("Valor inválido. Digite um novo valor.")
        elif campo in ["equipamentos", "mochila", "habilidades"]:
            entrada = await solicitar_entrada(prompt)
            ficha[campo] = entrada.split(", ")
        else:
            ficha[campo] = await solicitar_entrada(prompt)
    # Verificar se o nome já existe
    if ficha["nome"] in fichas:
        await channel.send("Este personagem já existe.")
        return
    # Adicionar autor ID à ficha
    ficha["autor"] = autor
    # Salvar ficha no arquivo
    fichas[ficha["nome"]] = ficha
    with open("fichas.json", "w", encoding='utf-8') as file:
        dump(fichas, file, ensure_ascii=False, indent=4)
    # Exibir ficha criada
    abrirficha = ver_ficha("fichas.json", ficha["nome"])
    await channel.send(embed=abrirficha)

@client.command()
async def editar(ctx, *nomes):
    channel = ctx.channel
    autor = ctx.message.author
    chave = " ".join(nomes)
    # Buscar fichas
    busca = buscar("fichas.json", chave)
    if not busca:
        await channel.send("Personagem não encontrado.")
        return
    # Carregar o arquivo de fichas
    with open("fichas.json", "r", encoding="utf-8") as file:
        fichas = load(file)
    # Selecionar personagem para editar
    if len(busca) > 1:
        list2 = [f"[{i+1}] {busca[i]}\n" for i in range(len(busca))]
        await channel.send(f"Digite qual personagem você gostaria de editar:\n{''.join(list2)}")
        try:
            msg = await client.wait_for(
                'message',
                timeout=120.0,
                check=lambda m: m.author == autor and m.channel == channel
            )
            escolha = int(msg.content) - 1
            if escolha < 0 or escolha >= len(busca):
                await channel.send("Escolha inválida.")
                return
            chave = busca[escolha]
        except ValueError:
            await channel.send("Entrada inválida. Por favor, digite um número.")
            return
    else:
        chave = busca[0]
    # Verificar permissão
    if not checar_autor(autor, "fichas.json", chave):
        await channel.send("Você não possui permissão para editar esta ficha.")
        return
    # Exibir ficha atual
    abrirficha = ver_ficha("fichas.json", chave)
    await channel.send(embed=abrirficha)
    # Lista de campos editáveis
    campos = [
        ("1", "Nome", "nome"),
        ("2", "Classe", "classe"),
        ("3", "Grupo", "grupo"),
        ("4", "Nível", "nível"),
        ("5", "XP", "xp"),
        ("6", "Vitalidade", "vitalidade"),
        ("7", "Energia", "energia"),
        ("8", "Raça", "raça"),
        ("9", "Agilidade", "agilidade"),
        ("10", "Habilidade", "habilidade"),
        ("11", "Força", "força"),
        ("12", "Sabedoria", "sabedoria"),
        ("13", "Percepção", "percepção"),
        ("14", "Sorte", "sorte"),
        ("15", "Equipamentos", "equipamentos"),
        ("16", "Mochila", "mochila"),
        ("17", "Habilidades", "habilidades"),
        ("18", "Habilidade natural", "habilidade natural"),
        ("19", "Cancelar", None)
    ]
    # Solicitar campo para editar
    campo_opcoes = "\n".join([f"[{campo[0]}] {campo[1]}" for campo in campos])
    await channel.send(f"O que você deseja editar?\n{campo_opcoes}")
    msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
    escolha = msg.content
    # Processar escolha
    for campo in campos:
        if escolha == campo[0]:
            if campo[2] is None:  # Cancelar
                await channel.send("Edição cancelada.")
                return
            elif campo[2] == "nome":  # Editar nome (chave do dicionário)
                await channel.send("Digite o novo nome:")
                msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
                novo_nome = msg.content
                # Verificar se o novo nome já existe
                if novo_nome in fichas:
                    await channel.send("Já existe um personagem com esse nome.")
                    return
                # Criar nova entrada com o novo nome e copiar os dados
                fichas[novo_nome] = fichas[chave]
                # Remover a entrada antiga
                del fichas[chave]
                chave = novo_nome  # Atualizar a chave para o novo nome
            elif campo[2] in ["equipamentos", "mochila", "habilidades"]:
                await editar_lista(client, channel, autor, fichas, chave, campo[2])
            else:
                await editar_campo(client, channel, autor, fichas, chave, campo[2])
            break
    else:
        await channel.send("Opção inválida.")
    # Salvar alterações
    with open("fichas.json", "w", encoding="utf-8") as file:
        dump(fichas, file, ensure_ascii=False, indent=4)
    # Exibir ficha atualizada
    abrirficha = ver_ficha("fichas.json", chave)
    await channel.send(embed=abrirficha)

@client.command()
async def thumbnail(ctx, nome, url):
    autor = ctx.message.author
    channel = ctx.channel
    # Buscar fichas que correspondem ao nome
    busca = buscar("fichas.json", nome)
    if not busca:
        await channel.send("Personagem não encontrado.")
        return
    # Carregar o arquivo de fichas
    with open("fichas.json", "r", encoding="utf-8") as file:
        fichas = load(file)
    # Selecionar personagem para editar
    if len(busca) > 1:
        list2 = [f"[{i+1}] {busca[i]}\n" for i in range(len(busca))]
        await channel.send(f"Digite qual personagem você gostaria de editar:\n{''.join(list2)}")
        try:
            msg = await client.wait_for(
                'message',
                timeout=120.0,
                check=lambda m: m.author == autor and m.channel == channel
            )
            escolha = int(msg.content) - 1
            if escolha < 0 or escolha >= len(busca):
                await channel.send("Escolha inválida.")
                return
            chave = busca[escolha]
        except ValueError:
            await channel.send("Entrada inválida. Por favor, digite um número.")
            return
    else:
        chave = busca[0]
    # Verificar permissão
    if not checar_autor(autor, "fichas.json", chave):
        await channel.send("Você não possui permissão para editar esta ficha.")
        return
    # Adicionar ou substituir a thumbnail
    fichas[chave]["thumbnail"] = url
    await channel.send("Thumbnail atualizada com sucesso.")
    # Salvar alterações
    with open("fichas.json", "w", encoding="utf-8") as file:
        dump(fichas, file, ensure_ascii=False, indent=4)
    # Exibir ficha atualizada
    embed = ver_ficha("fichas.json", chave)
    await channel.send(embed=embed)

@client.command()
async def removerthumbnail(ctx, *nomes):
    autor = ctx.message.author
    channel = ctx.channel
    nome = " ".join(nomes)
    # Buscar fichas que correspondem ao nome
    busca = buscar("fichas.json", nome)
    if not busca:
        await channel.send("Personagem não encontrado.")
        return
    # Carregar o arquivo de fichas
    with open("fichas.json", "r", encoding="utf-8") as file:
        fichas = load(file)
    # Selecionar personagem para editar
    if len(busca) > 1:
        list2 = [f"[{i+1}] {busca[i]}\n" for i in range(len(busca))]
        await channel.send(f"Digite qual personagem você gostaria de editar:\n{''.join(list2)}")
        try:
            msg = await client.wait_for(
                'message',
                timeout=120.0,
                check=lambda m: m.author == autor and m.channel == channel
            )
            escolha = int(msg.content) - 1
            if escolha < 0 or escolha >= len(busca):
                await channel.send("Escolha inválida.")
                return
            chave = busca[escolha]
        except ValueError:
            await channel.send("Entrada inválida. Por favor, digite um número.")
            return
    else:
        chave = busca[0]
    # Verificar permissão
    if not checar_autor(autor, "fichas.json", chave):
        await channel.send("Você não possui permissão para editar esta ficha.")
        return
    # Remover a thumbnail
    if "thumbnail" in fichas[chave]:
        del fichas[chave]["thumbnail"]
        await channel.send("Thumbnail removida com sucesso.")
    else:
        await channel.send("Este personagem não possui thumbnail.")
    # Salvar alterações
    with open("fichas.json", "w", encoding="utf-8") as file:
        dump(fichas, file, ensure_ascii=False, indent=4)
    # Exibir ficha atualizada
    embed = ver_ficha("fichas.json", chave)
    await channel.send(embed=embed)

@client.command()
async def excluir(ctx, *nomes):
    autor = ctx.message.author
    channel = ctx.channel
    chave = " ".join(nomes)
    # Buscar fichas
    personagens = buscar("fichas.json", chave)
    if not personagens:
        await channel.send("Personagem não encontrado.")
        return
    # Carregar fichas
    with open("fichas.json", "r", encoding='utf-8') as file:
        fichas = load(file)
    # Selecionar personagem para excluir
    if len(personagens) > 1:
        list2 = [f"[{i+1}] {personagens[i]}\n" for i in range(len(personagens))]
        await channel.send(f"Digite qual personagem você gostaria de excluir:\n{''.join(list2)}")
        msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
        digito = int(msg.content) - 1
        chave = personagens[digito]
    else:
        chave = personagens[0]
    # Verificar permissão
    if not checar_autor(autor, "fichas.json", chave):
        await channel.send("Você não possui permissão para excluir este personagem.")
        return
    # Excluir personagem
    fichas.pop(chave, None)
    await channel.send(f"Personagem '{chave}' excluído com sucesso.")
    # Salvar alterações
    with open("fichas.json", "w", encoding='utf-8') as file:
        dump(fichas, file, ensure_ascii=False, indent=4)

@client.command()
async def info(ctx, *nomes):
    autor = ctx.message.author
    channel = ctx.channel
    chave = " ".join(nomes)
    # Carregar o arquivo dicionario.json
    try:
        with open("dicionario.json", "r", encoding="utf-8") as file:
            dicionario = load(file)
    except FileNotFoundError:
        print("Arquivo 'dicionario.json' não encontrado.")
        return
    # Buscar itens que correspondem à chave
    resultados = buscar("dicionario.json", chave)
    # Verificar se há resultados
    if not resultados:
        await channel.send("Item não encontrado.")
        return
    # Se houver mais de um resultado, pedir ao usuário para escolher
    if len(resultados) > 1:
        opcoes = [f"[{i+1}] {resultados[i]}\n" for i in range(len(resultados))]
        await channel.send(f"Digite qual item você gostaria de visualizar:\n{''.join(opcoes)}")
        try:
            msg = await client.wait_for(
                'message',
                timeout=120.0,
                check=lambda m: m.author == autor and m.channel == channel
            )
            escolha = int(msg.content) - 1
            if escolha < 0 or escolha >= len(resultados):
                await channel.send("Escolha inválida.")
                return
            item = resultados[escolha]
        except ValueError:
            await channel.send("Entrada inválida. Por favor, digite um número.")
            return
    else:
        item = resultados[0]
    # Verificar se o item existe no dicionário
    if item not in dicionario:
        await channel.send("Item não encontrado.")
        return
    # Criar o embed com as informações do item
    embed = discord.Embed(
        title=item,
        description=dicionario[item][0],
        color=discord.Colour.random()
    )
    # Adicionar thumbnail se existir
    if len(dicionario[item]) > 1:
        embed.set_thumbnail(url=dicionario[item][1])
    # Enviar o embed
    await channel.send(embed=embed)

@client.command()
async def xp(ctx, chave, quant):
    autor = ctx.message.author
    channel = ctx.channel
    # Buscar fichas que correspondem à chave
    busca = buscar("fichas.json", chave)
    if not busca:
        await channel.send("Personagem não encontrado.")
        return
    # Carregar o arquivo de fichas
    try:
        with open("fichas.json", "r", encoding="utf-8") as file:
            fichas = load(file)
    except FileNotFoundError:
        print("Arquivo 'fichas.json' não encontrado.")
        return
    # Selecionar personagem para atribuir XP
    if len(busca) > 1:
        list2 = [f"[{i+1}] {busca[i]}\n" for i in range(len(busca))]
        await channel.send(f"Digite qual personagem você gostaria de atribuir XP:\n{''.join(list2)}")
        try:
            msg = await client.wait_for(
                'message',
                timeout=120.0,
                check=lambda m: m.author == autor and m.channel == channel
            )
            escolha = int(msg.content) - 1
            if escolha < 0 or escolha >= len(busca):
                await channel.send("Escolha inválida.")
                return
            chave = busca[escolha]
        except ValueError:
            await channel.send("Entrada inválida. Por favor, digite um número.")
            return
    else:
        chave = busca[0]
    # Verificar permissão do usuário
    if not checar_autor(autor, "fichas.json", chave):
        await channel.send("Você não possui permissão para atribuir XP a este personagem.")
        return
    # Atribuir XP ao personagem
    try:
        quant = int(quant)
    except ValueError:
        await channel.send("Quantidade de XP inválida. Por favor, digite um número.")
        return
    # Atualizar XP e nível do personagem
    if chave in fichas:
        nivel = int(fichas[chave]["nível"])
        xp_atual = int(fichas[chave]["xp"])
        xp_max = nivel * 5
        novo_xp = xp_atual + quant
        # Ajustar nível com base no novo XP
        while novo_xp >= xp_max:
            novo_xp -= xp_max
            nivel += 1
            xp_max = nivel * 5
        while novo_xp < 0:
            nivel -= 1
            if nivel < 1:
                nivel = 1
                novo_xp = 0
                break
            xp_max = nivel * 5
            novo_xp += xp_max
        # Atualizar ficha com novo XP e nível
        fichas[chave]["nível"] = nivel
        fichas[chave]["xp"] = novo_xp
        # Salvar alterações no arquivo
        with open("fichas.json", "w", encoding="utf-8") as file:
            dump(fichas, file, ensure_ascii=False, indent=4)
        # Exibir ficha atualizada
        embed = ver_ficha("fichas.json", chave)
        await channel.send(embed=embed)
    else:
        await channel.send("Erro ao encontrar o personagem.")

@client.command()
async def iniciativa(ctx, *nomes):
    # Verificar se foram fornecidos nomes
    if not nomes:
        await ctx.send("Por favor, forneça os nomes dos personagens.")
        return
    # Converter a tupla de nomes em uma lista e remover vírgulas extras
    nomes_lista = [nome.strip() for nome in " ".join(nomes).split(",")]
    # Embaralhar a lista de nomes
    shuffle(nomes_lista)
    # Criar uma string com a ordem da iniciativa
    ordem_iniciativa = "\n".join(nomes_lista)
    # Criar um embed para exibir a ordem da iniciativa
    embed = discord.Embed(
        title="Ordem da Iniciativa",
        description=ordem_iniciativa,
        color=discord.Colour.random()
    )
    # Enviar o embed
    await ctx.send(embed=embed)

@client.command()
async def help(ctx, comando: typing.Optional[str] = None):
    # Dicionário de comandos e suas descrições
    comandos = {
        "criar": "Cria uma nova ficha de personagem.",
        "ficha": "Visualiza uma ficha de personagem existente. Exemplo: `r.ficha Berwin Earling`.",
        "editar": "Edita uma ficha de personagem existente. Exemplo: `r.editar Berwin Earling`.",
        "excluir": "Exclui uma ficha de personagem existente. Exemplo: `r.excluir Berwin Earling`.",
        "thumbnail": "Adiciona ou substitui a thumbnail (imagem) de uma ficha de personagem existente. Exemplo: `r.thumbnail Berwin Earling https://exemplo.com/imagem.png`.",
        "removerthumbnail": "Remove a thumbnail de uma ficha de personagem existente. Exemplo: `r.removerthumbnail Berwin Earling`.",
        "xp": "Atribui ou remove XP de uma ficha de personagem existente. Exemplo: `r.xp Berwin Earling 10`.",
        "rolar": "Rola dado(s). Exemplo: `r.rolar d20` ou `r.rolar 3d4+2`.",
        "moeda": "Joga moeda(s). Exemplo: `r.moeda` ou `r.moeda 3`.",
        "calcular": "Calcula a operação dada. Exemplo: `r.calcular (2+2)*7`.",
        "ping": "Mostra o tempo de resposta do bot.",
        "iniciativa": "Automaticamente rola a iniciativa dos personagens. Exemplo: `r.iniciativa Berwin, Donaghy, Grug, Asura`.",
        "info": "Busca informações sobre um item ou personagem. Exemplo: `r.info Espada`."
    }
    # Se nenhum comando específico for fornecido, exibir apenas a lista de comandos
    if not comando:
        embed = discord.Embed(
            title="Comandos Disponíveis",
            description="Use `r.help <comando>` para obter mais informações sobre um comando específico.",
            color=discord.Colour.random()
        )
        # Adicionar apenas os nomes dos comandos ao embed
        lista_comandos = ", ".join([f"`r.{cmd}`" for cmd in comandos.keys()])
        embed.add_field(name="Comandos", value=lista_comandos, inline=False)
        await ctx.send(embed=embed)
    else:
        # Verificar se o comando existe
        comando = comando.lower()
        if comando in comandos:
            embed = discord.Embed(
                title=f"Comando `r.{comando}`",
                description=comandos[comando],
                color=discord.Colour.random()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Comando `{comando}` não encontrado. Use `r.help` para ver a lista de comandos disponíveis.")

client.run('COLOQUE O TOKEN DE SEU BOT DO DISCORD AQUI')
