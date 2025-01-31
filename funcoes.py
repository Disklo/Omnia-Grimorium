import discord
from json import load
from fuzzywuzzy import process
from concurrent.futures import ThreadPoolExecutor, as_completed

def ver_ficha(arq, chave):
    with open(arq, encoding='utf-8') as a:
        fichas = load(a)
    if chave not in fichas:
        return None  # Retorna None se a chave não existir
    ficha = fichas[chave]
    # Criar o embed com os dados da ficha
    embed = discord.Embed(
        title=str(chave),
        description=(
            f"Classe: {ficha.get('classe', 'N/A')}  Grupo: {ficha.get('grupo', 'N/A')}\n"
            f"Nível: {ficha.get('nível', 'N/A')}  XP: {ficha.get('xp', 'N/A')}\n"
            f"Vitalidade: {ficha.get('vitalidade', 'N/A')}  Energia: {ficha.get('energia', 'N/A')}\n"
            f"Raça: {ficha.get('raça', 'N/A')}\n\n"
            f"Agilidade: {ficha.get('agilidade', 'N/A')}   Habilidade: {ficha.get('habilidade', 'N/A')}\n"
            f"Força: {ficha.get('força', 'N/A')}        Sabedoria: {ficha.get('sabedoria', 'N/A')}\n"
            f"Percepção: {ficha.get('percepção', 'N/A')}   Sorte: {ficha.get('sorte', 'N/A')}\n\n"
            f"Equipamentos:\n{', '.join(ficha.get('equipamentos', ['N/A']))}\n\n"
            f"Mochila:\n{', '.join(ficha.get('mochila', ['N/A']))}\n\n"
            f"Habilidades:\n{', '.join(ficha.get('habilidades', ['N/A']))}\n\n"
            f"Habilidade natural: {ficha.get('habilidade natural', 'N/A')}"
        ),
        color=discord.Colour.random()
    )
    # Adicionar thumbnail se existir
    if "thumbnail" in ficha:
        embed.set_thumbnail(url=ficha["thumbnail"])
    return embed

def checar_autor(autor, arq, chave):
    # Verificar se o usuário tem permissão de administrador
    if autor.guild_permissions.administrator:
        return True
    # Carregar o arquivo de fichas
    with open(arq, encoding='utf-8') as file:
        fichas = load(file)
    # Verificar se o ID do autor corresponde ao ID armazenado na ficha
    if chave in fichas:
        if "autor_id" in fichas[chave] and autor.id == fichas[chave]["autor_id"]:
            return True
    # Se nenhuma das condições for atendida, retornar False
    return False

def buscar(arq, inp):
    # Carregar o arquivo JSON
    with open(arq, encoding='utf-8') as file:
        dados = load(file)
    # Obter a lista de chaves (nomes dos itens/personagens)
    chaves = list(dados.keys())
    # Dividir a lista de chaves em 4 partes para busca paralela
    partes = [chaves[i::4] for i in range(4)]
    # Função para realizar a busca fuzzy em uma parte da lista
    def buscar_parte(parte):
        resultados = process.extract(inp, parte, limit=20)  # Busca fuzzy com limite de 20 resultados
        return [item[0] for item in resultados if item[1] > 86]  # Retorna apenas itens com score > 50
    # Realizar a busca em paralelo usando threads
    resultados_finais = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(buscar_parte, parte) for parte in partes]
        for future in as_completed(futures):
            resultados_finais.extend(future.result())
    # Remover duplicatas (caso ocorram)
    resultados_finais = list(set(resultados_finais))
    return resultados_finais

async def editar_campo(client, channel, autor, fichas, chave, campo):
    await channel.send(f"Digite o novo valor para {campo}:")
    msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
    fichas[chave][campo] = msg.content

async def editar_lista(client, channel, autor, fichas, chave, campo):
    lista_atual = fichas[chave][campo]
    await channel.send(f"Valores atuais de {campo}:\n{', '.join(lista_atual)}")
    await channel.send("[1] Adicionar novo item\n[2] Editar item existente\n[3] Excluir item")
    msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
    if msg.content == "1":
        await channel.send("Digite o novo item:")
        msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
        lista_atual.append(msg.content)
    elif msg.content == "2":
        await channel.send("Qual item você deseja editar? (Digite o número)")
        for i, item in enumerate(lista_atual):
            await channel.send(f"[{i+1}] {item}")
        msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
        index = int(msg.content) - 1
        await channel.send("Digite o novo valor:")
        msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
        lista_atual[index] = msg.content
    elif msg.content == "3":
        await channel.send("Qual item você deseja excluir? (Digite o número)")
        for i, item in enumerate(lista_atual):
            await channel.send(f"[{i+1}] {item}")
        msg = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == autor and m.channel == channel)
        index = int(msg.content) - 1
        lista_atual.pop(index)
    fichas[chave][campo] = lista_atual