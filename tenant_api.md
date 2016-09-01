# 租户API接口定义

## 概述

租户是在易考系统上注册的客户，租户可以通过租户API读写系统内的数据，实现与外部系统的集成。
租户API为REST风格的 HTTP 或 HTTPS 服务端API，方便开发者使用。本文档描述租户API具体参数和规范。

所有交换数据格式为JSON格式。

## 认证

租户必须的系统上获得一个API Key，所有针对租户API的调用，都必须在请求的Head中包含有效的API Key。 例如："Authorization": "key sWRPaOAuzDYjer3KT3aF95xUPyLz"
其中sWRPaOAuzDYjer3KT3aF95xUPyLz为有效的API Key，如果系统发现API Key无效，则返回授权失败，即401错误。

## 内容接口

### 查询试卷

查询试卷是否存在。

URL
    /tenant/api/form/xxxx/

请求方式：GET
请求参数：无

URL中的xxxx为试卷代码，如果代码存在，则返回HTTP状态码：200，否则返回状态码：404
请求不返回任何数据。

### 取试卷

取试卷信息。

URL
    /tenant/api/form/xxxx/get/

请求方式：GET
请求参数：无

URL中的xxxx为试卷代码，如果试卷存在的话，返回200正确代码。并返回一个JSON对象，包含试卷的代码,试卷内容,试卷答案。
例如：

{"code":"xxx","form": {"id":"xxx",....}, "key": {"id":"xxxx",.....}

#### 测试命令

curl -X GET https://eztest.org/tenant/api/form/xxxx/get/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz'


### 导入试卷

通过导入试卷接口，可以把外部试卷导入到系统。试卷必须包含完整的试卷内容，包括试题和正确答案。

URL

    /tenant/api/form/

请求方式：POST
请求参数：包含答案的试卷JSON数据，参见样例。

返回结果
成功的话，返回201正确代码。并返回一个JSON对象，包含试卷的内部ID和代码。
例如：

    {
        "id": "5",
        "code": "F05"
    }

试卷中如果有引用图片等外部资源，可以采用两种方式：

- 使用完整的资源路径；
- 只使用文件名，后续调用试卷资源导入接口上传资源文件；

#### 测试命令

curl -X POST http://websitedomian/tenant/api/form/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz' -d ''"`cat ./doc/form_import_template.json`"''

### 导入试卷资源

添加试卷需要的图片等资源文件，资源添加必须指定到已经创建的试卷。
URL

    /tenant/api/form/xxxxx/resource/

xxxxx为已经创建的试卷ID。如果试卷ID不存在，或者不属于本租户，返回403错误和错误信息。

请求方式：POST

请求参数：

    {
        "name": "img.jpeg",
        "content_type": "img/jpeg",
        "content": "aW1hZ2UgY29udGVudA==\n"
    }

name必须和试卷中引用的名字一致。
content为经过BASE64编码的资源文件内容。

返回结果：
成功返回201代码。并返回一个json对象，包含试卷中引用此图片的次数。

    {
        "reference": "2"
    }

一般情况下引入次数都是为1，如果有超过1，说明试卷中有多处使用了此资源；如果为0，表示没有对此资源的引用，请检查是否上传了正确的文件。

试卷资源请避免使用中文或者带有空格的字符串，请使用英文字母和数字组合的文件名。

#### 测试命令

curl -X POST http://websitedomain/tenant/api/form/17/resource/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz' -d '{"name":"a.jpg", "content_type":"jpg/image", "content":"'"`cat ./doc/favicon.base64`"'"}'

## 场次接口

### 创建场次

URL

    /tenant/api/session/

请求方式：POST

请求参数：

    {
        "name": "场次名称",
        "message": "欢迎参加考试，。。。",
        "start": "2015-01-01 09:00",
        "end": "2015-01-01 11:00",
        "allow_anonymous": True,
        "forms": ["F001", "F002"],
        "personal": {
            "full_name": {
                "required": True,
                "type": "text",
                "order": 0,
                "label": "姓名"
            },
            "gender": {
                "choices": ["男", "女"],
                "required": True,
                "type": "radio",
                "order": 1,
                "label": "性别"
            },
            "email": {
                "required": True,
                "type": "email",
                "order": 2,
                "label": "邮箱"
            },
            "phone": {
                "required": True,
                "type": "text",
                "order": 3,
                "label": "手机"
            }
        },
        "extra": {
            "center": "考点名称",
            "room": "考场名称"
        }
        "notify_url": "http://yoursite/your_url"
    }

其中必须包含的参数包括：

- name  - 场次名称
- start - 开始时间
- end   - 结束时间，如果结束时间小于开始时间，或者小于当前时间，返回403和错误信息。
- forms - 试卷代码，一个或多个，一个试卷代码不存在，或者不属于当前租户，返回403和错误信息。

其他为非必须参数，当不存在时，取以下默认值。

- allow_anonymous - 默认False， 指是否允许即报即考
- message - 默认为空，指登录前显示给考生的信息
- personal - 需要考生填写的信息，默认包含full_name, gender, email, phone，可扩展
- extra - 补充信息，默认无
- notify_url - 回调地址，当存在此参数时，该场次的考生完成考试后，会主动调用通知此url

#### 回调通知

如果存在notify_url参数，则考生完成考试后，通过POST方式调用此url，参数如下：

    {
        "full_name": "考生姓名",
        "session_name": "考试名称",
        "permit": "准考证号",
        "total_score": "得分",
        "exam_address": "参考地点（根据IP地址）",
        "time": "考试用时",
        "form_name":"使用试卷名",
        "sections":[
            {
                "name": "单元名称",
                "total_score": "单元总分",
                "user_score": "单元得分",
                "groups": [
                    {
                        "name": "大题名称",
                        "total_score": "大题总分",
                        "user_score": "大题得分",
                    },...
                ],...
            },...
        ],
        "report_exist": (True or False),
        "reports": (exist only if report_exist is True)[
            {
                "name": "报告名称",
                "url": "报告URL",
            }
        ]
    }


返回结果：
成功返回201代码。并返回一个json对象，包含创建的场次信息。

    {
        "id": "2"
        "url": "https://eztest.org/exam/session/10/"
    }

#### 测试命令

curl -X POST http://websitedomain/tenant/api/session/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz' -d '{"end": "2015-01-01 11:00", "name": "测试场次名称", "personal": {"gender": {"choices": ["男", "女"], "required": "true", "type": "text", "order": "2", "label": "性别"}, "first_name": {"required": "true", "type": "text", "order": "0", "title": "名"}, "last_name": {"required": "true", "type": "text", "order": "1", "title": "姓"}}, "allow_anonymous": "True", "start": "2015-01-01 09:0", "message": "欢迎参加考试", "forms": ["F0001"]}'

### 删除场次

URL

    /tenant/api/session/xxx/

其中xxx为场次id

请求方式：DELETE

请求参数：无

返回结果：成功返回200

删除场次操作将删除整个场次，包括场次包含的考生。但不删除场次使用的试卷。如果要删除的场次不属于本租户，则返回403


### 修改场次

URL

    /tenant/api/session/xxx/

其中xxx为场次id

请求方式：PUT

请求参数：同创建场次请求参数

返回结果：成功返回200。如果要修改的场次不属于本租户，则返回403



### 创建考生

URL

    /tenant/api/session/xx/entry/

xx为场次ID。必须对应租户创建的场次。如果场次不存在，或者不属于本租户，返回403错误和错误信息。

请求方式：POST

请求参数：

    [
        {
            "permit": "xxxx0001",
            "full_name": "张三",
            "email": "xxx@xxx.com",
            "gender": "男",
            "phone": "13911112222"
        },
        {
            "permit": "xxxx0002",
            "full_name": "张三",
            "email": "xxx@xxx.com",
            "gender": "男",
            "phone": "13911112222"
        },
        {
            "permit": "xxxx0003",
            "full_name": "张三",
            "email": "xxx@xxx.com",
            "gender": "男",
            "phone": "13911112222"
        }
    ]

考生信息必须对应创建场次时指定的信息项。可同时创建多个考生，每个考生可指定准考证号，也可以不指定。如果不指定准考证号，系统会生成并返回准考证号。

返回结果：
成功返回201代码。返回成功的考生准考证号，及统计信息。
失败的考生返回具体考生账号和错误代码

错误代码如下
4000:其他错误;
4001:考生信息缺失;
4002:考生账号重复;


    {
        "succeed": "3",
        "fail": "2",
        "permits": ["xxxx0001", "xxxx0002", "xxxx0003"]
        "errors": [{"entry": "xxxx0001", "error": "4000"}]
    }

#### 测试命令

curl -X POST http://websitedomin/tenant/api/session/1/entry/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz' -d '[{"gender": "男", "email": "xxx@xxx.com", "full_name": "测试1", "phone": "13911112222"}]'


### 删除考生

URL

    /tenant/api/session/xx/entry/yyyyyy/

xx为场次ID。必须对应租户创建的场次。如果场次不存在，或者不属于本租户，返回403错误和错误信息。
yyyyyy为要删除考生的准考证号

请求方式：DELETE

请求参数：无

删除考生后无法回复，考生信息和考试结果等所有数据都被删除。

### 修改考生

URL

    /tenant/api/session/xx/entry/yyyyyy/

xx为场次ID。必须对应租户创建的场次。如果场次不存在，或者不属于本租户，返回403错误和错误信息。
yyyyyy为要修改考生的准考证号

请求方式：PUT

请求参数：

    {
        "full_name": "张三",
        "email": "xxx@xxx.com",
        "gender": "男",
        "phone": "13911112222"
    },


指定准考证号必须已经存在，修改成功返回200.

### 查询场次考生状态

URL

    /tenant/api/session/xx/entry/

请求方式: GET

请求参数：无

返回数据：

成功返回200，并返回考生状态明细数据。

    {
        "session": "1",
        "entries": [
            {
                "permit": "xxxx0001",
                "full_name": "张三",
                "email": "xxx@xxx.com",
                "phone": "13900000000",
                "gender": "男",
                "status": "ongoing"
            },
            {
                "permit": "xxxx0002",
                "full_name": "张三",
                "email": "xxx@xxx.com",
                "phone": "13900000000",
                "gender": "男",
                "status": "completed"
            },
            {
                "permit": "xxxx0003",
                "full_name": "张三",
                "email": "xxx@xxx.com",
                "phone": "13900000000",
                "gender": "男",
                "status": "valid"
            }
        ]
    }

status - 考生状态，可能存在5种：
    - valid: 未开考
    - ongoing: 考试中
    - interrupted: 中断
    - completed: 正常结束

### 查询单个考生成绩

URL

    /tenant/api/session/xx/entry/yyyyyyyy/score/

xx为场次ID, yyyyyyyy为考生准考证号

请求方式：GET

请求参数： 无

返回结果：
成功返回200代码, 并返回考生成绩明细，包含总得分，以及每个部分和每个大题的得分。

    {
        "permit": "KdyF0005",
        "score": 10,
        "sections": [
            {
                "score": 10,
                "name": "试卷主体",
                "groups": [
                    {
                        "score": 5,
                        "name": "言语理解",
                    },
                    {
                        "score": 5,
                        "name": "逻辑推理",
                    }
                ]
            }
        ]
    }

错误返回错误信息。如果考生不存在，返回代码403；如果考生存在，但是尚未完成考试，或分数计算尚未完成，同样返回代码403,以及如下错误信息：

    {
        "permit": "KdyF0005",
        "error": "Entry result not found",
    }

#### 测试命令

curl -X GET https://eztest.org/tenant/api/session/1/entry/OPN70001/score/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz'


### 查询单个考生成绩详情

URL

    /tenant/api/session/xx/entry/yyyyyyyy/score/detail/

xx为场次ID, yyyyyyyy为考生准考证号

请求方式：GET

请求参数： 无

返回结果：
成功返回200代码, 并返回考生成绩明细，包含总得分，以及每个部分和每个大题的得分。

    {
        "full_name": "考生姓名",
        "session_name": "考试名称",
        "permit": "准考证号",
        "total_score": "得分",
        "exam_address": "参考地点（根据IP地址）",
        "time": "考试用时",
        "form_name":"使用试卷名",
        "sections":[
            {
                "name": "单元名称",
                "total_score": "单元总分",
                "user_score": "单元得分",
                "groups": [
                    {
                        "name": "大题名称",
                        "total_score": "大题总分",
                        "user_score": "大题得分",
                    },...
                ],...
            },...
        ],
        "report_exist": (True or False),
        "reports": (exist only if report_exist is True)[
            {
                "name": "报告名称",
                "url": "报告URL",
            }
        ]
    }

错误返回错误信息。如果考生不存在，返回代码403；如果考生存在，但是尚未完成考试，或分数计算尚未完成，同样返回代码403,以及如下错误信息：

    {
        "permit": "KdyF0005",
        "error": "Entry result not found",
    }

#### 测试命令

curl -X GET https://eztest.org/tenant/api/session/1/entry/OPN70001/score/detail/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz'



### 查询场次考生成绩

URL

    /tenant/api/session/xx/score/

xx为场次ID

请求方式：GET

请求参数： 无

返回结果：
成功返回200代码。成功返回整场考生成绩。返回数据中不包含尚未开考的考生。

    {
        "session": "1",
        "entries": [
            {
                "permit": "xxxx0001",
                "score": "90",
                "finished": True
            },
            {
                "permit": "xxxx0002",
                "score": "100",
                "finished": True
            },
            {
                "permit": "xxxx0003",
                "score": "80",
                "finished": False
            },
            {
                "permit": "xxxx0004",
                "score": "92",
                "finished": True
            }
        ]
    }

如果场次不存在，或者不属于本租户，返回代码403和如下错误信息：

    {
        "session": "xx",
        "error": "session not found"
    }

#### 测试命令

curl -X GET http://websitedomain/tenant/api/session/1/score/ -o ~/response.html -H 'AUTHORIZATION: Key sWRPaOAuzDYjer3KT3aF95xUPyLz'


### 查询单个考生答题详情

URL

    /tenant/api/session/xx/entry/yyyyyyyy/response/

xx为场次ID, yyyyyyyy为考生准考证号

请求方式：GET

请求参数： 无

返回结果：
成功返回200代码, 并返回考生答题明细。返回数据结构如下:

    {
        "response": {"": "",.... },
        "form_content: {"": "", ...},
        "form_key: {"": "", ...},
        "form_code": "xxxxx"
    }


错误返回错误信息。如果考生不存在，返回代码403

    {
        "permit": "KdyF0005",
        "error": "Entry result not found",
    }


### 查询单个考生成绩

URL

    /tenant/api/session/xx/entry/yyyyyyyy/result/

xx为场次ID, yyyyyyyy为考生准考证号

请求方式：GET

请求参数： 无

返回结果：
成功返回200代码, 并返回考生得分详情。返回数据结构详见核心数据标准.


错误返回错误信息。如果考生不存在，返回代码403；如果考生存在，但是尚未完成考试，或分数计算尚未完成，同样返回代码403,以及如下错误信息：

    {
        "permit": "KdyF0005",
        "error": "Entry result not found",
    }
