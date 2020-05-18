from lxml.etree import HTML


def parse_kuaidaili(text):
    try:
        context = HTML(text)
    except ValueError:
        return None
    nodes = context.xpath('//*/div[@id="list"]/table/tbody/tr')
    for node in nodes:
        try:
            yield f'{node.xpath("./td[1]/text()")[0]}:{node.xpath("./td[2]/text()")[0]}'
        except IndexError:
            pass
