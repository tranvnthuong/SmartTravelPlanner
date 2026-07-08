Cách làm chuẩn:

### 1. Cấu trúc project

```txt
my-app/
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### 2. `README.md`

```md
---
license: mit
title: My Python App
sdk: docker
---
```

Hugging Face Spaces dùng `sdk: docker`, port mặc định thường là `7860`. Có thể đổi bằng `app_port`. ([Hugging Face][1])

### 3. Ví dụ app FastAPI

`app.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello from Hugging Face Space"}
```

`requirements.txt`

```txt
fastapi
uvicorn[standard]
```

### 4. `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

### 5. Deploy lên Hugging Face

Tạo Space mới, chọn **SDK = Docker**, rồi push code:

```bash
git init
git remote add origin https://huggingface.co/spaces/USERNAME/SPACE_NAME
git add .
git commit -m "initial deploy"
git push origin main
```

Hugging Face Spaces là Git repo; khi bạn push code, Space sẽ tự build Docker image và chạy app. ([Hugging Face][2])

### Lỗi hay gặp

App phải listen trên:

```txt
0.0.0.0:7860
```

Không dùng:

```txt
127.0.0.1
localhost
```

Và `Dockerfile` phải nằm ở root repo, tên đúng là:

```txt
Dockerfile
```