## TODO

以下为计划中的特性及优化方向

### 支持更多站点


### 加密字体识别优化 (基于 PaddleOCR)

为了解决起点小说网站中使用 "加密字体" 防止爬虫的问题

- [x] 收集常见类似于加密字体的样本图像
- [x] 标注训练集并转换为 PaddleOCR 可用格式 (约 2 万张样本图片)
- [x] 使用 PaddleOCR 进行模型微调训练
- [x] 加入验证集用于训练过程监控与调优 (7 万张样本, 覆盖 2.2k 个不重复字符)
- [x] 替换默认模型以提升整体识别效果 (目前准确率大概 $99.9\%$)
- [ ] 进一步优化模型 (包括轻量化部署 | 识别速度提升 | 误识别字符修正等)
