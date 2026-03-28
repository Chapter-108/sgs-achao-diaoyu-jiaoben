# 三国杀阿超钓鱼脚本

## **项目简介**: 

这是是一个自动化脚本，通过模拟鼠标操作，实现自动钓鱼，解放双手
初版代码来源于 https://github.com/KeNanXiaoLin/sgsminigame

## **使用步骤**

1.**克隆代码** 

将代码克隆到本地电脑。

```bash
git clone https://github.com/Elevo4/TKAutoFisher.git
```

2.**安装环境**

下载 Python 3.13.0，安装 `requirements.txt` 中的库。

```bash
pip3 install -r requirements.txt
```

3.**运行脚本**: 

在模拟器中打开三国杀阿超钓鱼界面，运行 `main.py` 文件，即可开始自动钓鱼。

![image](images/description_images/diaoyu.png)

就是这个界面，然后就可以再次运行main.py就可以了。

**配置文件中的参数说明**:

**生成配置文件**

运行 `main.py` 文件，会在 `generate/config.yaml` 生成配置文件。

只有两个默认参数，模拟器大小和模拟器名称.

模拟器窗口大小不用管，窗口标题需要自己修改，改成使用的模拟器名。

比如使用的是雷电模拟器，名称就是雷电模拟器，如果是的，就个改名就可以了

## 统一入口说明

- 当前统一主入口为：`main.py`
- 历史重复入口与冗余配置文件已移除，后续仅维护 `main.py` 与 `setting.py`。

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
