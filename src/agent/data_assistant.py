"""数据助手 Agent 核心逻辑"""
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate


class DataAssistantAgent:
    """数据助手 Agent"""
    
    def __init__(
        self,
        llm,
        vectorstore_manager,
        rag_retriever,
        agent_name: str = "数据小秘书",
        agent_description: str = "我是你的数据管理助手",
        max_history: int = 10
    ):
        """
        初始化数据助手 Agent
        
        Args:
            llm: 大语言模型
            vectorstore_manager: 向量数据库管理器
            rag_retriever: RAG 检索器
            agent_name: Agent 名称
            agent_description: Agent 描述
            max_history: 最大对话历史数
        """
        self.llm = llm
        self.vectorstore_manager = vectorstore_manager
        self.rag_retriever = rag_retriever
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.max_history = max_history
        
        # 初始化对话记忆
        self.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True,
            k=max_history
        )
        
        # 创建对话链
        self.conversation_chain = self._create_conversation_chain()
    
    def _create_conversation_chain(self) -> ConversationChain:
        """创建对话链"""
        
        prompt_template = f"""你是 {self.agent_name}，{self.agent_description}。

你可以帮助用户:
1. 查询和分析公司数据库中的数据
2. 解答关于数据结构的问题
3. 提供数据洞察和建议
4. 执行数据相关的任务

对话历史:
{{history}}

用户: {{input}}

{self.agent_name}:"""
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=prompt_template
        )
        
        return ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )
    
    def chat(self, user_input: str, use_rag: bool = True) -> Dict[str, Any]:
        """
        与用户对话
        
        Args:
            user_input: 用户输入
            use_rag: 是否使用 RAG 检索
            
        Returns:
            对话结果
        """
        response = {
            "user_input": user_input,
            "agent_name": self.agent_name,
            "use_rag": use_rag,
        }
        
        # 如果使用 RAG，先检索相关信息
        if use_rag:
            try:
                rag_result = self.rag_retriever.query(user_input)
                
                # 将 RAG 结果整合到对话中
                context = f"\n\n[相关数据库信息]\n{rag_result['answer']}\n"
                enhanced_input = user_input + context
                
                # 使用增强后的输入进行对话
                agent_response = self.conversation_chain.predict(input=enhanced_input)
                
                response["answer"] = agent_response
                response["rag_sources"] = rag_result.get("sources", [])
                
            except Exception as e:
                # RAG 失败时，使用普通对话
                print(f"RAG 检索失败: {str(e)}，使用普通对话模式")
                agent_response = self.conversation_chain.predict(input=user_input)
                response["answer"] = agent_response
                response["error"] = f"RAG 检索失败: {str(e)}"
        else:
            # 普通对话
            agent_response = self.conversation_chain.predict(input=user_input)
            response["answer"] = agent_response
        
        return response
    
    def query_database(self, query: str) -> Dict[str, Any]:
        """
        查询数据库相关信息
        
        Args:
            query: 查询问题
            
        Returns:
            查询结果
        """
        return self.rag_retriever.query(query)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        messages = self.memory.chat_memory.messages
        
        history = []
        for msg in messages:
            history.append({
                "role": msg.type,
                "content": msg.content
            })
        
        return history
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.memory.clear()
        print("✓ 对话历史已清空")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取 Agent 状态
        
        Returns:
            状态信息
        """
        return {
            "agent_name": self.agent_name,
            "agent_description": self.agent_description,
            "conversation_count": len(self.memory.chat_memory.messages),
            "max_history": self.max_history,
            "vectorstore_type": self.vectorstore_manager.vector_db_type,
        }
