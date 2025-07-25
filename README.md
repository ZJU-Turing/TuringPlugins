# mkdocs-turing-plugins

> [!IMPORTANT]
> 本仓库中插件的所有功能已改为更优雅且方便的 [hook](https://www.mkdocs.org/user-guide/configuration/#hooks) 实现，构建 [TuringCourses](https://github.com/ZJU-Turing/TuringCourses) 将不再需要安装本插件，因此本仓库弃用。如有功能性修改，请直接向 [TuringCourses 中的 hooks 文件夹](https://github.com/ZJU-Turing/TuringCourses/tree/master/hooks)提交 Pull Request。

一个专门用在 [TuringCourses](https://github.com/ZJU-Turing/TuringCourses) 文档上的 mkdocs 插件集合。

## 安装
只用于 TuringCourses，所以不考虑发布 PyPI，只能从源码安装：

```shell
$ git clone https://github.com/ZJU-Turing/TuringPlugins.git
$ cd TuringPlugins
$ pip install . # or pip install -e .
```

## 开发
仍在开发阶段，当前开发计划请见 [Projects: TuringPlugins development plan](https://github.com/orgs/ZJU-Turing/projects/1)。其他 feature request 也可以开在 Issue 里面。欢迎 PR 来一起实现这些功能。
