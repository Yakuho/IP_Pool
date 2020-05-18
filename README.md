# 自定义代理池

## 采集网站的配置文件->spider and parse
可以改动文件
spider：配置该网页的请求头，爬取页数等相关配置，return类型一定要用yield
parse：配置该网页的解析网页的规则，最后解析出ip:port的字符串，用yield返回
domain: 配置网站名与你上面写的spider和parse对应上的名字
    例如： 你使用request_aaa与parse_aaa (spider文件与parse文件写的对应名字要一样，这里指的是aaa)
    则domain的对应配置则为 网站名-aaa
main: 运行文件
