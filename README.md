# LMA: An Open-Source Local Audio Sample Manager

Welcome. This document contains three part in sequence: Chinese LMA Quick Start, English LMA Quick Start and information for developers.

![](/images/LMA_promo.png)

---

## LMA使用指南

感谢你使用LMA（暂定名）本地音频采样管理器。软件皆在帮助音乐创作者们更快的检索和标记本地的音频采样。

以下是对操作的简单说明。

### 初始化
- 选择Select Folder，并选择你希望检索的本地采样的文件夹。
- 选择Rescan会重新扫描文件夹内的采样。

### 检索
- 在Enter Keywords处输入搜索关键词，点击search搜索采样。
  - 点击下方窗口出现的采样进行音频预览，再次点击则可中断音频播放
- 选中采样后即可拖拽采样至宿主软件/其它位置，拖拽后的采样会被复制到新的位置。
- 可以选择搜索loop或者one shot
- 可以搜索指定范围BPM的采样
  - 如果前后输入为同一个数字，则转而搜索精准BPM
  - 
### 标记
  - 右键采样出现选项 “Add to collection”
    - 选中后，列表中采样前会有星星标记。
    - 标记采样并不会改变文件本身的名称，请放心。
- 采样的分类与索引基于文件本身的命名

---

# LMA Quick Start Guide

Thank you for using LMA (Working Title) Local Audio Sample Manager. I designed this light tool to help music creators retrieve and tag their local audio samples faster.

### Initialization

* Press "Select Folder" and choose the local sample folder you wish to scan.
* Press "Rescan" to perform a fresh scan of the samples within the folder.

# Serching Samples

* Enter your search keywords in the Enter Keywords field, then click Search or press Enter to find samples.
  * Click on a sample that appears in the window below to preview the audio. Clicking it again will stop the playback.
* Once a sample is selected, you can drag and drop it to your DAW or another location. The dragged sample will be copied to the new location.
* You can choose to search for loop or one-shot samples.
* You can search for samples within a specified BPM range.
  * If you enter the same number for both the start and end of the range, the search will switch to looking for an exact BPM match.

### Tagging
* Right-click on a sample to bring up the option: "Add to Collection."
  * Once selected, the sample will have a star icon next to it in the list.
  * Please note that tagging a sample does not change the file's original name, so you can use this feature worry-free.
* Sample classification and indexing are based on the file's original name.

---

# For Developers

LMA was developed using **Python** (3.8+ recommended) and the **PyQt5** framework.

### Core Dependencies:
* `PyQt5`
* `pygame`
* `soundfile`

### Code Structure:
* **`LMA_GUI.py`**: Handles the graphical user interface (GUI), user interaction, and session persistence.
* **`sample_parser.py`**: Contains the core logic for **scanning folders** and **parsing filename metadata** (BPM, Key, Form).

LMA is currently under development. Please let me know if you have any suggestions or ideas to make it better. You are also welcomed to modify the codes yourself:)