workers = 2
bind = "0.0.0.0:10000"
timeout = 300  # 增加到5分钟
worker_class = 'sync'
max_requests = 1000
max_requests_jitter = 50
preload_app = True
keepalive = 120 