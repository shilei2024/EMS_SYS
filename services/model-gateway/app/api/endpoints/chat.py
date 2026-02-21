"""
聊天相关端点
"""
import asyncio
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.gateway import ChatMessage, ChatRequest, ChatResponse, get_gateway

router = APIRouter()


@router.post("/completion", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    聊天补全

    Args:
        request: 聊天请求，包含消息列表和参数

    Returns:
        聊天响应
    """
    gateway = get_gateway()

    try:
        response = await gateway.chat_with_fallback(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"模型调用失败: {str(e)}"
        )


@router.post("/completion/stream")
async def chat_completion_stream(request: ChatRequest):
    """
    流式聊天补全

    Args:
        request: 聊天请求，stream参数应设为True

    Returns:
        流式响应
    """
    # 设置流式请求
    request.stream = True

    async def stream_generator():
        gateway = get_gateway()
        try:
            # 这里需要实现实际的流式响应逻辑
            # 由于不同提供商的流式API不同，这里简化处理
            response = await gateway.chat_with_fallback(request)

            # 模拟流式输出
            words = response.content.split()
            for word in words:
                yield f"data: {word}\n\n"
                await asyncio.sleep(0.1)

            yield f"data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/batch")
async def batch_chat_completion(requests: list[ChatRequest]):
    """
    批量聊天补全

    Args:
        requests: 聊天请求列表

    Returns:
        批量响应列表
    """
    gateway = get_gateway()
    responses = []

    for request in requests:
        try:
            response = await gateway.chat_with_fallback(request)
            responses.append({
                "success": True,
                "response": response.dict()
            })
        except Exception as e:
            responses.append({
                "success": False,
                "error": str(e)
            })

    return {"responses": responses}


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """
    获取聊天历史

    Args:
        session_id: 会话ID
        limit: 返回消息数量限制

    Returns:
        聊天历史
    """
    # TODO: 从数据库获取聊天历史
    return {
        "session_id": session_id,
        "messages": [],
        "limit": limit
    }


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    清除聊天历史

    Args:
        session_id: 会话ID
    """
    # TODO: 从数据库删除聊天历史
    return {
        "session_id": session_id,
        "cleared": True,
        "message": "聊天历史已清除"
    }