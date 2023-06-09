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
# Func. ScrapyTD: Scrapea/Recolecta la informacion de la pagina principal de Transmisiones de Datos
################################
def ScrapyTD():
    class Novedad(Item):
        id = Field()
        fecha = Field()
        descripcion = Field()

    class TDSpider(Spider):
        name = "NovedadesSpider"

        custom_settings = {
            "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
        }
        start_urls = ['https://microprocesadores.unt.edu.ar/transmision/']

        def parse(self, response):
            sel = Selector(response)
            listaNovedades = sel.xpath("//table[@class='table table-striped table-bordered table-condensed']//tr")

            i = 0

            for n in listaNovedades:
                item = ItemLoader(Novedad(), n)

                item.add_value("id", i)
                item.add_xpath("fecha", ".//td[1]/text()")

                d = [x.xpath(".//text()").extract() for x in n.xpath(".//td[2]")]
                item.add_value("descripcion", d)

                i += 1

                yield item.load_item()

    ################################
    # Correr la funcion Scrapy sin terminal
    ################################
    archivo = "data/novedadesTD.json"

    if (os.path.isfile(archivo)):
        remove(archivo)

    def crawl():
        crawler = CrawlerProcess({
            'FEED_FORMAT': 'json',
            'FEED_URI': 'data/novedadesTD.json',
            'LOG_ENABLED': log_enabled
        })
        crawler.crawl(TDSpider)
        crawler.start()

    processProcesadores = Process(target=crawl)
    processProcesadores.start()
    processProcesadores.join()


################################
# Func. ScrapyTDInicial: Scrapea/Recolecta solo el titulo de la ultima novedad
################################
def ScrapyTDInicial():
    class Novedad(Item):
        id = Field()
        fecha = Field()
        descripcion = Field()

    class TDSpider(Spider):
        name = "NovedadesSpider"

        custom_settings = {
            "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
        }
        start_urls = ['https://microprocesadores.unt.edu.ar/transmision/']

        def parse(self, response):
            sel = Selector(response)
            n = sel.xpath("//table[@class='table table-striped table-bordered table-condensed']//tr[1]")

            i = 0

            item = ItemLoader(Novedad(), n)

            item.add_value("id", i)
            item.add_xpath("fecha", ".//td[1]/text()")

            d = [x.xpath(".//text()").extract() for x in n.xpath(".//td[2]")]
            item.add_value("descripcion", d)

            i += 1

            yield item.load_item()

    ################################
    # Correr la funcion Scrapy sin terminal
    ################################
    archivo = "data/novedadesTD.json"

    if (os.path.isfile(archivo)):
        remove(archivo)

    def crawl():
        crawler = CrawlerProcess({
            'FEED_FORMAT': 'json',
            'FEED_URI': 'data/novedadesTD.json',
            'LOG_ENABLED': log_enabled
        })
        crawler.crawl(TDSpider)
        crawler.start()

    processProcesadores = Process(target=crawl)
    processProcesadores.start()
    processProcesadores.join()

    #####################
    # Leo y devuelvo la descripcion de la ultima novedad publicada
    #####################
    ruta = 'data/novedadesTD.json'
    with open(ruta) as contenido:
        novedad = json.load(contenido)
        n = novedad[0]
        descripcionNovedad = "".join(n["descripcion"][0])

        return descripcionNovedad