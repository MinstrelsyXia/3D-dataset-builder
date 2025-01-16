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

# Details on different website:
## polycam:
1. 手动登录网站 https://poly.cam/，点击右上角sign up并用邮箱创建账号
2. 清空电脑内的下载文件夹，并在放置脚本的同一目录下创建models文件夹（详情可参考3.2）
3. 将脚本`polycam.py`内的默认下载路径和邮箱密码等改为自己的，运行脚本
4. 要求输入catagory和item，catagory统一输入art，item有以下可选项：ceramics / bronze / dynasty / ancient / antique / culture
5. 该网站时不时会出点bug，如果程序报错就重新运行脚本，如果之前已经下载好了一部分模型，可以在脚本执行完邮箱登录操作后的空挡里（设置了30秒缓冲时间），手动拖动右侧滚动条滑倒上次未下载完的地方，脚本即可从该处继续下载
【注：因为该网站下载速度很快，所以脚本执行是一边爬取数据并写入json文件，一边直接下载模型到本地，同时程序自动地将模型改名并移动到models文件夹内】
【注：脚本已做了一些异常情况处理，比如有些模型已经下载过/没有下载链接，就会自动跳过，无需手动剔除重复样本，脚本存在的最大问题就是程序可能下载完一些模型后自动退出，这时需要参考第5步】

## 3d-si:
1. `json_generation_3dsi.py` 从网页爬取数据并生成json文件
2. `data_download_3dsi.py` 根据json文件下载压缩包到本地文件夹
3. 若出现"Chrome failed to start"问题可尝试注释第39行
`# chrome_options.add_argument('--no-sandbox')`
4. 注1：由于这个网站的下载速度很慢，所以不在爬取数据的时候下载，而是等把下载链接都爬下来后看，再统一下载
5. 注2：很多模型并没有合适的下载链接，脚本会输出“no matching link“，这是合理的，请不必惊慌

## sketchfab:
1. `sketchfab.ipynb`: 由于skatchfab没有下载链接，这个脚本同时运行的同时就把模型下载到了本地，然后再把模型更名为{uid}.glb放到models文件夹。
1. 注1：**先把你的download文件夹清空**! 实现思路是：把download文件夹清空，每次下下来一个文件，把这个单一文件移动到models文件夹
2. 注2：Skatchfab 每个账号每天会有下载限制（约100？）
