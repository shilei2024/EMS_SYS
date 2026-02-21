"""
模型网关核心模块
负责大模型调用的统一接口、主备切换、健康检查、费用监控等功能
"""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import aiohttp
import backoff
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """模型提供商类型"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    LOCAL = "local"


class ModelCapability(str, Enum):
    """模型能力"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    VISION = "vision"


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    display_name: str
    provider_type: ProviderType
    api_base: str
    api_key: str
    context_length: int = 4096
    max_tokens: int = 2048
    temperature: float = 0.7
    capabilities: List[ModelCapability] = field(default_factory=list)
    priority: int = 1  # 优先级，数字越小优先级越高
    is_enabled: bool = True
    cost_per_token: float = 0.0


@dataclass
class ProviderHealth:
    """提供商健康状态"""
    provider_name: str
    is_healthy: bool = False
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # "system", "user", "assistant"
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """聊天响应"""
    content: str
    model_used: str
    provider_used: str
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0
    response_time_ms: float = 0.0


class BaseProvider(ABC):
    """提供商基类"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.health = ProviderHealth(provider_name=config.name)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """聊天补全"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """计算费用"""
        return (prompt_tokens + completion_tokens) * self.config.cost_per_token


class OpenAIProvider(BaseProvider):
    """OpenAI提供商"""

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """调用OpenAI聊天补全API"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        url = urljoin(self.config.api_base, "/v1/chat/completions")

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": request.model or self.config.name,
            "messages": [msg.dict() for msg in request.messages],
            "temperature": request.temperature or self.config.temperature,
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "stream": request.stream
        }

        start_time = datetime.now()

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()

                end_time = datetime.now()
                response_time_ms = (end_time - start_time).total_seconds() * 1000

                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})

                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                cost = self.calculate_cost(prompt_tokens, completion_tokens)

                return ChatResponse(
                    content=content,
                    model_used=result["model"],
                    provider_used="openai",
                    total_tokens=total_tokens,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost=cost,
                    response_time_ms=response_time_ms
                )
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """OpenAI健康检查"""
        if not self.session:
            return False

        url = urljoin(self.config.api_base, "/v1/models")
        headers = {"Authorization": f"Bearer {self.config.api_key}"}

        start_time = datetime.now()

        try:
            async with self.session.get(url, headers=headers, timeout=10) as response:
                self.health.response_time_ms = (datetime.now() - start_time).total_seconds() * 1000

                if response.status == 200:
                    self.health.is_healthy = True
                    self.health.error_message = None
                    return True
                else:
                    self.health.is_healthy = False
                    self.health.error_message = f"HTTP {response.status}"
                    return False
        except Exception as e:
            self.health.is_healthy = False
            self.health.error_message = str(e)
            return False
        finally:
            self.health.last_check = datetime.now()


class AnthropicProvider(BaseProvider):
    """Anthropic提供商"""

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """调用Anthropic聊天补全API"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        url = urljoin(self.config.api_base, "/v1/messages")

        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # 转换消息格式
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": [{"type": "text", "text": msg.content}]
            })

        payload = {
            "model": request.model or self.config.name,
            "messages": messages,
            "temperature": request.temperature or self.config.temperature,
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "stream": request.stream
        }

        start_time = datetime.now()

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()

                end_time = datetime.now()
                response_time_ms = (end_time - start_time).total_seconds() * 1000

                content = result["content"][0]["text"]

                # Anthropic API不返回token使用情况，估算
                input_tokens = len(result.get("input_tokens", "0"))
                output_tokens = len(result.get("output_tokens", "0"))
                total_tokens = input_tokens + output_tokens
                cost = self.calculate_cost(input_tokens, output_tokens)

                return ChatResponse(
                    content=content,
                    model_used=result["model"],
                    provider_used="anthropic",
                    total_tokens=total_tokens,
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens,
                    cost=cost,
                    response_time_ms=response_time_ms
                )
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """Anthropic健康检查"""
        if not self.session:
            return False

        # Anthropic没有专门的健康检查端点，尝试发送一个小的测试请求
        url = urljoin(self.config.api_base, "/v1/messages")
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "claude-3-haiku-20240307",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5
        }

        start_time = datetime.now()

        try:
            async with self.session.post(url, headers=headers, json=payload, timeout=10) as response:
                self.health.response_time_ms = (datetime.now() - start_time).total_seconds() * 1000

                if response.status == 200:
                    self.health.is_healthy = True
                    self.health.error_message = None
                    return True
                else:
                    self.health.is_healthy = False
                    self.health.error_message = f"HTTP {response.status}"
                    return False
        except Exception as e:
            self.health.is_healthy = False
            self.health.error_message = str(e)
            return False
        finally:
            self.health.last_check = datetime.now()


class ModelGateway:
    """模型网关主类"""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self.models: Dict[str, ModelConfig] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_running = False

    def add_provider(self, provider: BaseProvider):
        """添加提供商"""
        self.providers[provider.config.name] = provider
        self.models[provider.config.name] = provider.config
        logger.info(f"添加模型提供商: {provider.config.name}")

    def get_configured_providers(self) -> List[BaseProvider]:
        """获取已配置的提供商（按优先级排序）"""
        enabled_providers = [
            p for p in self.providers.values()
            if p.config.is_enabled
        ]
        return sorted(enabled_providers, key=lambda p: p.config.priority)

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    async def chat_with_fallback(self, request: ChatRequest) -> ChatResponse:
        """
        聊天请求，支持主备自动切换
        计划中提到的核心逻辑实现
        """
        providers = self.get_configured_providers()

        if not providers:
            raise RuntimeError("没有可用的模型提供商")

        last_error = None

        for provider in providers:
            try:
                # 检查提供商健康状态
                if not provider.health.is_healthy:
                    logger.warning(f"提供商 {provider.config.name} 不健康，跳过")
                    continue

                logger.info(f"尝试使用提供商: {provider.config.name}")
                response = await provider.chat_completion(request)
                logger.info(f"提供商 {provider.config.name} 调用成功，响应时间: {response.response_time_ms:.2f}ms")
                return response

            except Exception as e:
                last_error = e
                logger.error(f"提供商 {provider.config.name} 调用失败: {str(e)}")
                # 标记为不健康
                provider.health.is_healthy = False
                provider.health.error_message = str(e)
                continue

        # 所有提供商都失败
        error_msg = f"所有模型提供商都失败了: {str(last_error)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    async def start_health_check(self, interval_seconds: int = 60):
        """启动定时健康检查"""
        self._is_running = True

        async def health_check_loop():
            while self._is_running:
                try:
                    await self._check_all_providers_health()
                except Exception as e:
                    logger.error(f"健康检查失败: {str(e)}")

                await asyncio.sleep(interval_seconds)

        self._health_check_task = asyncio.create_task(health_check_loop())
        logger.info(f"启动健康检查，间隔: {interval_seconds}秒")

    async def stop_health_check(self):
        """停止健康检查"""
        self._is_running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("停止健康检查")

    async def _check_all_providers_health(self):
        """检查所有提供商的健康状态"""
        tasks = []
        for provider in self.providers.values():
            tasks.append(provider.health_check())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        healthy_count = 0
        for provider, result in zip(self.providers.values(), results):
            if isinstance(result, Exception):
                logger.error(f"提供商 {provider.config.name} 健康检查异常: {str(result)}")
                provider.health.is_healthy = False
                provider.health.error_message = str(result)
            else:
                if result:
                    healthy_count += 1

        total_providers = len(self.providers)
        logger.info(f"健康检查完成: {healthy_count}/{total_providers} 个提供商健康")

    def get_health_status(self) -> Dict[str, Any]:
        """获取所有提供商的健康状态"""
        status = {}
        for name, provider in self.providers.items():
            provider_type = provider.config.provider_type
            # 如果是枚举类型，获取 value；如果已经是字符串，直接使用
            if hasattr(provider_type, 'value'):
                provider_type_value = provider_type.value
            else:
                provider_type_value = str(provider_type)

            status[name] = {
                "is_healthy": provider.health.is_healthy,
                "last_check": provider.health.last_check.isoformat() if provider.health.last_check else None,
                "error_message": provider.health.error_message,
                "response_time_ms": provider.health.response_time_ms,
                "config": {
                    "provider_type": provider_type_value,
                    "priority": provider.config.priority,
                    "is_enabled": provider.config.is_enabled
                }
            }
        return status

    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        models = []
        for config in self.models.values():
            if config.is_enabled:
                # 兼容 provider_type 为字符串或枚举类型
                provider_type = config.provider_type
                if hasattr(provider_type, 'value'):
                    provider_type_value = provider_type.value
                else:
                    provider_type_value = str(provider_type)

                # 兼容 capabilities 为字符串或枚举类型
                capabilities_values = []
                for c in config.capabilities:
                    if hasattr(c, 'value'):
                        capabilities_values.append(c.value)
                    else:
                        capabilities_values.append(str(c))

                models.append({
                    "name": config.name,
                    "display_name": config.display_name,
                    "provider_type": provider_type_value,
                    "context_length": config.context_length,
                    "max_tokens": config.max_tokens,
                    "capabilities": capabilities_values,
                    "priority": config.priority
                })
        return models


# 全局网关实例
_gateway_instance: Optional[ModelGateway] = None


def get_gateway() -> ModelGateway:
    """获取全局网关实例"""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = ModelGateway()
    return _gateway_instance


async def initialize_gateway(configs: List[Dict[str, Any]]) -> ModelGateway:
    """初始化网关"""
    gateway = get_gateway()

    for config_data in configs:
        try:
            config = ModelConfig(**config_data)

            if config.provider_type == ProviderType.OPENAI:
                provider = OpenAIProvider(config)
            elif config.provider_type == ProviderType.ANTHROPIC:
                provider = AnthropicProvider(config)
            else:
                logger.warning(f"不支持的提供商类型: {config.provider_type}")
                continue

            gateway.add_provider(provider)

        except Exception as e:
            logger.error(f"初始化提供商失败: {config_data.get('name', 'unknown')} - {str(e)}")

    # 启动健康检查
    await gateway.start_health_check()

    return gateway