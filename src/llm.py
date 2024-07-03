import sys

# LangChain Models
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

import json

sys.path.append('../util')
from config import Config
config = Config('../config/config.yml').parse()

class LLM:
    def __init__(self, keyword):
        self.keyword = keyword
        self.llm = OpenAI(temperature=0, 
                          api_key=config['KEY'], 
                          max_tokens=-1
                          )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        self.prmpt_each_article = f"키워드 '{keyword}'와 관련된 다음 뉴스에서 육하원칙에 따라서 반드시 한 문장으로 문서를 요약해줘.\n\n{{text}}\n\n 요약:"

    def summarize_article(self, article):
        chunks = self.text_splitter.split_text(article)
        chunk_summary_template = """
        글을 읽고 요점을 정리해줘. 각 요점은 완벽한 문장으로 문법에 맞게 개괄식으로 정리해줘.
        요약할 글: {text}
        
        요약 결과:
        """
        chunk_summary_prompt = PromptTemplate(template=chunk_summary_template, input_variables=["text"])
        chunk_summary_chain = LLMChain(llm=self.llm, prompt=chunk_summary_prompt)
        chunk_summaries = [chunk_summary_chain.invoke(chunk)['text'] for chunk in chunks]
        chunk_summaries = "\n\n".join(chunk_summaries)
        # print('기사요약: ', chunk_summaries, '\n')

        # Combine chunk summaries into a final article summary
        final_summary_template = """
        전체 뉴스기사를 나눠서 요약해 놓은 문장들을 취합해서 한 문장으로 육하원칙에 따라 정확히 정리해줘        
        요약할 글: {summaries}
        
        통합적인 요약:
        """
        final_summary_prompt = PromptTemplate(template=final_summary_template, input_variables=["summaries"])
        final_summary_chain = LLMChain(llm=self.llm, prompt=final_summary_prompt)
        final_summary = final_summary_chain.invoke(chunk_summaries)['text']
        # print('종합요약: ', final_summary, '\n')

        return final_summary
    
    def summarize_articles(self, articles):
        return [self.summarize_article(x) for x in articles]

    def generate_report(self, summaries):
        template = """
        {keyword}를 중심으로 최근 다뤄진 뉴스기사에 대한 요약글들을 참고해서 통합적인 이슈 리포트를 작성해줘.
        서술된 객관적인 사실들을 나열하고, {keyword}에 대한 여론 분석을 수행해줘.
 
        요약:
        {summaries}

        여론 분석:
        """
        prompt = PromptTemplate(template=template, input_variables=["keyword", "summaries"])
        chain = LLMChain(llm=self.llm, prompt=prompt)
        report = chain.invoke({
            'summaries': "\n\n".join(summaries), 
            'keyword': self.keyword
        })
        return report

    def analysis(self, articles):
        summaries = self.summarize_articles(articles)
        summaries = [f'\n\n뉴스 {i}: {x}' for i, x in enumerate(summaries)]
        report = self.generate_report(summaries)
        return report['text'].replace('\n', '')