from langchain_openai import ChatOpenAI
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class LLM:
    def __init__(self, base_url, api_key, model, verbose=False):
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=base_url,
            model=model,
            streaming=True,
            verbose=verbose
        )
        self.store = {}
        
        system_message = ""
        with open('resources/persona.txt', 'r') as file:
            system_message = ("system", file.read().replace('\n', ''))
        
        history_placeholder = MessagesPlaceholder(variable_name="history")
        human_message = ("human", "{input}")
        self.prompt = ChatPromptTemplate.from_messages([system_message, history_placeholder, human_message])

        self.llm_chain = self.prompt | self.llm
        self.with_message_history = RunnableWithMessageHistory(
            self.llm_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        
    def get_config(self, session_id="dev"):
        return {"configurable": {"session_id": session_id}}
                
    async def get_response(self, input, config):
        async for chunk in self.with_message_history.astream({"input": input}, config=config):
            yield chunk.content

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]
    