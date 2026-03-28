# 三国杀阿超钓鱼脚本

## **项目简介**: 

这是是一个自动化脚本，通过模拟鼠标操作，实现自动钓鱼，解放双手
初版代码来源于 https://github.com/KeNanXiaoLin/sgsminigame

## **使用步骤**
1.**运行脚本**: 

在模拟器中打开三国杀阿超钓鱼界面，运行 `main.py或start.bat` 文件，即可开始自动钓鱼。

![image](images/description_images/diaoyu.png)

就是这个界面。

**配置文件中的参数说明**:

**生成配置文件**

运行启动文件，会在 `generate/config.yaml` 生成配置文件。

只有两个默认参数，模拟器大小和模拟器名称.

模拟器窗口大小不用管，窗口标题需要自己修改，改成使用的模拟器名。

比如使用的是雷电模拟器，名称就是雷电模拟器，如果是的，就个改名就可以了

## start.bat 说明

`start.bat` 是项目的快速启动脚本，适合直接双击运行，不用手动输入命令。

- 双击后会显示菜单：
  - `1` 正常启动（默认配置）
  - `2` 检查模式（默认配置）
  - `3` 退出
- 也支持命令行透传参数给 `main.py`，例如：

```bash
start.bat --检查模式 --配置 default
start.bat --窗口标题 "雷电模拟器"
```

## 命令行参数

`main.py` 支持直接传参覆盖窗口配置（无需改代码）：

```bash
python main.py --窗口标题 "雷电模拟器"
python main.py --窗口区域 163,33,1602,946
python main.py --配置 default
python main.py --保存配置 雷电配置 --窗口标题 "雷电模拟器"
python main.py --检查模式 --配置 default
```

- `--窗口标题`: 覆盖模拟器窗口标题。
- `--窗口区域`: 覆盖截图区域，格式为 `x,y,width,height`。
- `--配置`: 使用 `generate/profiles.yaml` 中的配置档（可复用多模拟器参数）。
- `--保存配置`: 将当前解析后的窗口参数保存到指定配置档后退出。
- `--检查模式`: 执行资源、配置和窗口可用性检查后退出（适合排障）。

## profiles 配置示例

脚本首次运行会自动创建 `generate/profiles.yaml`，也可以手动维护：

```yaml
default:
  window_title: 雷电模拟器
  window_size: [163, 33, 1602, 946]
```
