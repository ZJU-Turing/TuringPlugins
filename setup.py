import os
from setuptools import setup, find_packages


setup(
    name='mkdocs-turing-plugins',
    version='0.0.1',
    author='ZJU Turing',
    description='A MkDocs plugin used in TuringCourses',
    url='https://github.com/ZJU-Turing/TuringPlugins',
    python_requires='>=3.5',
    install_requires=[
        'mkdocs',
        'GitPython'
    ],
    entry_points={
        'mkdocs.plugins': [
            'turing_changelog = mkdocs_turing_plugins.changelog:ChangelogPlugin',
            'turing_contributors = mkdocs_turing_plugins.contributors:ContributorsPlugin',
            'turing_evaluations = mkdocs_turing_plugins.evaluations:EvaluationsPlugin',
            'turing_outdate_warning = mkdocs_turing_plugins.outdate_warning:OutdateWarningPlugin',
        ]
    },
    include_package_data=True,
    package_data={
        'src': [
            'templates/*.html'
        ]
    }
)
