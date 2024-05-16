# 创作

## 获取随机提示词

请求：

```http
GET /api/image/prompt/random HTTP/1.1
Host: 127.0.0.1:7800
```

响应：

```json
{
  "code": 0,
  "data": "one man"
}
```

## 文生图

请求：

```http
POST /api/image/txt2img HTTP/1.1
Host: 127.0.0.1:7800
Content-Type: application/json

{
    "origin_prompt": "一个男人",
    "ckpt_name": "juggernautXL_v9Rdphoto2Lightning.safetensors",
    "negative_prompt": "nsfw",                                     // 可选
    "seed": 0,                                                     // 可选
    "steps": 5,                                                    // 可选
    "cfg": 2.0,                                                    // 可选
    "sampler_name": "dpmpp_sde",                                   // 可选
    "scheduler": "scheduler",                                      // 可选
    "denoise": 1.0,                                                // 可选
    "batch_size": 4,                                               // 可选
    "width": 1024,                                                 // 可选
    "height": 1024                                                 // 可选

}
```

响应：

```json
{
    "code": 0,
    "data" {
        "task_uuid": "abcerf"
    }
}
```

# 配置
