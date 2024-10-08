from src import util
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

class LLM:
    def __init__(self, keyword):
        self.keyword = keyword
        self.llm = ChatOpenAI(temperature=0, 
                            api_key= util.load_key(), 
                            max_tokens=2000,
                          )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
        self.parser = StrOutputParser()

    def summarize_article(self, article):
        chunks = self.text_splitter.split_text(article)
        chunk_tmplt = """
        글을 읽고 요점을 정리해줘. 각 요점은 완벽한 문장으로 문법에 맞게 개괄식으로 정리해줘.
        요약 결과는 반드시 세 문장이 넘지 않도록 해야해.

        요약할 글:
        """
        chunk_prmpt = ChatPromptTemplate.from_messages(
            [("system", chunk_tmplt), ("user", "{text}")]
        )
        chunk_chain = chunk_prmpt | self.llm | self.parser

        chunk_summaries = [chunk_chain.invoke({'text': chunk}) for chunk in chunks]
        chunk_summaries = "\n\n".join(chunk_summaries)
        # print('기사요약: ', chunk_summaries, '\n')

        article_tmplt = """
        뉴스기사 일부를 개괄식으로 요약해둔 글을 읽고, 육하원칙에 따라 정리해줘 
        요약할 글:
        """
        article_prmpt = ChatPromptTemplate.from_messages(
            [("system", article_tmplt), ("user", "{text}")]
        )
        article_chain = article_prmpt | self.llm | self.parser
        final_summary = article_chain.invoke({'text': chunk_summaries})
        # print('종합요약: ', final_summary, '\n')

        return final_summary
    
    def summarize_articles(self, articles):
        return [self.summarize_article(x) for x in articles]

    def generate_report(self, summaries):
        report_tmplt = """
        {keyword}를 중심으로 최근 다뤄진 뉴스기사에 대한 요약글들을 참고해서 통합적인 이슈 리포트를 작성해줘.
        서술된 객관적인 사실들을 나열하고, {keyword}에 대한 여론 분석을 수행해줘.
 
        요약:
        """
        report_prmpt = ChatPromptTemplate.from_messages(
            [("system", report_tmplt), ("user", "{text}")]
        )
        report_chain = report_prmpt | self.llm | self.parser
        report = report_chain.invoke({
            'keyword': self.keyword, 
            'text': "\n\n".join(summaries), 
        })
        return report

    def analysis(self, articles):
        summaries = self.summarize_articles(articles)
        summaries = [f'\n\n뉴스 {i}: {x}' for i, x in enumerate(summaries)]
        # print('입력:', summaries)
        report = self.generate_report(summaries)
        return report.replace('\n', '') 