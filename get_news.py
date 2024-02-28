from newspaper import Article
import news_analysis
import article_writer


def parseNewsArticleText(articleUrl):
    try:
        a = Article(articleUrl) 
        a.download()
        a.parse()
        return a.text
    except err:
        print(err)
    return ""
    




def parseNewsArticle(articleUrl):
    a = Article(articleUrl) 
    a.download()
    a.parse()
    authors = a.authors
    authorList = []
    for author in authors:
        if author.startswith("More About") or  author.startswith("The Washington Times"):
            continue
        authorList.append(author)

    authorStr = ",".join(authorList)
    print(a.publish_date)
    print(a.title)
    print(a.text)

    
    #a_id = news_analysis.processArticleTextwithLLM(articleUrl, a.title, a.publish_date, a.text, authorStr)
    a_id = news_analysis.processArticleTextwithOpenAI(articleUrl, a.title, a.publish_date, a.text, authorStr)


    #Store the article in a file...
    #article_writer.store_article(a_id, articleUrl, a.title, a.publish_date, a.text, authorStr)


def parseNewsArticleAndGetSummary(articleUrl):
    a = Article(articleUrl) 
    a.download()
    a.parse()
    print(a.text)

    return news_analysis.processArticleTextAndGenerateSummarywithOpenAI(articleUrl,  a.text)
    

def parseNewsArticle_to_update_iptc(articleUrl):
    a = Article(articleUrl) 
    a.download()
    a.parse()
    authors = a.authors
    authorList = []
    for author in authors:
        if author.startswith("More About") or  author.startswith("The Washington Times"):
            continue
        authorList.append(author)

    authorStr = ",".join(authorList)
    print(a.publish_date)
    print(a.title)
    print(a.text)

    #a_id = news_analysis.processArticleTextwithLLM(articleUrl, a.title, a.publish_date, a.text, authorStr)
    a_id = news_analysis.processArticleText_to_update_IPTC_withOpenAI(articleUrl,  a.text)


    #Store the article in a file...
    #article_writer.store_article(a_id, articleUrl, a.title, a.publish_date, a.text, authorStr)


def parseNewsArticle_only(articleUrl):
    a = Article(articleUrl) 
    a.download()
    a.parse()
    authors = a.authors
    authorList = []
    for author in authors:
        if author.startswith("More About") or  author.startswith("The Washington Times"):
            continue
        authorList.append(author)

    authorStr = ",".join(authorList)
    #print(a.publish_date)
    #print(a.title)
    #print(a.text)
    #print(authorStr)
    return a
