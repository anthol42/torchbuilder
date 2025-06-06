# TorchBuilder
TorchBuilder is an easy-to-use tool designed to start project faster by writing all boilerplate code for you. In fact,
you can create your own template or download existing template and simply initialize them in a new project with a 
single command.

## The mission
Make the structuring process of project faster, easier and more organized. This way, organizations can all have the same
template and improve consistency across projects. On the other hand, a single researcher or student can design its own
template personalized to its needs and use it across all its projects in a single command. The installation includes a
default template that I believe is great for most projects, so you do not have to create your own template.

## How to use
### Installation
#### UV
This is the recommended way to install TorchBuilder.  You need to have 
[UV](https://docs.astral.sh/uv/getting-started/installation/) installed first on your system. If you do not have it, 
I highly recommend you to install it, as it is a great tool to manage python projects:)
```commandline
uv tool install torchbuilder
```
#### Pipx
This is an alternative to UV for people who prefer to use [pipx](https://github.com/pypa/pipx).  It is also a great tool to manage python tools.
```commandline
pipx install torchbuilder
```
#### Pip
It is not recommended to install TorchBuilder with pip globally on your system without using a virtual environment. 
Having to activate a virtual environment every time you want to use TorchBuilder can be tedious. This is why it is not 
recommended to install TorchBuilder using pip. However, if you want to install TorchBuilder globally, you can do so 
with the following command:
```commandline
pip install torchbuilder
```

### Creating a project
It is as simple as:
```commandline
torchbuilder new <project_name>
```

If you have multiple templates and want to use a specific one, you can specify it with the `--tempplate` option:
```commandline
torchbuilder new <project_name> --template=<template_name>
```

For more information, run the help command:
```commandline
torchbuilder new --help
```

### Installing a template
You can create your own template in a folder. Make a .gitignore file in the root of the tempalte and those files will 
be ignored when you create a new project with this template. You can also upload your template on github and install it
from a remote location.

```commandline
torchbuilder install <path_or_git_url>
```
Local file example:
```commandline
torchbuilder install /path/to/my/template
```

Remote git example:
```commandline
torchbuilder install git+https://github.com/anthol42/tb-template_functional.git
```

### Updating a template
If you have installed a template from a remote location, you can update it with the following command:

```commandline
torchbuilder update <template_name>
```

Otherwise, you can update it with the following command:
```commandline
torchbuilder update <template_name> <path_to_template>
```

### Listing installed templates
You can list all installed templates with the following command:
```commandline
torchbuilder ls
```

### Removing a template
You can remove a template with the following command:
```commandline
torchbuilder remove <template_name>
```

## Additional help
For all available commands and options, you can add the --help flag to any command. For example:
```commandline
torchbuilder install --help
```