"""LLM 工厂类 - 支持多种大模型"""
from typing import Optional
from langchain_core.language_models import BaseLLM
from langchain.chat_models import ChatOpenAI


class LLMFactory:
    """大模型工厂类"""
    
    @staticmethod
    def create_llm(
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ) -> BaseLLM:
        """
        创建 LLM 实例
        
        Args:
            provider: 模型提供商 (openai, dashscope, zhipuai, anthropic)
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            api_key: API 密钥
            api_base: API 基础地址
            **kwargs: 其他参数
            
        Returns:
            LLM 实例
        """
        provider = provider.lower()
        
        if provider == "openai":
            return LLMFactory._create_openai(
                model_name or "gpt-3.5-turbo",
                temperature,
                max_tokens,
                api_key,
                api_base,
                **kwargs
            )
        elif provider == "dashscope":
            return LLMFactory._create_dashscope(
                model_name or "qwen-turbo",
                temperature,
                max_tokens,
                api_key,
                **kwargs
            )
        elif provider == "zhipuai":
            return LLMFactory._create_zhipuai(
                model_name or "chatglm_turbo",
                temperature,
                max_tokens,
                api_key,
                **kwargs
            )
        elif provider == "anthropic":
            return LLMFactory._create_anthropic(
                model_name or "claude-2",
                temperature,
                max_tokens,
                api_key,
                **kwargs
            )
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")
    
    @staticmethod
    def _create_openai(
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        api_base: Optional[str],
        **kwargs
    ) -> BaseLLM:
        """创建 OpenAI LLM"""
        params = {
            "model_name": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if api_key:
            params["openai_api_key"] = api_key
        if api_base:
            params["openai_api_base"] = api_base
        
        params.update(kwargs)
        
        return ChatOpenAI(**params)
    
    @staticmethod
    def _create_dashscope(
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        **kwargs
    ) -> BaseLLM:
        """创建阿里云通义千问 LLM"""
        try:
            from langchain_community.llms import Tongyi
            
            params = {
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if api_key:
                params["dashscope_api_key"] = api_key
            
            params.update(kwargs)
            
            return Tongyi(**params)
        except ImportError:
            raise ImportError("请安装 dashscope: pip install dashscope")
    
    @staticmethod
    def _create_zhipuai(
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        **kwargs
    ) -> BaseLLM:
        """创建智谱 AI LLM"""
        try:
            from langchain_community.llms import ChatGLM
            
            params = {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if api_key:
                params["api_key"] = api_key
            
            params.update(kwargs)
            
            return ChatGLM(**params)
        except ImportError:
            raise ImportError("请安装 zhipuai: pip install zhipuai")
    
    @staticmethod
    def _create_anthropic(
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        **kwargs
    ) -> BaseLLM:
        """创建 Anthropic Claude LLM"""
        try:
            from langchain_community.chat_models import ChatAnthropic
            
            params = {
                "model": model_name,
                "temperature": temperature,
                "max_tokens_to_sample": max_tokens,
            }
            
            if api_key:
                params["anthropic_api_key"] = api_key
            
            params.update(kwargs)
            
            return ChatAnthropic(**params)
        except ImportError:
            raise ImportError("请安装 anthropic: pip install anthropic")


def get_llm_from_config(config) -> BaseLLM:
    """
    从配置创建 LLM 实例
    
    Args:
        config: 配置对象
        
    Returns:
        LLM 实例
    """
    return LLMFactory.create_llm(
        provider=config.default_llm_provider,
        model_name=config.default_model_name,
        temperature=config.default_temperature,
        max_tokens=config.default_max_tokens,
        api_key=getattr(config, f"{config.default_llm_provider}_api_key", None),
        api_base=getattr(config, f"{config.default_llm_provider}_api_base", None),
    )
