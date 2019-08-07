import os

from jinja2 import FileSystemLoader, Environment

parent = os.path.dirname(os.path.dirname(__file__))
path = os.path.join(parent, 'templates')
# 创建一个加载器, jinja2 会从这个目录中加载模板
loader = FileSystemLoader(path)
# 用加载器创建一个环境, 有了它才能读取模板文件
e = Environment(loader=loader)


def render(filename, *args, **kwargs):
    # 调用 get_template() 方法加载模板并返回
    template = e.get_template(filename)
    # 用 render() 方法渲染模板
    # 可以传递参数
    return template.render(*args, **kwargs)

def test():
    render("test.html")