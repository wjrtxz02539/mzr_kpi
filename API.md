# API接口文档

## 动态接口

### 动态类型

* 1: 转发动态
* 2: 普通动态1
* 4: 普通动态2
* 8: 视频动态
* 64: 专栏动态
* 2048: 话题动态

### 数据结构

```json5
{
    "dynamic_type": 2,
    // 动态类型
    "orig_dy_id": 0,
    // 转发的原动态ID
    "orig_type": 0,
    // 转发的原动态类型
    "video_id": null,
    // 视频BID
    "dynamic_id": 533172653108740435,
    // 动态ID
    "user_id": 401742377,
    // 用户ID
    "report_id": 137965321,
    // 专栏ID？若动态类型为 64 时，该字段为专栏ID可跳转
    "target_url": null,
    // 动态话题跳转URL
    "thread_id": 137965321,
    // 评论版面ID
    "description": "​互动抽奖 #原神# #声优小剧场# #璃月雅集#\n\n《原神》声优小剧场——「璃月雅集」第二期  现已发布。\n\n初夏时节，仙人与旅者齐聚「璃月雅集」，清茶一盏，淡话闲事。\n在蝉鸣四起之前，新的逸闻又逐渐传播开来… \n\n关注@原神 并转发，我们将随机抽出10位旅行者赠送【《原神》Q版人物金属挂件（样式随机） 】1份。 ",
    "time": "2021-06-06 11:02:12",
    "view": 761422,
    "like": 12941,
    "run_records": [
        {
            "runtime_id": "60bcc9cb7ba97a271992150a",
            "total": 1938,
            "progress": 0,
            "start_time": "2021-06-06 13:12:43",
            "end_time": "2021-06-06 13:13:07"
        }
    ]
}
```

### 分页接口

`GET /api/dynamic`

#### 参数

|  字段   | 类型  | 描述 | 范例 |
|  ----  | ----  | ---- | ---- |
| dynamic_type  | int | 动态类型 | 533172653108740435 |
| user_id  | int | 用户id | 401742377 |
| thread_id  | int | 版面id | 137965321 |
| description  | str | 动态内容 | 崩坏3 |
| order_by  | str | 排序 | -time |
| start_time  | str | 起始时间 | 2021-06-06 20:00:00 |
| end_time  | str | 截止时间 | 2021-06-06 20:00:00 |
| size  | int | 分页大小 | 10 |
| start  | int | 分页起始 | 0 |

#### 返回值

```json5
{
    "data": [
        // 具体动态数据结构
    ],
    "pagination": {
        "total": 283,
        "start": 0,
        "size": 1
    },
    "meta": {}
}
```

### 详情接口

`GET /api/dynamic/<string:dynamic_id>`

* dynamic_id: 动态ID

#### 返回值

```json5
{
    // 具体动态数据结构
}
```

## 评论接口

### 数据结构

```json5
{
    "_id": ObjectId(
    "60dfe95088d4c677030fdaf0"
    ),
    "up_id": NumberInt(27534330),
    // 发送动态的UP ID
    "reply_id": NumberLong(4834510342),
    // 评论ID
    "thread_id": NumberInt(631470504),
    // 评论区ID（不同类型动态的评论区ID取值不一样）
    "floor": NumberInt(-1),
    // 楼层，-1意味着楼中楼
    "root": NumberLong(4833536480),
    // 楼中楼的第一个评论ID（若不为楼中楼则空）
    "parent": NumberLong(4833536480),
    // 评论回复的评论ID（若不为楼中楼则空）
    "dialog": NumberLong(4834510342),
    // 对话ID（若不为楼中楼则空）
    "time": ISODate(
    "2021-07-03T12:35:47.000+0000"
    ),
    // 发表时间
    "like": NumberInt(0),
    // 点赞数量
    "user_id": NumberInt(439493649),
    // 发布用户ID
    "user": {
        "user_id": NumberInt(439493649),
        "username": "血泪-S",
        // 发布用户名
        "avatar": "http://i0.hdslb.com/bfs/face/9f8aa281b428526c1cdffd17d1afd55684ef22eb.jpg",
        // 用户头像URL
        "sex": NumberInt(1),
        // 用户性别，0=女，1=男，2=保密
        "sign": "我今天就把话放这了，老子就是这休伯利安的舰长！老子就是要为了这个世界上所有的美好而战！",
        // 用户签名
        "level": NumberInt(4),
        // 用户级别
        "vip": NumberInt(1),
        // 会员类型，1=大会员，2=年度大会员（应该没错吧）
        "sailings": [
            // 粉丝牌
            {
                "name": "崩坏3·天穹流星",
                "is_fan": true,
                "number": NumberInt(39894)
                // 粉丝牌编号
            }
        ],
        "pendants": [
            // 挂件
            "崩坏3·天穹流星"
        ]
    },
    "up": {
        "user_id": NumberInt(27534330),
        "username": "崩坏3第一偶像爱酱"
    },
    "content": "加美颜，谢谢！[脱单doge]",
    // 评论内容
    "device": "",
    // 发布设备，好像只有 空 和 phone
    "replies_count": NumberInt(0),
    // 该评论的回复数量
    "has_folded": false,
    "is_folded": false,
    "invisible": false
}
```

### 分页接口

`GET /api/reply`

#### 参数

|  字段   | 类型  | 描述 | 范例 |
|  ----  | ----  | ---- | ---- |
| user_id  | int | 用户ID | 1036 |
| up_id  | int | UP主ID | 401742377 |
| thread_id  | int | 版面id | 137965321 |
| floor  | int | 楼层 | 37585 |
| content  | str | 内容 | 大本营 |
| device  | str | 设备 | phone |
| has_replies  | bool | 是否有回复 | true |
| dialog  | int | 对话ID | 4452482836 |
| order_by  | str | 排序 | -time |
| start_time  | str | 起始时间 | 2021-06-06 20:00:00 |
| end_time  | str | 截止时间 | 2021-06-06 20:00:00 |
| size  | int | 分页大小 | 10 |
| start  | int | 分页起始 | 0 |

#### 返回值

```json5
{
    "data": [
        // 具体评论数据结构
    ],
    "pagination": {
        "total": 283,
        "start": 0,
        "size": 1
    },
    "meta": {}
}
```

### 详情接口

`GET /api/reply/<string:reply_id>`

* reply_id: 评论ID

#### 返回值

```json5
{
    // 具体评论数据结构
}
```

### 字段聚合接口

`GET /api/reply/tag/<string:field>`

* 请尽量填写 `thread_id` 参数，缩小评论的选取范围，防止请求超时
* field: 想要聚合的字段
  * 用户名聚合：user.name
  * 用户等级聚合：user.level
  * 用户会员聚合：user.vip
  * 用户性别聚合：user.sex
  * 用户挂件聚合：user.pendants
  * 用户粉丝牌聚合：user.sailings.name

#### 参数

**请尽量填写 `thread_id` 参数，缩小评论的选取范围，防止请求超时**

|  字段   | 类型  | 描述 | 范例 |
|  ----  | ----  | ---- | ---- |
| user_id  | int | 用户ID | 1036 |
| up_id  | int | UP主ID | 401742377 |
| thread_id  | int | 版面id | 137965321 |
| floor  | int | 楼层 | 37585 |
| content  | str | 内容 | 大本营 |
| device  | str | 设备 | phone |
| has_replies  | bool | 是否有回复 | true |
| dialog  | int | 对话ID | 4452482836 |
| order_by  | str | 排序 | -time |
| start_time  | str | 起始时间 | 2021-06-06 20:00:00 |
| end_time  | str | 截止时间 | 2021-06-06 20:00:00 |
| size  | int | 分页大小 | 10 |
| start  | int | 分页起始 | 0 |

#### 返回值

```json5
[
    {
        "value": "崩坏3·天穹流星",
        "count": 1902.0
    },
    {
        "value": "原神",
        "count": 751.0
    }
]
```

### 时间线接口

会根据给定的时间范围、用户ID、评论版面ID自动进行时间线上评论数量的统计。 注：该接口在当前数据库宿主机配置下，可能会处理一分钟以上

`GET /api/reply/date_histogram`

#### 参数

|  字段   | 类型  | 描述 | 范例 |
|  ----  | ----  | ---- | ---- |
| user_id  | int | 用户ID | 1036 |
| up_id  | int | UP主ID | 401742377 |
| thread_id  | int | 版面id | 137965321 |
| start_time  | str | 起始时间 | 2021-06-06 20:00:00 |
| end_time  | str | 截止时间 | 2021-06-06 20:00:00 |

#### 返回值

`time`字段内可能的二级字段：

* `year`：必有
* `month`：必有
* `day`：必有
* `hour`：可能有
* `minutes`：可能有
* `seconds`：可能有

```json5
[
    {
        "time": {
            "year": 2021,
            "month": 6,
            "day": 21
        },
        "count": 7378
    },
    {
        "time": {
            "year": 2021,
            "month": 6,
            "day": 3
        },
        "count": 3038
    }
]
```

## 用户接口

### 数据结构

```json5
{
    "user_id": 189,
    "username": "彭薅仁",
    "sex": 1,
    "sign": "我们不用很麻烦很累就可以投币！",
    "level": 6,
    "vip": 2
}
```

### 分页接口

`GET /api/user`

#### 参数

|  字段   | 类型  | 描述 | 范例 |
|  ----  | ----  | ---- | ---- |
| username  | str | 用户名 | 崩坏3 |
| sex  | int | 性别 | 1 |
| sign  | str | 签名 | 签名内容查询 |
| max_level  | int | 最大用户等级 | 5 |
| min_level  | int | 最小用户等级 | 1 |
| vip  | int | 会员 | 2 |
| order_by  | str | 排序 | -time |
| size  | int | 分页大小 | 10 |
| start  | int | 分页起始 | 0 |

#### 返回值

```json5
{
    "data": [
        // 具体用户数据结构
    ],
    "pagination": {
        "total": 283,
        "start": 0,
        "size": 1
    },
    "meta": {}
}
```

### 详情接口

`GET /api/user/<string:user_id>`

* user_id: 用户ID

#### 返回值

```json5
{
    // 具体用户数据结构
}
```
