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
def ScrapyNombreSeccion():
    class NombreDelObjeto(Item):
        id = Field()
        link = Field()
        titulo = Field()
        fecha = Field()
        descripcion = Field()

    class FINombreDelSpider(Spider):
        name = "NombreSpider"

        custom_settings = {
            "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
        }
        start_urls = ['URL']

        def parse(self, response):
            sel = Selector(response)
            listaPasantia = sel.xpath("//div[@id='panel-194-0-0-0']//article[contains(@id, 'post-')]")

            for p in listaPasantia:
                item = ItemLoader(NombreDelObjeto(), p)

                item.add_xpath("id", "@id")
                item.add_xpath("link", ".//h1/a/@href")
                item.add_xpath("titulo", ".//h1/a/text()")
                item.add_xpath("fecha", ".//div[@class='entry-meta']/a/time/text()")

                d = [x.xpath(".//text()").extract() for x in
                     p.xpath(".//div[@class='entry-content']//div[contains(@class,'siteorigin-widget')]")]
                item.add_value("descripcion", d)

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
        crawler.crawl(FINombreDelSpider)
        crawler.start()

    processPPS = Process(target=crawl)
    processPPS.start()
    processPPS.join()


################################
# Func. ScrapyInicial: Scrapea/Recolecta solo el titulo de la ultima publicacion publicada
################################
def ScrapyNombreSeccionInicial():
    class NombreDelObjetoInicial(Item):
        id = Field()
        titulo = Field()
        descripcion = Field()

    class FINombreDelSpiderInicial(Spider):
        name = "NombreSpider"

        custom_settings = {
            "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
        }
        start_urls = ['URL']

        def parse(self, response):
            sel = Selector(response)
            p = sel.xpath("//div[@id='panel-194-0-0-0']//article[contains(@id, 'post-')][1]")

            item = ItemLoader(NombreDelObjetoInicial(), p)

            item.add_xpath("id", "@id")
            item.add_xpath("titulo", ".//h1/a/text()")

            d = [x.xpath(".//text()").extract() for x in p.xpath(".//div[@class='entry-content']//div[contains(@class,'siteorigin-widget')]")]

            item.add_value("descripcion", d)

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
        crawler.crawl(FINombreDelSpiderInicial)
        crawler.start()

    processPPS = Process(target=crawl)
    processPPS.start()
    processPPS.join()

   
    #####################
    # Leo y devuelvo el titulo de la ultima publicacion publicada
    #####################

    ruta = 'NombreArchivoJSON.json'
    with open(ruta) as contenido:
        des = ""
        publicacion = json.load(contenido)

        pub = publicacion[0]
        idPPS = pub["id"][0]
        tituloPPS = pub["titulo"][0]
        descripcion = pub["descripcion"][0]

        for d in descripcion:
            if ('\n\u2022' in d):
                des = des + d.strip("\t")
            elif ('\u2022' in d):
                des = des + "\n" + d.strip("\t")
            elif ('\u27a2' in d):
                des = des + "\n" + d.strip("\t")
            elif ('\n' in d):
                des = des + d.strip("\t")
            elif (':' in d):
                des = des + d.strip("\t") + "\n"
            else:
                des = des + d.strip("\t")

        return idPPS, tituloPPS, des