# IELTS Evaluator - 雅思评估助手

一个基于 DeepSeek AI 的雅思写作和口语评估工具，提供专业的评分和详细的改进建议。

## 功能特性

- ✍️ **写作评估 (Writing)**
  - Task Achievement/Response (TR)
  - Coherence & Cohesion (CC)
  - Lexical Resource (LR)
  - Grammatical Range & Accuracy (GRA)

- 🎤 **口语评估 (Speaking)**
  - Fluency & Coherence (FC)
  - Lexical Resource (LR)
  - Grammatical Range & Accuracy (GRA)
  - Pronunciation (P)

- 📊 **详细反馈**
  - 四项评分标准单独打分
  - 致命错误分析
  - 改进建议
  - Band 8.0 版本示范
  - 总体评价

## 项目结构

```
ielts-evaluator/
├── backend/
│   ├── main.py           # FastAPI 后端服务
│   └── requirements.txt  # Python 依赖
├── frontend/
│   └── index.html        # 前端界面
└── README.md             # 项目说明
```

## 快速开始

### 1. 配置 DeepSeek API

设置环境变量：

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-api-key-here"

# Windows CMD
set DEEPSEEK_API_KEY=your-api-key-here

# Linux/Mac
export DEEPSEEK_API_KEY=your-api-key-here
```

### 2. 启动后端服务

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动。

### 3. 使用前端界面

直接在浏览器中打开 `frontend/index.html` 文件，或使用简单的 HTTP 服务器：

```bash
cd frontend

# Python 3
python -m http.server 3000

# 或使用 Node.js
npx serve .
```

然后访问 `http://localhost:3000`。

## API 接口

### POST /evaluate

评估雅思写作或口语。

**请求体：**

```json
{
  "mode": "writing" | "speaking",
  "task_prompt": "题目（可选）",
  "response": "考生的回答内容"
}
```

**响应：**

```json
{
  "result": "评估结果文本（Markdown 格式）"
}
```

## 使用说明

1. 选择评估模式（Writing 或 Speaking）
2. 输入题目（可选，但建议提供以获得更准确的评估）
3. 粘贴你的作文或口语转录文本
4. 点击 "Evaluate My Response" 按钮
5. 查看详细的评估结果和改进建议

## 技术栈

- **后端**: FastAPI, Python 3.8+
- **前端**: HTML5, CSS3, Vanilla JavaScript
- **AI 模型**: DeepSeek Chat API

## 注意事项

- 需要有效的 DeepSeek API Key
- 评估结果基于 AI 模型，仅供参考
- 建议结合官方评分标准使用

## License

MIT License
