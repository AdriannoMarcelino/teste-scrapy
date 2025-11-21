import re
import scrapy
from datetime import datetime
from trf5.items import ProcessoItem

class Trf5Spider(scrapy.Spider):
    name = 'trf5'

    def __init__(self, processo=None, cnpj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processo = [p.strip() for p in processo.split(',')] if processo else []
        self.cnpj = cnpj

    def start_requests(self):
        if self.processo:
            for p in self.processo:
                url = f"https://www5.trf5.jus.br/processo/{p}"
                yield scrapy.Request(url=url, callback=self.parse)
        elif self.cnpj:
            cnpj_limpo = self.cnpj.replace('.', '').replace('/', '').replace('-', '')
            url = f"https://cp.trf5.jus.br/processo/cpf/porData/ativos/{cnpj_limpo}/0"
            yield scrapy.Request(url=url, callback=self.parse_cnpj_response)
        else:
            raise ValueError("Passe um processo ou CNPJ: scrapy crawl trf5 -a processo=XXXX ou -a cnpj=YYYY")
    
    def parse_cnpj_response(self, response):
        processos_links = response.xpath("//table[@class='consulta_resultados']//a[contains(@title, 'Processo')]/@href").getall()
        for link in processos_links:
            yield scrapy.Request(url=response.urljoin(link), callback=self.parse)

        next_page = response.xpath("//a[text()='>']/@href").get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse_cnpj_response)
            
    def parse(self, response):
        nodes = response.xpath('//p[@style]')
        texts = [n.xpath('normalize-space(.)').get() or '' for n in nodes]

        numero_processo = texts[0] if len(texts) > 0 else ''
        numero_legado = texts[1] if len(texts) > 1 else ''

        match2 = re.search(r'(\d{2}\.\d{2}\.\d{5}-\d{1})', numero_legado)
        numero_legado = match2.group(0).strip() if match2 else (numero_legado.strip() or None)

        match1 = re.search(r'(\d{7}-\d{2}\.\d{4}\.\d+\.\d+\.\d+)', numero_processo)
        if not match1:
            match1 = re.search(r'[\d\.\-]{10,}', numero_processo)
        numero_processo = match1.group(0).strip() if match1 else None    

        if not numero_processo and numero_legado:
            numero_processo = numero_legado

        autuacao_texto = response.xpath('normalize-space(//div)').get()
        data_autuacao = None
        if autuacao_texto:
            match_data = re.search(r'(\d{2}/\d{2}/\d{4})', autuacao_texto)
            if match_data:
                data = datetime.strptime(match_data.group(0), '%d/%m/%Y')
                data_autuacao = data.strftime('%d-%m-%Y')

        item = ProcessoItem()
        item["numero_processo"] = numero_processo
        item["numero_legado"] = numero_legado
        item["data_autuacao"] = data_autuacao
        item["relator"] = self.extract_relator(response)
        item["envolvidos"] = self.extract_envolvidos(response)
        item["movimentacoes"] = self.extract_movimentacoes(response)
        item["url_origem"] = response.url

        yield item

    def extract_relator(self, response):
        relator = response.xpath(
            "normalize-space(//td[contains(translate(normalize-space(.),'RELATOR','relator'),'relator')]/following-sibling::td[1])"
        ).get()
        if not relator:
            relator = response.xpath("normalize-space(//td[normalize-space(.)='Relator']/following-sibling::td[1])").get()
        if relator:
            relator = relator.strip()
            relator = re.sub(r'^:+\s*', '', relator)
            return relator or None
        return None
    
    def extract_envolvidos(self, response):
        envolvidos = []
        table = response.xpath("(//table)[3]")
        if not table:
            return envolvidos
        for tr in table.xpath(".//tr"):
            papel = tr.xpath("normalize-space(./td[1]//text())").get(default="").strip()
            nome = tr.xpath("normalize-space(./td[2]//b/text())").get(default="").strip()
            if papel.upper().find("RELATOR") != -1:
                continue
            if papel or nome:
                envolvidos.append({'papel': papel or None, 'nome': nome or None})
        return envolvidos

    def extract_movimentacoes(self, response):
        movimentacoes = []
        tables = response.xpath("//table[contains(., 'Em ')]")
        for tbl in tables:
            data_mov = tbl.xpath("normalize-space(.//a/text())").get(default="")
            if data_mov.startswith("Em "):
                data_mov = data_mov.replace("Em ", "").strip()
            descricao = tbl.xpath("normalize-space(.//tr[2]/td[2])").get(default="").strip()
            if data_mov or descricao:
                movimentacoes.append({'data': data_mov or None, 'texto': descricao or None})
        return movimentacoes
