from fastmcp import FastMCP
import random
from typing import Optional
import asyncio
import os
import logging
from dotenv import load_dotenv
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import litellm  # type: ignore
    HAS_LITELLM = True
except Exception:
    HAS_LITELLM = False

load_dotenv()

# 初始化 MCP Server（LiteLLM 版本）
mcp = FastMCP("self-evolving-mcp-litellm", "一个使用 LiteLLM 打分的自进化 Prompt 优化 MCP Server")


# 全局状态（Prompt Pool）
prompt_pool = [
    "精确搜索: {query}",
    "拓展相关主题: {query}",
    "用学术角度解释: {query}"
]


# 配置 LiteLLM 模型
# - DeepSeek 示例：LITELLM_JUDGE_MODEL=deepseek/deepseek-chat 并设置 OPENAI_API_KEY, OPENAI_BASE_URL=https://api.deepseek.com
# - Ollama 示例：LITELLM_JUDGE_MODEL=ollama/llama3 并设置 OPENAI_BASE_URL=http://localhost:11434/v1, OPENAI_API_KEY=ollama
JUDGE_MODEL: str = os.getenv("LITELLM_JUDGE_MODEL", "deepseek/deepseek-chat")


async def _score_with_litellm(prompt: str) -> Optional[int]:
    if not HAS_LITELLM:
        logger.warning("LiteLLM 未安装，跳过 LLM 评分")
        print("LiteLLM 未安装，跳过 LLM 评分")
        return None
    
    logger.info(f"开始 LLM 评分，使用模型: {JUDGE_MODEL}")
    print(f"开始 LLM 评分，使用模型: {JUDGE_MODEL}")
    logger.debug(f"评分提示词: {prompt[:200]}...")
    
    try:
        # 先判断是否有异步接口
        if hasattr(litellm, "acompletion"):
            logger.info("使用异步接口 acompletion")
            print("使用异步接口 acompletion")
            resp = await litellm.acompletion(  # type: ignore[attr-defined]
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8,
                temperature=0.0,
            )
        else:
            logger.info("使用同步接口 completion")
            print("使用同步接口 completion")
            resp = litellm.completion(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8,
                temperature=0.0,
            )

        logger.info(f"LLM 响应类型: {type(resp)}")
        logger.debug(f"LLM 原始响应: {resp}")

        # 兼容 LiteLLM 的返回结构（可能是 dict 或对象）
        choices = getattr(resp, "choices", None) or resp.get("choices")  # type: ignore[union-attr]
        if not choices:
            logger.error("LLM 响应中没有 choices 字段")
            return None
            
        logger.info(f"choices 数量: {len(choices)}")
        
        message = choices[0].get("message") or getattr(choices[0], "message", {})
        content = (message.get("content") if isinstance(message, dict) else getattr(message, "content", "")).strip()
        
        logger.info(f"LLM 返回内容: '{content}'")
        
        # 尝试解析分数
        try:
            score = int(str(content).strip())
            logger.info(f"成功解析分数: {score}")
            return score
        except ValueError as e:
            logger.error(f"无法将内容 '{content}' 解析为整数: {e}")
            return None
            
    except Exception as e:
        logger.error(f"LLM 调用失败: {type(e).__name__}: {e}")
        import traceback
        logger.debug(f"详细错误堆栈:\n{traceback.format_exc()}")
        return None


def _score_with_heuristic(original: str, rewritten: str, results: str) -> int:
    # 基于词重合度的简易启发式评分，范围 1-5
    tokens_q = set(w for w in rewritten.lower().split() if len(w) > 1)
    tokens_r = set(w for w in results.lower().split() if len(w) > 1)
    if not tokens_q or not tokens_r:
        return 1
    overlap = len(tokens_q & tokens_r) / max(1, len(tokens_q))
    if overlap >= 0.6:
        return 5
    if overlap >= 0.4:
        return 4
    if overlap >= 0.25:
        return 3
    if overlap >= 0.1:
        return 2
    return 1


# 工具1：Rewrite
@mcp.tool()
def rewrite(query: str) -> dict:
    """
    对用户 query 进行改写，返回优化后的 query。

    Args:
        query: 用户原始查询
        
    Returns:
        dict: 优化后的 query
    
    Examples:
        >>> rewrite("什么是Python？")
        {"rewritten_query": "拓展相关主题: 什么是Python？"}
    """
    template = random.choice(prompt_pool)
    rewritten = template.format(query=query)
    return {"rewritten_query": rewritten}


# 工具2：Feedback（内部自动打分：LiteLLM 优先，失败回退启发式）
@mcp.tool()
async def feedback(original: str, rewritten: str, results: str, user_comment: Optional[str] = None) -> dict:
    """
    对一次改写结果进行反馈，MCP 内部自动调用 LLM 打分。
    打分标准：结果是否与用户 query 相关（1-5 分）。

    Args:
        original: 用户原始查询
        rewritten: 改写后的查询
        results: 搜索结果
        user_comment: 用户的自然语言反馈，例如 "这个答案很有用，但有点太复杂"，可为空
        
    Returns:
        dict: 打分结果
    
    Examples:
        >>> feedback("什么是Python？", "拓展相关主题: 什么是Python？", "Python 是一种高级编程语言。")
        {"score": 5，"current_pool": [0:"精确搜索: {query}". 1:"拓展相关主题: {query}",2:"用学术角度解释: {query}"]}
    """
    prompt = f"""
        用户原始查询: {original}
        改写后的查询: {rewritten}
        搜索结果: {results[:500]}
        用户自然语言反馈: {user_comment or "（无反馈）"}

        请你评价这个搜索结果是否与原始查询相关。
        只给出一个 1-5 的整数分数，其中 1 表示完全不相关，5 表示高度相关。
        答案只输出数字。
        """

    score = await _score_with_litellm(prompt)
    if score is None:
        score = _score_with_heuristic(original, rewritten, results)

    # 自进化策略：如果分数高，则保留模板
    if score >= 4:
        new_template = rewritten.replace(original, "{query}")
        if new_template not in prompt_pool:
            prompt_pool.append(new_template)

    return {
        "score": score,
        "current_pool": prompt_pool
    }


# 运行 MCP Server
if __name__ == "__main__":
    mcp.run()


