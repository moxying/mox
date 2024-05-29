# 一、启动 Launch

- App 更新
- Git 更新
- Python 环境更新
- Agent 更新

# 二、创作 Create

## 2.1 配置

（1）比例 配置

- 16:9（1024x576）
- 3:2（1024x682）
- 4:3（1024x768）
- 1:1（1024x1024）

（2）精细度 配置

提示信息：数值越大生成的效果越好，耗时会更久。
范围：4~20；默认 5

（3）参考图 配置

参考方式：

- 人物长相
- 人物姿势
- 主要物体
- 边缘轮廓
- 构图景深
- 图片风格

## 2.2 任务发起

- 提示词
- 给个灵感

## 2.3 任务列表

任务：

- 任务提示词
- 任务 tag 列表
- 任务参考图片缩略图
- 任务支持操作：
  - 重新生成
  - 更多
    - 复制提示词

图片：

- 图片支持操作：细微变化、强烈变化
- 图片右键菜单

整体：

- 刷新

# 三、我的 Personal

## 3.1 图片列表

- 图片右键菜单
- 收藏夹
  - 全部图片
  - 创建收藏夹
  - 修改收藏夹
- 框选：添加到收藏夹
- 拖动图片到收藏夹
- 按提示词搜索过滤列表

# 四、图片详情 ImageDetail

图片详细信息：

- tag 列表
- 提示词
- 任务参考图片缩略图+参考方式+参考配置
- 图片右键菜单（同上）

图生图操作：

- 变化：
  - 细微（basic_img2img,denoise=0.2）
  - 强烈（basic_img2img,denoise=0.8）;
- 高清
  - 直接（simple_upscale）
  - 创意（pixel_upscale,denoise=0.48）;
- 调整：
  - 局部重绘（basic_inpainting）
  - 重新生成（basic_txt2img）
- 扩图：
  - 1.5x（basic_outpainting）
  - 2x（basic_outpainting）
  - 上（basic_outpainting）
  - 下（basic_outpainting）
  - 左（basic_outpainting）
  - 右（basic_outpainting）
- 参考：
  - 人物长相（basic_instantid,extra node + extra model）
  - 人物姿势（controlnet_openpose,extra node + extra model）
  - 边缘轮廓 TODO
  - 构图景深 TODO
  - 图片风格 TODO

# 五、图片右键菜单

- 图片右键菜单：
  - 分类一
    - 复制图片
    - 在文件夹中显示
    - 添加到收藏夹/从收藏夹移除
  - 分类二
    - 重新生成
    - 调整比例
    - 变化：细微、强烈、局部重绘
    - 高清：直接、创意
    - 作为参考图片

# 六、引擎 Engine

## 6.1 绘图引擎 Draw Engine

## 6.2 插件 Plugin

# 七、配置 Config
