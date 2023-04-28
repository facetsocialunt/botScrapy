import discord
import os
from ScrapyOL import ScrapyOL
from ScrapyOL import ScrapyOLInicial
from ScrapyPPS import ScrapyPPS
from ScrapyPPS import ScrapyPPSInicial
from ScrapyProcesadores import ScrapyProcesadores
from ScrapyProcesadores import ScrapyProcesadoresInicial
from ScrapyTD import ScrapyTD
from ScrapyTD import ScrapyTDInicial
from ScrapyArquitectura import ScrapyArquitectura
from ScrapyArquitectura import ScrapyArquitecturaInicial
import json
from discord.ext import tasks
import urllib3

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

#################
# Variables globales de configuracion
#################
SECRET_TOKEN_BOT = config['DISCORD']['SECRET_TOKEN_BOT']
ID_CHANNEL_OFERTAS = config['DISCORD']['ID_CHANNEL_OFERTAS']
ID_CHANNEL_PASANTIAS = config['DISCORD']['ID_CHANNEL_PASANTIAS']
ID_CHANNEL_MICROPROCESADORES = config['DISCORD']['ID_CHANNEL_MICROPROCESADORES']
ID_CHANNEL_TRANSMISION_DE_DATOS = config['DISCORD']['ID_CHANNEL_TRANSMISION_DE_DATOS']
ID_CHANNEL_ARQUITECTURA = config['DISCORD']['ID_CHANNEL_ARQUITECTURA']
ID_CHANNEL_CMD = config['DISCORD']['ID_CHANNEL_CMD']

http = urllib3.PoolManager()
client = discord.Client()

#################
# Variables globales que almacenan informacion de las ultimas publicaciones
#################
global ultimaPPSId, ultimaPPSTitulo, ultimaPPSDes
global ultimaOLId, ultimaOLTitulo, ultimaOLDes
global ultimaNovedadProcesadores
global ultimaNovedadTD
global ultimaNovedadArquitectura

ultimaPPSId, ultimaPPSTitulo, ultimaPPSDes = "", "", ""
ultimaOLId, ultimaOLTitulo, ultimaOLDes = "", "", ""
ultimaNovedadProcesadores = ""
ultimaNovedadTD = ""
ultimaNovedadArquitectura = ""



#################
# Funcion "event", respuesta a la interaccion del usuario: "hello","latest"
#################
@client.event
async def on_message(message):
    if message.author == client.user:
        return
        # lower case message
    message_content = message.content.lower()

    # Para el msj: $hello
    if message.content.startswith(f'$hello'):
        await message.channel.send('Buenos dias, soy un Bot que te mantiene al tanto de las ultimas noticias!!')

    # Para el msj: $latest
    if f'$latest' in message_content:
        await message.channel.send("__**Ultima Pasatia y PPS:**__")
        await message.channel.send(ultimaPPSId + "\n" + ultimaPPSTitulo + "\n" + ultimaPPSDes)
        await message.channel.send("__**Ultima Oferta Laboral:**__")
        await message.channel.send(ultimaOLId + "\n" + ultimaOLTitulo + "\n" + ultimaOLDes)
        await message.channel.send("__**Ultima Novedad de Sist. con Microprocesadores:**__")
        await message.channel.send(ultimaNovedadProcesadores)
        await message.channel.send("__**Ultima Novedad de Transmisiones de Datos:**__")
        await message.channel.send(ultimaNovedadTD)
        await message.channel.send("__**Ultima Novedad de Arquitectura de Computadoras:**__")
        await message.channel.send(ultimaNovedadArquitectura)

    if f'$pps' in message_content:
        await message.channel.send("__**Ultima Pasatia y PPS:**__")
        await message.channel.send(ultimaPPSId + "\n" + ultimaPPSTitulo + "\n" + ultimaPPSDes)

    if f'$ol' in message_content:
        await message.channel.send("__**Ultima Oferta Laboral:**__")
        await message.channel.send(ultimaOLId + "\n" + ultimaOLTitulo + "\n" + ultimaOLDes)

    if f'$pro' in message_content:
        await message.channel.send("__**Ultima Novedad de Sist. con Microprocesadores:**__")
        await message.channel.send(ultimaNovedadProcesadores)

    if f'$td' in message_content:
        await message.channel.send("__**Ultima Novedad de Transmisiones de Datos:**__")
        await message.channel.send(ultimaNovedadTD)
    
    if f'$arq' in message_content:
        await message.channel.send("__**Ultima Novedad de Arquitectura de Computadoras:**__")
        await message.channel.send(ultimaNovedadArquitectura)


#################
# Funcion para revisar y publicar las ultimas Ofertas Laborales publicadas (cada 30 min)
#################
@tasks.loop(seconds=1800)
async def ofertasLaborales():
    # Canal de Ofertas Laborales
    global ultimoOLEstadoError
    channel = client.get_channel(int(ID_CHANNEL_OFERTAS))
    try:
        http.request('GET', 'https://www.facet.unt.edu.ar/sbe/ofertas-laborales/', retries=2)
    except:
        print(f'Problema de conexion con https://www.facet.unt.edu.ar/sbe/ofertas-laborales/')
        if ultimoOLEstadoError < 2:
            if ultimoOLEstadoError == 0:
                # Case: 0 (Primera vez sin conexion. Se espera a la siguiente vuelta)
                ultimoOLEstadoError += 1
            elif ultimoOLEstadoError == 1:
                # Case: 1 (Segunda vez sin conexion. Se envia mensaje)
                await channel.send(" ** Nuestro servicio de notificaciones no se encuentra disponible debido a problemas externos ** ❗ \n\n Por favor controla tus notificaiones manualmente en https://www.facet.unt.edu.ar/sbe/ofertas-laborales/")
                ultimoOLEstadoError += 1    
    else:
        ultimoOLEstadoError = 0
        print("hay conexion: variable puesta en 0")
    # Ejecuta Scrapy de Ofertas Laborales
        ScrapyOL()
        des = ""
        global ultimaOLId, ultimaOLTitulo, ultimaOLDes
        # Lee el archivo y publica publicaciones nuevas si es que hay
        ruta = 'data/ofertas.json'
        with open(ruta) as contenido:

            ofertaslaborales = json.load(contenido)

            for oferta in ofertaslaborales:
                des = ""
                of = oferta
                id = "".join(of["id"])
                titulo = "".join(of["titulo"])
                fecha = "".join(of["fecha"])
                link = "".join(of["link"])
                descripcion = of["descripcion"][0]

                for d in descripcion:
                    if ('\n\u2022' in d):
                        des = des + d.strip("\t")
                    elif ('\u2022' in d):
                        des = des + "\n" + d.strip("\t")
                    elif ('\u27a2' in d):
                        des = des + "\n" + d.strip("\t")
                    elif ('\n' in d):
                        # des = des + "\n" + d.strip("\t")
                        des = des + d.strip("\t")
                    elif (':' in d):
                        des = des + d.strip("\t") + "\n"
                    else:
                        des = des + d.strip("\t")

                msgOL = "__**Ofertas Laborales**__\n\n" + "**" + titulo + "**" + " \n" + fecha + " \n\n" + des + " \n\n" + "***Ver mas:  ***" + link + " \n\n" + "═════════════════"

                if (id == ultimaOLId):
                    if (titulo == ultimaOLTitulo):
                        if (des == ultimaOLDes):
                            ultimaOLId, ultimaOLTitulo, ultimaOLDes = ScrapyOLInicial()
                            break
                        else:
                            ultimaOLId, ultimaOLTitulo, ultimaOLDes = ScrapyOLInicial()
                            await channel.send(msgOL)
                            break
                    else:
                        ultimaOLId, ultimaOLTitulo, ultimaOLDes = ScrapyOLInicial()
                        await channel.send(msgOL)
                        break
                else:
                    await channel.send(msgOL)

# #################
# # Funcion para revisar y publicar las ultimas Pasantias publicadas (cada 30 min)
# #################
@tasks.loop(seconds=1800)
async def pasantias():
    # Canal de Pasantias
    channel = client.get_channel(int(ID_CHANNEL_PASANTIAS))
    global ultimoPPSEstadoError
    try:
        http.request('GET', 'https://www.facet.unt.edu.ar/sbe/pasantias-y-pps/', retries=2)
    except:
        print(f'Problema de conexion con https://www.facet.unt.edu.ar/sbe/pasantias-y-pps/')
        if ultimoPPSEstadoError < 2:
            if ultimoPPSEstadoError == 0:
                # Case: 0 (Primera vez sin conexion. Se espera a la siguiente vuelta)
                ultimoPPSEstadoError += 1
            elif ultimoPPSEstadoError == 1:
                # Case: 1 (Segunda vez sin conexion. Se envia mensaje)
                await channel.send(" ** Nuestro servicio de notificaciones no se encuentra disponible debido a problemas externos ** ❗ \n\n Por favor controla tus notificaiones manualmente en https://www.facet.unt.edu.ar/sbe/pasantias-y-pps/")
                ultimoPPSEstadoError += 1
    else:
        ultimoPPSEstadoError = 0
        # Ejecuta Scrapy de Pasantias
        ScrapyPPS()
        des = ""
        global ultimaPPSTitulo, ultimaPPSId, ultimaPPSDes

        # Lee el archivo y publica publicaciones nuevas si es que hay
        ruta = 'data/pasantias.json'
        with open(ruta) as contenido:

            pasantiasypps = json.load(contenido)

            for pasantia in pasantiasypps:
                des = ""
                pas = pasantia
                id = "".join(pas["id"])
                titulo = "".join(pas["titulo"])
                fecha = "".join(pas["fecha"])
                link = "".join(pas["link"])
                descripcion = pas["descripcion"][0]

                for d in descripcion:
                    if ('\n\u2022' in d):
                        des = des + d.strip("\t")
                    elif ('\u2022' in d):
                        des = des + "\n" + d.strip("\t")
                    elif ('\u27a2' in d):
                        des = des + "\n" + d.strip("\t")
                    elif ('\n' in d):
                        # des = des + "\n" + d.strip("\t")
                        des = des + d.strip("\t")
                    elif (':' in d):
                        des = des + d.strip("\t") + "\n"
                    else:
                        des = des + d.strip("\t")

                msgPPS = "__**Pasantias y PPS**__\n\n" + "**" + titulo + "**" + " \n" + fecha + " \n\n" + des + " \n\n" + "***Ver mas:  ***" + link + " \n\n" + "═════════════════"

                if (id == ultimaPPSId):
                    if (titulo == ultimaPPSTitulo):
                        if (des == ultimaPPSDes):
                            ultimaPPSId, ultimaPPSTitulo, ultimaPPSDes = ScrapyPPSInicial()
                            break
                        else:
                            ultimaPPSId, ultimaPPSTitulo, ultimaPPSDes = ScrapyPPSInicial()
                            await channel.send(msgPPS)
                            break
                    else:
                        ultimaPPSId, ultimaPPSTitulo, ultimaPPSDes = ScrapyPPSInicial()
                        await channel.send(msgPPS)
                        break
                else:
                    await channel.send(msgPPS)


# #################
# # Funcion para revisar y publicar las ultimas novedades publicadas de Microprocesadoes (cada 15 min)
# #################
@tasks.loop(seconds=900)
async def novedadesProcesarores():
    # Canal de la Microprocesadores
    channel = client.get_channel(int(ID_CHANNEL_MICROPROCESADORES))
    global ultimoProcesadoresEstadoError
    try:
        http.request('GET', 'https://microprocesadores.unt.edu.ar/procesadores/', retries=2)
    except:
        print(f'Problema de conexion con https://microprocesadores.unt.edu.ar/procesadores/')
        if ultimoProcesadoresEstadoError < 2:
            if ultimoProcesadoresEstadoError == 0:
                # Case: 0 (Primera vez sin conexion. Se espera a la siguiente vuelta)
                ultimoProcesadoresEstadoError += 1
            elif ultimoProcesadoresEstadoError == 1:
                # Case: 1 (Segunda vez sin conexion. Se envia mensaje)
                await channel.send(" ** Nuestro servicio de notificaciones no se encuentra disponible debido a problemas externos ** ❗ \n\n Por favor controla tus notificaiones manualmente en https://microprocesadores.unt.edu.ar/procesadores/")
                ultimoProcesadoresEstadoError += 1
    else:
        ultimoProcesadoresEstadoError = 0
        # Ejecuta Scrapy de Procesadores
        ScrapyProcesadores()
        global ultimaNovedadProcesadores

        # Lee el archivo y publica publicaciones nuevas si es que hay
        ruta = 'data/novedadesProcesadores.json'
        with open(ruta) as contenido:

            novedades = json.load(contenido)

            for novedad in novedades:
                nov = novedad
                fecha = "".join(nov["fecha"])
                descripcion = "".join(nov["descripcion"][0])

                msgProcesadores = "📢 __**Nueva publicación**__\n\n" + descripcion + "**\n\nFecha: **" + fecha + "\n\n\n🔗 __**Links de Secciones:**__\n\n" + "***-📰 Cartelera de Novedades:***\n" + "https://microprocesadores.unt.edu.ar/procesadores/" + "\n***-📚 Diapositivas:***\n" + "https://microprocesadores.unt.edu.ar/procesadores/downloads/type/0/" + "\n***-📝 Prácticos/Laboratorios:***\n" + "https://microprocesadores.unt.edu.ar/procesadores/downloads/assignments/" + " \n\n" + "═════════════════"

                if (descripcion != ultimaNovedadProcesadores):
                    await channel.send(msgProcesadores)
                else:
                    nov = novedades[0]
                    descripcion = "".join(nov["descripcion"][0])
                    ultimaNovedadProcesadores = descripcion
                    break


# #################
# # Funcion para revisar y publicar las ultimas novedades publicadas de Trans. de Datos (cada 15 min)
# #################
@tasks.loop(seconds=900)
async def novedadesTD():
    # Canal de Transmision de Datos
    channel = client.get_channel(int(ID_CHANNEL_TRANSMISION_DE_DATOS))
    global ultimoTDEstadoError
    try:
        http.request('GET', 'https://microprocesadores.unt.edu.ar/transmision/', retries=2)
    except:
        print(f'Problema de conexion con https://microprocesadores.unt.edu.ar/transmision/')
        if ultimoTDEstadoError < 2:
            if ultimoTDEstadoError == 0:
                # Case: 0 (Primera vez sin conexion. Se espera a la siguiente vuelta)
                ultimoTDEstadoError += 1
            elif ultimoTDEstadoError == 1:
                # Case: 1 (Segunda vez sin conexion. Se envia mensaje)
                await channel.send(" ** Nuestro servicio de notificaciones no se encuentra disponible debido a problemas externos ** ❗ \n\n Por favor controla tus notificaiones manualmente en https://microprocesadores.unt.edu.ar/transmision/")
                ultimoTDEstadoError += 1
    else:
        ultimoTDEstadoError = 0
    
        # Ejecuta Scrapy de Trans. de Datos
        ScrapyTD()
        global ultimaNovedadTD

        # Lee el archivo y publicar publicaciones nuevas si es que hay
        ruta = 'data/novedadesTD.json'
        with open(ruta) as contenido:

            novedades = json.load(contenido)

            for novedad in novedades:
                nov = novedad
                fecha = "".join(nov["fecha"])
                descripcion = "".join(nov["descripcion"][0])

                msgTD = "📢 __**Nueva publicación**__\n\n" + descripcion + "**\n\nFecha: **" + fecha + "\n\n\n🔗 __**Links de Secciones:**__\n\n" + "***-📰 Cartelera de Novedades:***\n" + "https://microprocesadores.unt.edu.ar/transmision/" + "\n***-📚 Diapositivas:***\n" + "https://microprocesadores.unt.edu.ar/transmision/downloads/type/0/" + "\n***-📝 Prácticos/Laboratorios:***\n" + "https://microprocesadores.unt.edu.ar/transmision/downloads/assignments/" + " \n\n" + "═════════════════"

                if (descripcion != ultimaNovedadTD):
                    await channel.send(msgTD)
                else:
                    nov = novedades[0]
                    descripcion = "".join(nov["descripcion"][0])
                    ultimaNovedadTD = descripcion
                    break


# #################
# # Funcion para revisar y publicar las ultimas novedades publicadas de Arquitectua de Computadoras (cada 15 min)
# #################
@tasks.loop(seconds=900)
async def novedadesArquitectura():
    # Canal de Transmision de Datos
    channel = client.get_channel(int(ID_CHANNEL_ARQUITECTURA))
    global ultimoArquitecturaEstadoError
    try:
        http.request('GET', 'https://microprocesadores.unt.edu.ar/arqcom/', retries=2)
    except:
        print(f'Problema de conexion con https://microprocesadores.unt.edu.ar/arqcom/')
        if ultimoArquitecturaEstadoError < 2:
            if ultimoArquitecturaEstadoError == 0:
                # Case: 0 (Primera vez sin conexion. Se espera a la siguiente vuelta)
                ultimoArquitecturaEstadoError += 1
            elif ultimoArquitecturaEstadoError == 1:
                # Case: 1 (Segunda vez sin conexion. Se envia mensaje)
                await channel.send(" ** Nuestro servicio de notificaciones no se encuentra disponible debido a problemas externos ** ❗ \n\n Por favor controla tus notificaiones manualmente en https://microprocesadores.unt.edu.ar/arqcom/")
                ultimoArquitecturaEstadoError += 1
    else:
        ultimoArquitecturaEstadoError = 0
    
        # Ejecuta Scrapy de Trans. de Datos
        ScrapyArquitectura()
        global ultimaNovedadArquitectura

        # Lee el archivo y publicar publicaciones nuevas si es que hay
        ruta = 'data/novedadesArquitectura.json'
        with open(ruta) as contenido:

            novedades = json.load(contenido)

            for novedad in novedades:
                nov = novedad
                fecha = "".join(nov["fecha"])
                descripcion = "".join(nov["descripcion"][0])

                msgArquitectura = "📢 __**Nueva publicación**__\n\n" + descripcion + "**\n\nFecha: **" + fecha + "\n\n\n🔗 __**Links de Secciones:**__\n\n" + "***-📰 Cartelera de Novedades:***\n" + "https://microprocesadores.unt.edu.ar/arqcom/" + "\n***-📚 Diapositivas:***\n" + "https://microprocesadores.unt.edu.ar/arqcom/downloads/type/0/" + "\n***-📝 Prácticos/Laboratorios:***\n" + "https://microprocesadores.unt.edu.ar/arqcom/downloads/assignments/" + " \n\n" + "═════════════════"

                if (descripcion != ultimaNovedadArquitectura):
                    await channel.send(msgArquitectura)
                else:
                    nov = novedades[0]
                    descripcion = "".join(nov["descripcion"][0])
                    ultimaNovedadArquitectura = descripcion
                    break


#################
# Funcion inicial del servicio, inicia el bot y funciones
#################
@client.event
async def on_ready():
    print(f'Hola, el bot facetSocial Scrapy esta vivo!\n {client.user} esta conectado!')
    ofertasLaborales.start()
    pasantias.start()
    novedadesProcesarores.start()
    novedadesTD.start()
    novedadesArquitectura.start()

    global ultimaPPSId, ultimaPPSTitulo, ultimaPPSDes
    global ultimaOLId, ultimaOLTitulo, ultimaOLDes
    global ultimaNovedadProcesadores
    global ultimaNovedadTD
    global ultimaNovedadArquitectura

    ultimaPPSId, ultimaPPSTitulo, ultimaPPSDes = ScrapyPPSInicial()
    ultimaOLId, ultimaOLTitulo, ultimaOLDes = ScrapyOLInicial()
    ultimaNovedadProcesadores = ScrapyProcesadoresInicial()
    ultimaNovedadTD = ScrapyTDInicial()
    ultimaNovedadArquitectura = ScrapyArquitecturaInicial()

#################
# Token del bot de Discord
#################
client.run(SECRET_TOKEN_BOT)
