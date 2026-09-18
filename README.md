# Desk CN（升降桌 / 床 / 窗帘 Home Assistant 集成）

通过 REST 轮询对接中国区 AWS IoT Core 后端，把智能升降桌、床、窗帘接入 Home Assistant。

## 安装（HACS 自定义库）

1. 在 HACS 里点右上角 `⋮` → **自定义存储库（Custom repositories）**
2. 类别选 **Integration**，地址填 `https://github.com/liulijun2019/ha-desk-cn`
3. 添加后，在 HACS 里搜索 **Desk 升降桌** → 下载安装
4. 重启 Home Assistant

> 也可手动安装：把本仓库 `custom_components/desk_cn/` 目录复制到 HA 的 `config/custom_components/desk_cn/`。

## 配置

安装后在「设置 → 设备与服务 → 添加集成」搜 **Desk 升降桌**，填写：

| 字段 | 说明 |
|---|---|
| `base_url` | 后端 HA API 地址，如 `https://xxx.execute-api.cn-north-1.amazonaws.com.cn/prod` |
| `api_key` | API Gateway 的 API Key（`x-api-key`） |
| `account` | 绑定账号 |
| `password` | 绑定密码 |
| `poll_interval` | 轮询间隔（秒），默认 10 |

## 设备映射

| 设备类型 | HA 实体 |
|---|---|
| desk / curtain | `cover`（升降/位置/停止） |
| bed | `number` × 2（head / foot 角度） |

## 后端要求

需要先部署好对应的后端服务（API Gateway + Lambda + DynamoDB）。详见后端项目文档。

## License

MIT
