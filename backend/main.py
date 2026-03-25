"""
雅思评估助手 - FastAPI 后端服务
IELTS Evaluator Backend Service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import httpx
import json
from typing import Literal, Optional, Dict, Any
from datetime import datetime

app = FastAPI(title="IELTS Evaluator API", version="1.1.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器 - 确保错误返回统一格式
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """处理请求参数验证错误"""
    errors = []
    for error in exc.errors():
        errors.append(f"{error['loc'][-1]}: {error['msg']}")
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation error: " + "; ".join(errors),
            "details": {"errors": errors},
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """处理所有其他异常"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"Internal server error: {str(exc)}",
            "details": {"error_type": type(exc).__name__},
            "timestamp": datetime.now().isoformat()
        }
    )

# 支持的模型列表
SUPPORTED_MODELS = {
    # DeepSeek 模型
    "deepseek-chat": {"provider": "deepseek", "name": "DeepSeek Chat (V3)", "max_tokens": 8192},
    "deepseek-coder": {"provider": "deepseek", "name": "DeepSeek Coder", "max_tokens": 8192},
    "deepseek-reasoner": {"provider": "deepseek", "name": "DeepSeek R1 (Reasoner)", "max_tokens": 8192},
    # OpenAI 模型
    "gpt-4": {"provider": "openai", "name": "GPT-4", "max_tokens": 8192},
    "gpt-4-turbo": {"provider": "openai", "name": "GPT-4 Turbo", "max_tokens": 8192},
    "gpt-4o": {"provider": "openai", "name": "GPT-4o", "max_tokens": 8192},
    "gpt-4o-mini": {"provider": "openai", "name": "GPT-4o Mini", "max_tokens": 8192},
    "gpt-3.5-turbo": {"provider": "openai", "name": "GPT-3.5 Turbo", "max_tokens": 4096},
    # Anthropic 模型
    "claude-3-opus": {"provider": "anthropic", "name": "Claude 3 Opus", "max_tokens": 4096},
    "claude-3-sonnet": {"provider": "anthropic", "name": "Claude 3 Sonnet", "max_tokens": 4096},
    "claude-3-haiku": {"provider": "anthropic", "name": "Claude 3 Haiku", "max_tokens": 4096},
    "claude-3-5-sonnet": {"provider": "anthropic", "name": "Claude 3.5 Sonnet", "max_tokens": 4096},
    # Google Gemini 模型
    "gemini-2.5-pro": {"provider": "google", "name": "Gemini 2.5 Pro", "max_tokens": 8192},
    "gemini-2.5-flash": {"provider": "google", "name": "Gemini 2.5 Flash", "max_tokens": 8192},
    "gemini-2.0-flash": {"provider": "google", "name": "Gemini 2.0 Flash", "max_tokens": 8192},
    "gemini-2.0-flash-lite": {"provider": "google", "name": "Gemini 2.0 Flash Lite", "max_tokens": 8192},
    "gemini-1.5-pro": {"provider": "google", "name": "Gemini 1.5 Pro", "max_tokens": 8192},
    "gemini-1.5-flash": {"provider": "google", "name": "Gemini 1.5 Flash", "max_tokens": 8192},
}

# 默认 API URL 映射
DEFAULT_API_URLS = {
    "deepseek": "https://api.deepseek.com/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "google": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
}

# Writing 评估系统提示词（改版）
WRITING_SYSTEM_PROMPT = """You are a brutally honest IELTS examiner. Your job is to expose every flaw with surgical precision.

Scoring criteria (strictly applied):
- TR: Task Achievement — position clear and fully developed?
- CC: Coherence & Cohesion — logical flow, paragraph structure?
- LR: Lexical Resource — vocabulary range, precision, collocation?
- GRA: Grammatical Range & Accuracy — sentence variety, error frequency?

OUTPUT FORMAT — follow exactly:

## 分项评分
TR: X/9
CC: X/9
LR: X/9
GRA: X/9
**综合分: X/9**

## 致命错误
每个错误按以下格式列出：
❌ [错误类型]：原文引用 "[exact quote]"
→ 为什么这个写法卡在7分以下：[中文解释，说清楚考官看到这句话的判断]
→ REWRITE: "[corrected version in English]"

没有致命错误则写：本次无致命错误。

## 扣分项（非致命但限制评分）
列出2-4个具体弱点，说明它把分数压在哪里。
禁止泛泛而谈，比如"词汇需要提高"这种废话不要写。
要具体到：哪个词用错了、哪个句子结构重复、哪个逻辑跳跃——直接指出来。

## Band 8.0 示范
把开头段和一个正文句子改写成8.0水准。改写必须全英文，不加任何中文夹杂。

改写之后单独用中文解释：
- 哪个词替换了哪个词，connotation上的差距是什么
- 哪个句式做了什么改动，为什么这样更自然
- 论证结构上做了什么，为什么考官会给更高分
解释要具体到词级别，不要只说"更高级"或"更流畅"。

## 核心诊断
一段话，不准说废话。
不要谈语法小错——指出让这篇文章停在当前分数的最根本问题是什么，是论证逻辑、还是思维深度、还是语言习惯？"""

# Speaking 评估系统提示词（改版）
SPEAKING_SYSTEM_PROMPT = """You are a brutally honest IELTS speaking examiner. The candidate submitted a written transcript of their spoken answer. Evaluate as if delivered aloud.

Scoring criteria:
- FC: Fluency & Coherence
- LR: Lexical Resource
- GRA: Grammatical Range & Accuracy
- P: Pronunciation (estimated from text)

OUTPUT FORMAT — follow exactly:

## 分项评分
FC: X/9
LR: X/9
GRA: X/9
P: X/9（基于文本估算）
**综合分: X/9**

## 致命错误
❌ [错误类型]：原文引用 "[exact quote]"
→ 为什么母语考官听到这句话会扣分：[中文解释]
→ NATURAL VERSION: "[how a fluent speaker would actually say this]"

## 流利度杀手
列出具体短语或句式，说明它们在口语中会造成什么问题。
直接引用原文，用中文解释问题在哪。

## 发音风险词
从原文挑3-5个中国英语学习者高频念错的词或短语。
用中文标注：错误读法通常是什么，正确重音和音节在哪。

## Band 8.0 示范
把其中一段改写成8.0口语水准，至少4句。改写必须全英文，不加任何中文夹杂。

改写之后单独用中文解释：
- 原版用了什么表达，改版换成了什么，为什么改版更像母语者会说的话
- 原版的衔接逻辑和改版的衔接逻辑有什么差别
- 指出原版里一个具体的语言习惯，说清楚为什么这个习惯会被考官识别为中式英语
解释要落到具体的词或短语，不要泛泛说"更自然"。

## 核心诊断
一段话。指出这个回答里最暴露非母语身份的特征是什么——考官在前10秒就感知到的那个东西。"""

# 短输入扩写诊断提示词
SHORT_INPUT_PROMPT = """The candidate has submitted a short English text (under 150 words). Do NOT score it. Your job is to dissect every sentence and show how to expand it into band 8.0 quality using embedded clauses and structural layering.

For each sentence in the input, do the following:

## 句子诊断

原句：[quote the sentence exactly]

**潜在问题（中文）**
- 直接问题：语法、用词、搭配上的硬错误，直接指出
- 语言习惯问题：这句话暴露了什么中式英语思维定势——不是错的，但母语者不会这么说
- 信息密度问题：这句话在逻辑上跳过了什么，读者需要自己补什么

**结构扩写示范（全英文）**

从原句出发，用以下维度逐层嵌套扩写：
- WHO：主体是谁，有什么限定（定语从句 / 介词短语修饰）
- WHAT：动作是什么，动词精不精准，有没有更准确的动词
- WHEN：时间条件，用时间状语从句或分词结构嵌入
- WHERE：地点或范围限定，用介词短语嵌入
- HOW：方式，用 by doing / through / via 等结构嵌入
- WHY / BECAUSE：原因或结果，用 given that / owing to / which in turn 等嵌入
- CONDITION：前提或假设，用 provided that / in the absence of 等嵌入

不要一次全部塞进去。给出3个版本，每个版本都要上英下中（英文句子+中文翻译+结构拆解）：

**版本1：加1-2层，自然流畅**
英文：
[英文句子]

中文翻译：
[整句的中文意思]

结构拆解：
- 第1层加了什么，挂在哪个词上
- 第2层加了什么（如有）
- 整体效果：为什么这样更流畅

**版本2：加3-4层，适合写作正文句**
英文：
[英文句子]

中文翻译：
[整句的中文意思]

结构拆解：
- 第1层：加了什么，挂在哪个词上，起什么作用
- 第2层：加了什么，挂在哪个词上，起什么作用
- 第3层：加了什么，挂在哪个词上，起什么作用
- 第4层（如有）：加了什么
- 去掉某层会损失什么信息

**版本3：加5层以上，展示极限密度**
英文：
[英文句子]

中文翻译：
[整句的中文意思]

结构拆解：
- 逐层列出每个嵌入结构
- 说明：什么时候适合用这种长度
- 警告：过度使用的风险

---

对input里所有句子做完以上分析后：

## 扩写路线图

用中文说明：
- 这段文字如果要扩写到150词，最应该往哪个方向加信息——是补逻辑、补细节、补背景、还是补反驳
- 给出一个完整的扩写版本（全英文，150词以上），展示所有句子整合之后的自然流动
- 扩写版本之后用中文标注：哪些地方用了从句嵌套，嵌套的锚点是什么词"""


class ApiConfig(BaseModel):
    """API配置模型"""
    api_url: Optional[str] = Field(default=None, description="API端点URL（可选，留空则自动根据模型选择）")
    api_key: str = Field(description="API认证密钥")
    model: str = Field(default="deepseek-chat", description="模型名称")
    custom_model: Optional[str] = Field(default=None, description="自定义模型名称")


class EvaluateRequest(BaseModel):
    """评估请求模型"""
    mode: Literal["writing", "speaking", "expansion"]
    task_prompt: str = ""
    response: str
    word_count: int = 0
    api_config: Optional[ApiConfig] = None


class EvaluateResponse(BaseModel):
    """评估响应模型"""
    result: str


class TestApiRequest(BaseModel):
    """测试API连接请求"""
    api_url: Optional[str] = None
    api_key: str
    model: str


class TestApiResponse(BaseModel):
    """API测试结果响应"""
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class ModelInfo(BaseModel):
    """模型信息"""
    id: str
    name: str
    provider: str
    max_tokens: int


class ModelsResponse(BaseModel):
    """可用模型列表响应"""
    models: list[ModelInfo]


def get_model_info(model_id: str) -> Dict[str, Any]:
    """获取模型信息"""
    return SUPPORTED_MODELS.get(model_id, {
        "provider": "unknown",
        "name": model_id,
        "max_tokens": 4096
    })


def build_api_request_body(model: str, messages: list, max_tokens: int = 100) -> Dict[str, Any]:
    """构建API请求体，根据不同提供商调整格式"""
    model_info = get_model_info(model)
    provider = model_info.get("provider", "unknown")
    
    # 基础请求体
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": min(max_tokens, model_info.get("max_tokens", 4096)),
    }
    
    # 根据提供商添加特定参数
    if provider == "anthropic":
        # Anthropic Claude API 格式
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": min(max_tokens, model_info.get("max_tokens", 4096)),
        }
    elif provider == "openai":
        # OpenAI API 格式
        body["temperature"] = 0.7
    elif provider == "deepseek":
        # DeepSeek API 格式
        body["temperature"] = 0.7
        # DeepSeek R1 (reasoner) 模型特殊处理
        if "reasoner" in model or "r1" in model.lower():
            body["max_tokens"] = min(max_tokens, 8192)
    
    return body


def build_api_headers(api_key: str, provider: str = "deepseek") -> Dict[str, str]:
    """构建API请求头"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Anthropic 需要特殊的 header
    if provider == "anthropic":
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    # Google Gemini 使用 API key 作为查询参数，不需要在 header 中设置
    elif provider == "google":
        headers = {
            "Content-Type": "application/json"
        }
    
    return headers


@app.get("/")
async def root():
    """根路径 - 服务状态检查"""
    return {
        "status": "ok", 
        "service": "IELTS Evaluator API",
        "version": "1.1.0",
        "supported_models": len(SUPPORTED_MODELS)
    }


@app.get("/models", response_model=ModelsResponse)
async def get_models():
    """获取支持的模型列表"""
    models = [
        ModelInfo(
            id=model_id,
            name=info["name"],
            provider=info["provider"],
            max_tokens=info["max_tokens"]
        )
        for model_id, info in SUPPORTED_MODELS.items()
    ]
    return ModelsResponse(models=models)


@app.post("/test-api", response_model=TestApiResponse)
async def test_api_connection(request: TestApiRequest):
    """
    测试API连接是否可用
    
    Args:
        request: 包含API配置信息的请求
        
    Returns:
        详细的连接测试结果
    """
    timestamp = datetime.now().isoformat()
    
    try:
        # 获取模型信息
        model_info = get_model_info(request.model)
        provider = model_info.get("provider", "unknown")
        
        # 确定 API URL
        if request.api_url:
            api_url = request.api_url
        else:
            # 根据 provider 自动选择默认 URL
            if provider == "google":
                api_url = DEFAULT_API_URLS["google"].format(model=request.model)
            else:
                api_url = DEFAULT_API_URLS.get(provider, DEFAULT_API_URLS["deepseek"])
        
        # 构建请求头和请求体
        headers = build_api_headers(request.api_key, provider)
        
        # Google Gemini API 特殊处理
        if provider == "google":
            body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "Hello, this is a connection test."}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 10,
                    "temperature": 0.7
                }
            }
            # Gemini API key 作为查询参数
            if "?" in api_url:
                api_url = f"{api_url}&key={request.api_key}"
            else:
                api_url = f"{api_url}?key={request.api_key}"
        else:
            messages = [{"role": "user", "content": "Hello, this is a connection test."}]
            body = build_api_request_body(request.model, messages, max_tokens=10)
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # 发送测试请求
            test_response = await client.post(
                api_url,
                headers=headers,
                json=body
            )
            
            response_data = {
                "status_code": test_response.status_code,
                "headers": dict(test_response.headers),
            }
            
            # 尝试解析响应体
            try:
                response_json = test_response.json()
                response_data["response_preview"] = str(response_json)[:200]
            except:
                response_data["response_preview"] = test_response.text[:200]
            
            # 处理不同状态码
            if test_response.status_code == 200:
                return TestApiResponse(
                    status="success",
                    message=f"✅ API connection successful! Model '{model_info['name']}' is ready.",
                    details={
                        "provider": provider,
                        "model": request.model,
                        "model_name": model_info["name"],
                        "response": response_data
                    },
                    timestamp=timestamp
                )
            elif test_response.status_code == 401:
                return TestApiResponse(
                    status="error",
                    message="❌ Authentication failed. Please check your API key.",
                    details={
                        "error_type": "authentication",
                        "status_code": 401,
                        "suggestion": "Verify that your API key is correct and has not expired."
                    },
                    timestamp=timestamp
                )
            elif test_response.status_code == 404:
                return TestApiResponse(
                    status="error",
                    message="❌ API endpoint not found. Please check the URL.",
                    details={
                        "error_type": "not_found",
                        "status_code": 404,
                        "suggestion": "Verify the API URL is correct. Common URLs:\n- DeepSeek: https://api.deepseek.com/chat/completions\n- OpenAI: https://api.openai.com/v1/chat/completions\n- Anthropic: https://api.anthropic.com/v1/messages"
                    },
                    timestamp=timestamp
                )
            elif test_response.status_code == 429:
                return TestApiResponse(
                    status="error",
                    message="❌ Rate limit exceeded. Too many requests.",
                    details={
                        "error_type": "rate_limit",
                        "status_code": 429,
                        "suggestion": "Please wait a moment before trying again."
                    },
                    timestamp=timestamp
                )
            elif test_response.status_code >= 500:
                return TestApiResponse(
                    status="error",
                    message="❌ AI service error. The API server encountered an error.",
                    details={
                        "error_type": "server_error",
                        "status_code": test_response.status_code,
                        "suggestion": "This is a temporary issue with the AI service. Please try again later."
                    },
                    timestamp=timestamp
                )
            else:
                return TestApiResponse(
                    status="error",
                    message=f"❌ API error (HTTP {test_response.status_code})",
                    details={
                        "error_type": "api_error",
                        "status_code": test_response.status_code,
                        "response": response_data,
                        "suggestion": "Please check your API configuration and try again."
                    },
                    timestamp=timestamp
                )
                
    except httpx.TimeoutException:
        return TestApiResponse(
            status="error",
            message="❌ Connection timeout. The API server took too long to respond.",
            details={
                "error_type": "timeout",
                "suggestion": "Check your network connection. If using a proxy/VPN, ensure it's working properly."
            },
            timestamp=timestamp
        )
    except httpx.ConnectError as e:
        error_msg = str(e).lower()
        if "name or service not known" in error_msg or "getaddrinfo failed" in error_msg:
            return TestApiResponse(
                status="error",
                message="❌ DNS resolution failed. Cannot resolve API hostname.",
                details={
                    "error_type": "dns_error",
                    "suggestion": "Check your internet connection and DNS settings. The API URL may be incorrect."
                },
                timestamp=timestamp
            )
        elif "connection refused" in error_msg:
            return TestApiResponse(
                status="error",
                message="❌ Connection refused. The API server refused the connection.",
                details={
                    "error_type": "connection_refused",
                    "suggestion": "The API server may be down or the port may be blocked. Check your firewall settings."
                },
                timestamp=timestamp
            )
        else:
            return TestApiResponse(
                status="error",
                message="❌ Cannot connect to API server.",
                details={
                    "error_type": "connection_error",
                    "error_message": str(e),
                    "suggestion": "Check your network connection and API URL."
                },
                timestamp=timestamp
            )
    except Exception as e:
        return TestApiResponse(
            status="error",
            message=f"❌ Connection test failed: {str(e)}",
            details={
                "error_type": "unknown",
                "error_message": str(e),
                "suggestion": "Please check your configuration and try again."
            },
            timestamp=timestamp
        )


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(request: EvaluateRequest):
    """
    评估雅思写作或口语
    
    Args:
        request: 包含评估模式、题目和考生回答的请求
        
    Returns:
        评估结果文本
    """
    # 获取API配置（优先使用请求中的配置，否则使用环境变量）
    if request.api_config:
        api_key = request.api_config.api_key
        model = request.api_config.custom_model if request.api_config.model == "custom" and request.api_config.custom_model else request.api_config.model
        
        # 获取模型信息
        model_info = get_model_info(model)
        provider = model_info.get("provider", "unknown")
        
        # 如果提供了 api_url 则使用，否则根据模型自动选择
        if request.api_config.api_url:
            api_url = request.api_config.api_url
        else:
            # 根据 provider 自动选择默认 URL
            if provider == "google":
                api_url = DEFAULT_API_URLS["google"].format(model=model)
            else:
                api_url = DEFAULT_API_URLS.get(provider, DEFAULT_API_URLS["deepseek"])
    else:
        # 使用环境变量作为后备
        api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        model = "deepseek-chat"
        model_info = get_model_info(model)
        provider = model_info.get("provider", "unknown")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured. Please set it in Settings.")
    
    # 选择对应的系统提示词
    # 如果字数少于150且是写作模式，使用扩写提示词
    if request.mode == "expansion" or (request.mode == "writing" and request.word_count > 0 and request.word_count < 150):
        system_prompt = SHORT_INPUT_PROMPT
        user_message = f"""CANDIDATE'S SHORT RESPONSE ({request.word_count} words):
{request.response}"""
    elif request.mode == "writing":
        system_prompt = WRITING_SYSTEM_PROMPT
        user_message = f"""TASK PROMPT: {request.task_prompt or "Not provided"}

CANDIDATE'S RESPONSE:
{request.response}"""
    else:  # speaking
        system_prompt = SPEAKING_SYSTEM_PROMPT
        user_message = f"""TASK PROMPT: {request.task_prompt or "Not provided"}

CANDIDATE'S RESPONSE:
{request.response}"""
    
    # 构建请求头和请求体
    headers = build_api_headers(api_key, provider)
    
    # Google Gemini API 特殊处理
    if provider == "google":
        # Gemini 使用 contents 格式，且 system prompt 需要特殊处理
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{user_message}"}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": min(8000, model_info.get("max_tokens", 8192)),
                "temperature": 0.7
            }
        }
        # Gemini API key 作为查询参数
        if "?" in api_url:
            api_url = f"{api_url}&key={api_key}"
        else:
            api_url = f"{api_url}?key={api_key}"
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        body = build_api_request_body(model, messages, max_tokens=4000)
    
    # 调用 AI API
    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            api_response = await client.post(
                api_url,
                headers=headers,
                json=body
            )
            
            if api_response.status_code != 200:
                error_detail = api_response.text
                if api_response.status_code == 401:
                    error_detail = "Invalid API key. Please check your API configuration."
                elif api_response.status_code == 429:
                    error_detail = "Rate limit exceeded. Please try again later."
                elif api_response.status_code == 500:
                    error_detail = "AI service error. Please try again later."
                elif api_response.status_code == 404:
                    error_detail = "Model not found. Please check if the model name is correct."
                
                raise HTTPException(
                    status_code=api_response.status_code,
                    detail=f"API error: {error_detail}"
                )
            
            result = api_response.json()
            
            # 处理不同提供商的响应格式
            if provider == "anthropic":
                evaluation_text = result["content"][0]["text"]
            elif provider == "google":
                # Gemini API 响应格式
                evaluation_text = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                evaluation_text = result["choices"][0]["message"]["content"]
            
            return EvaluateResponse(result=evaluation_text)
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to AI API timed out. Please try again.")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to AI API. Please check your network and API URL.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
