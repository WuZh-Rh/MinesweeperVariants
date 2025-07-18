encoding: utf-8

Minesweeper Variants

  版本：1.3

  14 Minesweeper Variants（简称 14mv）是一款扫雷变体的解谜游戏生成器。
  支持多种扫雷规则组合，可生成具有唯一解的纸笔类谜题，或运行交互式游戏逻辑。

环境配置

  本项目基于 Python 虚拟环境开发，运行前需完成以下步骤：

  1. 安装 Python（推荐 3.11+）
    Windows 可至 https://www.python.org 下载官方安装包。

  2. 创建虚拟环境
    在项目根目录下执行：
      python -m venv .venv

    然后激活虚拟环境：
      Windows：
        .venv\Scripts\activate
      Linux / macOS：
        source .venv/bin/activate

  3. 安装依赖
    确保当前在虚拟环境中，执行：
      python -m pip install -r requirements.txt

  4. C 扩展构建环境（Windows）
    部分依赖可能需要编译 C 扩展，必须安装：
      Visual C++ Build Tools：
        可从以下地址下载安装：
        https://visualstudio.microsoft.com/visual-cpp-build-tools/

        勾选内容包括：
          C++ 生成工具（含 MSVC、Windows SDK）
          CMake

    安装完成后请重新启动终端。

使用说明

  运行方式：
    run [参数列表]
    调用主程序，生成谜题。

  常用参数（run）：

    参数               类型       说明
    -s, --size         整数（必填）  谜题尺寸
    -t, --total        整数       地雷总数
    -c, --rules        字符串列表    所有规则列表（如 2F 1Q V 1K 1F），会自动分类为左中右线规则
    -d, --dye          字符串      染色函数名（如 @c）
    -r, --drop-r       布尔开关     是否允许 R 推理
    -a, --attempts     整数       生成谜题的最大尝试次数
    -q, --query        整数       生成题板时有几线索推理才会被记录至 demo（该选项速度极慢）
    --seed             整数       随机种子（启用后会自动将 --attempts 设置为 1）
    --log-lv           字符串      日志等级，支持 DEBUG、INFO、WARNING 等
    --board-class      字符串      底层实现的题板 ID，使用默认值即可
    list                          列出当前所有实现的规则内容

  运行示例：

    run -s 5 -c 2F 1k 1q V -d c -r -q 5

    生成一道 5×5 题板，棋盘格染色，规则使用 2F、1Q（左线），V、1K（右线）
    携带 R 推理，仅记录至少具有 5 条线索推理的题板（写入 demo.txt）
    注：规则名大小写不敏感

  运行结果输出（run）：

    运行成功后将在 output/ 目录中生成以下文件：

      output/
        output.png     图像默认输出文件
        demo.txt       历史所有可推理解密文本
        demo.png       题目图片
        answer.png     答案图片

    demo.txt 中将包含以下内容：

      生成时间
      线索表（仅使用 -q 时生效）
      生成用时
      总雷数：格式为 总雷数 / 总空格
      种子 / 题号：一串整数数字
      题板的题目内容
      题板的答案和无问号时内容
      题板图片的命令生成指令（以 img 开头）
      答案图片的命令生成指令

图像输出方式

  img [参数列表]
  调用图像输出子命令。

  参数列表（img）：

    参数                  类型       说明
    -c, --code            字符串      题板字节码，表示固定题板内容
    -r, --rule-text       字符串      规则字符串（含空格需加引号）
    -s, --size            整数        单元格尺寸
    -o, --output          字符串      输出文件名（不含后缀）
    -w, --white-base      布尔开关     是否使用白底
    -b, --board-class     字符串      底层实现的board类，使用默认值即可

  运行示例：

    img -c ... -r "[V]-R*/15-4395498" -o demo -s 100 -w

    生成图片 底部文字使用 [V]-R*/15-4395498 输出保存至 output/demo.png
    每个格子的大小是 100x100 像素的 白底的图片

    注: ... 需要替换为题板的代码值，其内容被保存至 output/demo.txt 内部

开发者文档结构

  项目包含完整的开发文档，位于 doc/ 目录中：

    文档路径                                         说明
    doc/README.md                                   入口文件
    doc/dev/rule_mines.md                           左线规则接口说明
    doc/dev/rule_clue_mines.md                      中线规则接口说明
    doc/dev/rule_clue.md                            右线规则接口说明
    doc/dev/board_api.md                            题板结构与坐标系统
    doc/dev/utils.md                                工具模块接口
