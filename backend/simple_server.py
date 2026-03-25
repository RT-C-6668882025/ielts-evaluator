# 简化的后端服务 - 无需外部依赖
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "ok", "service": "IELTS Evaluator API (Simple Mode)", "message": "后端运行中，但AI功能需要安装依赖"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/models':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            models = [
                {"id": "deepseek-chat", "name": "DeepSeek Chat (V3)", "provider": "deepseek"},
                {"id": "deepseek-reasoner", "name": "DeepSeek R1 (Reasoner)", "provider": "deepseek"},
            ]
            self.wfile.write(json.dumps({"models": models}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/test-api':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": "⚠️ 依赖未安装，无法测试API连接",
                "details": {
                    "suggestion": "请在本地终端手动运行：pip install fastapi uvicorn httpx pydantic\n然后启动：python backend/main.py"
                },
                "timestamp": "2024-01-01T00:00:00"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/evaluate':
            self.send_response(503)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "detail": "AI评估功能需要安装依赖。请运行：pip install fastapi uvicorn httpx pydantic"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), SimpleHandler)
    print("🚀 简化版后端服务启动成功！")
    print("📍 地址: http://localhost:8000")
    print("⚠️  注意：这是简化模式，AI功能需要安装依赖")
    print("💡 安装命令: pip install fastapi uvicorn httpx pydantic")
    server.serve_forever()
