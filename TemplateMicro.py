from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
import os
import json
from os import remove
from multiprocessing.context import Process

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

log_enabled = config['DEBUG']['LOG_ENABLED']

################################
# Func. Scrapy: Scrapea/Recolecta la informacion de la pagina principal
################################
def ScrapyNombreMateria():
    class NombreObjeto(Item):
        id = Field()
        fecha = Field()
        descripcion = Field()

    class NombreMateriaSpider(Spider):
        name = "NombreSpider"

        custom_settings = {
            "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
        }
        start_urls = ['URL']

        def parse(self, response):
            sel = Selector(response)
            listaNovedades = sel.xpath("//table[@class='table table-striped table-bordered table-condensed']//tr")

            i = 0

            for n in listaNovedades:
                item = ItemLoader(NombreObjeto(), n)

                item.add_value("id", i)
                item.add_xpath("fecha", ".//td[1]/text()")

                d = [x.xpath(".//text()").extract() for x in n.xpath(".//td[2]")]
                item.add_value("descripcion", d)

                i += 1

                yield item.load_item()


    #####################
    # Para correr la funcion scrapy sin terminal
    #####################
    archivo = "NombreArchivoJSON.json"

    if (os.path.isfile(archivo)):
        remove(archivo)

    def crawl():
        crawler = CrawlerProcess({
            'FEED_FORMAT': 'json',
            'FEED_URI': 'NombreArchivoJSON.json',
            'LOG_ENABLED': log_enabled
        })
        crawler.crawl(NombreMateriaSpider)
        crawler.start()

    processProcesadores = Process(target=crawl)
    processProcesadores.start()
    processProcesadores.join()


################################
# Func. ScrapyInicial: Scrapea/Recolecta solo el titulo de la ultima novedad
################################
def ScrapyNombreMateriaInicial():
    class NombreObjeto(Item):
        id = Field()
        fecha = Field()
        descripcion = Field()

    class NombreMateriaSpider(Spider):
        name = "NombreSpider"

        custom_settings = {
            "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
        }
        start_urls = ['URL']

        def parse(self, response):
            sel = Selector(response)
            n = sel.xpath("//table[@class='table table-striped table-bordered table-condensed']//tr[1]")

            i = 0

            item = ItemLoader(NombreObjeto(), n)

            item.add_value("id", i)
            item.add_xpath("fecha", ".//td[1]/text()")

            d = [x.xpath(".//text()").extract() for x in n.xpath(".//td[2]")]
            item.add_value("descripcion", d)

            i += 1

            yield item.load_item()


    #####################
    # Para correr la funcion scrapy sin terminal
    #####################
    archivo = "NombreArchivoJSON.json"

    if (os.path.isfile(archivo)):
        remove(archivo)

    def crawl():
        crawler = CrawlerProcess({
            'FEED_FORMAT': 'json',
            'FEED_URI': 'NombreArchivoJSON.json',
            'LOG_ENABLED': log_enabled
        })
        crawler.crawl(NombreMateriaSpider)
        crawler.start()

    processProcesadores = Process(target=crawl)
    processProcesadores.start()
    processProcesadores.join()


    #####################
    # Leo y devuelvo la descripcion de la ultima novedad publicada
    #####################
    ruta = 'NombreArchivoJSON.json'
    with open(ruta) as contenido:
        novedad = json.load(contenido)
        n = novedad[0]
        descripcionNovedad = "".join(n["descripcion"][0])

        return descripcionNovedad