import scrapy


class ProcessoItem(scrapy.Item):
    numero_processo = scrapy.Field()
    numero_legado = scrapy.Field()
    data_autuacao = scrapy.Field()
    envolvidos = scrapy.Field()
    relator = scrapy.Field()
    movimentacoes = scrapy.Field()
    url_origem = scrapy.Field()