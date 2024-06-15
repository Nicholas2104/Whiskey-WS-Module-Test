import requests
from bs4 import BeautifulSoup
import time
# Queremos coletar adequadamente todos os dados de todos os produtos de certa subcategoria
# Isso pode ser feito iternado sobre cada pagina do site, ate nao haver mais conteudo
# a cada iteracao acessamso a pagina individual de cada produto e lemos suas caracteristicas
# Caracteristicas: Nome, preco, avaliacao, numero de avaliacoes, conteudo escrito da avaliacoes
# depois de coletar todas a caracteristicas podemos armazenar estas informacoes num dicionario onde a chave e o nome do produto
def collect_all_product_info(default_url): # temos como parametro a url basica do site
    all_product_info = dict()
    page_num = 1
    while True:
        print(page_num)
        url = default_url+str(page_num) # esepecificamos qual pagina queremos acessar
        start_time = time.time()
        main_page = requests.get(url)
        print("--- %s seconds ---" % (time.time() - start_time))
        main_page_soup = BeautifulSoup(main_page.text, "lxml")
        if main_page_soup.find_all("div", class_="main-content") == []: # Se a a pagina n tiver mais conteudo saimos do loop, pois revistamos todo o site
            break
        else:
            products_on_page = main_page_soup.find_all("a",class_="product-link") # todo produto possui um segmento individual sobre a class product-link
            for product in products_on_page:
                product_url = "https://sipwhiskey.com"+product['href'] # adcionamos a url basica do site o complemento do site do produto especifico
                product_page = requests.get(product_url)
                product_page_soup = BeautifulSoup(product_page.text, "lxml")
                name = product_page_soup.find("h1", class_="title").text
                # Preco eh exibido como "$x.xxx,cc" onde c sao centavos - para adequadamente transformar o preco num float removemos o prefixo e a virgula
                price = float((product_page_soup.find("span", class_="price theme-money").text).removeprefix("$").replace(",",""))
                reviews = product_page_soup.find_all("div",class_="stamped-review")
                # Se nao existir avaliacao, associamos valores default para as caracterisiticas do produto
                if len(reviews) == 0:
                    rating = "none"
                    num_reviews = "none"
                    review_content = []
                else:
                    review_content = []
                    rating = float(product_page_soup.find("span",class_="stamped-summary-text-1").text)
                    # numero de avaliacoes eh aramazenada como o texto padrao "Based on X reviews" - assim para poder adequadamente 
                    # transformar essa variavel num inteiro selecionamos apenas o X dessa string
                    num_reviews = int((product_page_soup.find("span",class_="stamped-summary-caption stamped-summary-caption-2").find("span").text).split(" ")[2])
                    # para executar uma analise qualitativa dos dados precisamos isolar o conteudo escrito de cada avaliacao
                    for review in reviews: # assim comecamos iterando por cada avaliacao
                        #achamos o titulo da avaliacao - Muito importante porque muitas vezes resume proposito da avaliacao
                        header = (review.find("div", class_="stamped-review-body").find(class_="stamped-review-header-title").text).strip() 
                        #achamaos tambem o conteudo escrito da avaliacao
                        body = (review.find("div", class_="stamped-review-body").find(class_="stamped-review-content-body").text).strip()
                        #adcionamos a uma unica variavel a avaliacao escrita e adcionamos ao review_content que aramazena todas as avaliacoes escritas
                        #individuais do produto
                        content = f"{header}: {body}"
                        review_content.append(content)
                # Finalmente aramzenamos toda a infomrcao do produto em um dicionario facilmenre acessivel
                all_product_info[name] = {'price':price,'rating':rating,'# reviews':num_reviews,'review content': review_content}  
        page_num+=1 # seguimos para a proxima pagina
    return all_product_info

tequila_page_url_default = "https://sipwhiskey.com/collections/rye-whiskey?page="
all_product_links = collect_all_product_info(tequila_page_url_default)

