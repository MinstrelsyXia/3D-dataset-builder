The spider program of spidering on [polycam](https://poly.cam), [3d.si](https://3d.si.edu), and [sketchfab](https://sketchfab.com)

# Environment setup
1. ChromeGoogle浏览器：请下载最新版本，可通过属性查看所下载的版本
2. ChromeDriver驱动器：
对于chrome115及以上版本，通过该页面下载：https://googlechromelabs.github.io/chrome-for-testing/

注：上述两个软件的exe文件最好放在同一个目录下，并添加ChromeDriver的基本路径，添加完基本路径后重启电脑（chromedriver和chrome的exe所在的文件夹添加路径到系统变量中的Path）

3. XPATH-Helper：拓展插件，可方便地检测你所写的xpath语句是否能准确找到所需节点

4. Selenium爬虫库：
```shell
selenium：pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple selenium
requests：pip install requests
```
