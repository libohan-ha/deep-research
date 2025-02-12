from flask import Flask, render_template, request, jsonify
import requests
import json
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# 用于存储最后一次请求的时间
last_request_time = None
MIN_REQUEST_INTERVAL = 5  # 最小请求间隔（秒）

def run_knowledge_summary(concept):
    global last_request_time
    
    # 检查请求间隔
    current_time = datetime.now()
    if last_request_time is not None:
        time_diff = (current_time - last_request_time).total_seconds()
        if time_diff < MIN_REQUEST_INTERVAL:
            return {"success": False, "error": f"请求过于频繁，请等待{int(MIN_REQUEST_INTERVAL - time_diff)}秒后再试"}
    
    url = "https://api.coze.cn/v1/workflow/run"
    
    headers = {
        'Authorization': 'Bearer pat_v7TVyTawPSnSBkqW1WARKkbn9D7cYU5PK5HAlEdGGsH6pXMfrEz9HdMdicK33cq9',
        'Content-Type': 'application/json'
    }
    
    data = {
        "workflow_id": "7470519122577588260",
        "parameters": {
            "input": concept
        }
    }
    
    # 重试机制
    max_retries = 3
    retry_delay = 2  # 重试间隔（秒）
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result['code'] == 0:
                last_request_time = current_time  # 更新最后请求时间
                output_data = json.loads(result['data'])
                return {"success": True, "data": output_data['data']}
            else:
                # 如果是限速错误，增加重试延迟
                if "frequency exceeds" in result.get('msg', '').lower():
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                return {"success": False, "error": result['msg']}
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "请求失败，请稍后重试"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    concept = request.json.get('concept')
    if not concept:
        return jsonify({"success": False, "error": "请输入要分析的概念"})
    
    result = run_knowledge_summary(concept)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 