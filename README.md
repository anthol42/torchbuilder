# TorchBuilder
**- Current version 0.3.0 -**  
TorchBuilder is an easy-to-use tool designed to help you research faster and more efficiently.
It is a tool that will create the whole folder tree of you project in only one terminal 
command.  In addition, it implements a lot of boiler plates for you with the same command.
It automatically creates the virtual environment and upload the initial commit to your
git repository.  As if it wasn't enough, the project tree and boiler plates are fully and
easily customizable to fit your preferences.

## Our mission
Our mission is to do the vast majority of the repetitive stuff to let you 
focus on your research.  We believe that time is a scarce resource, and we 
must spare it.  In addition to that, to alleviate the risk of getting a 
messy project, we provide suggested guidelines to help you manage your projects
and researches as clear and understandable as possible.  We also provide
useful resources that can help you develop faster, better and cleaner projects.

## How to use
### Context
To make research more ordered, we use a solution as a parent folder.  
A solution can contain many projects.  Each project can contain many
experiments.  It is suggested to create a new solution for each problem
to solve.  For example, if I want to make a deep neural network that detects
anomalies in neurons, I would create a solution called something like 
"synapticAnomalyDetection".  Then, each approach has its own project.  For example,
if I want to implement something I found in a paper and explore different variant
of this, I would create a project for this.  In this project, I can have different 
experiment with different hyperparameters to try.  In later subsection,
proposed guidelines will explain in more details how to structure the project.

### Installation
*Notes:You may need to install additional dependencies like python-venv or other to be able to
create a virtual environment.  In addition, you will need to set up your git with your profile
to enable automatic push. (With username and password)*

First clone the repository:
```commandline
git clone "https://github.com/carcajou666/torchbuilder.git"
```
Then go in the newly cloned directory:
```commandline
cd torchbuilder
```
Then compile the installation script:
```commandline
chmod +x install.sh
```
Then install the app:
```commandline
./install.sh
```
It may be needed to restart the terminal app to let the installation take effect.

**Uninstall**
```commandline
cd ~/torchbuilder
chmod +x uninstall.sh
./uninstall.sh
```

### Creating a solution
Basic syntax: torchbuilder make [solution name] project=[project name] **kwargs
```commandline
torchbuilder make solution1 --project="project1" --repo="https://github.com/abc/xyz.git" --venv=True
```
**Parameters:**
- make : tells TorchBuilder that we want to make a solution
- project : [optional] Name of the project to create.  If not specified, no project will be created.
- --repo : [optional] Url to the repo.  If not specified, solution won't be uploaded to repo.
- --venv : [optional] (True or False) If False, virtual environment won't be created.  Default:True

### Creating a project
**Notes:**

A project can only be inside a solution.  Solutions have a .solution.sol file that contains information
about the solution.  If the file has been deleted,  TorchBuilder will not recognize the folder as a 
solution. 

Basic syntax: torchbuilder new [project name] **kwargs
```commandline
torchbuilder new project2 --venv=True 
```
**Parameters:**
- new : tells TorchBuilder that we want to create a project.
- --venv: [optional] (True or False) If False, virtual environment won't be created.  Default:True

### Removing a project
You can safely delete the project folder, and it's not more complicated than that!

## Suggested Guidelines
This section explains suggested guidelines to follow to work seamlessly with the default template and to understand the 
idea behind the way the default template has been designed.  If you create you own template, we encourage you to make
proposed guidelines to help people work with you template.
### Idea to keep in mind
The idea to keep in mind when making a project is, one, be as organized as possible.  Two, EVERY results of
different experiments must always be written down with information to reproduce the result.  Three, results must be
authentic, not just written on the fly.

**Rules:**
1. Never delete anything!
2. Config files are immutable.  Never modify a config file, create a new one.

### How to organise the project
Always go for a modular approach.  Every class or function should have its own file. (With exception to internal 
functions/class or functions/class that are really close together in terms of usage.)  This way,
files won't have too many lines and will be way more readable.

- Each experiment is a function in its own file and is registered in the main file in the dictionary.(See comments in the main fil for more info.)
- The main file is the only file that is run.  
- Every hyperparameters are pass through a config file (Yaml) or through kwargs to the main file
- ResultTable api is used to keep tract of results through different experiments and hyperparameters.
- Write a labbook describing the goal of each experiment, the hypothesis and the results.  It is adviced
to write these information in markdown files with the same name as the experiment file.

## Useful Components integrated
- [ResultTable](Documentation/ResultTable.md)
- [CheckPoint](Documentation/CheckPoint.md)
- [Color](Documentation/Color.md)
- [FeedBack](Documentation/FeedBack.md)
- [DynamicMetric](Documentation/DynamicMetric.md)
- [ConfigFile](Documentation/ConfigFile.md)
- [State](Documentation/State.md)

## Example
When TorchBuilder builds a new project, it builds code to run a classification task on MNIST.
This section show an example how to run the code generated by TorchBuilder to classify handwritten numbers.

1. Once the project is created, move in the project directory.  (Remember that the solution is not the project)
2. Then, you can activate the virtual environment:
```commandline
source venv/bin/activate
```
3. Run the 'experiment1' with the 'config.yml' config file.
```commandline
python main.py --experiment="experiment1" --config="configs/config.yml" --debug=True
```
4. There you go, you ran in few seconds a small computer vision project!

**Note:**
To add new kwarg, it is possible to add them in the main.py file.

## Customization
To customize templates, you can create a project that you want to be your new template,
then you can compile it and Torchbuilder will add it to the existing list of templates.  NOTE: The compiling process
will save as a template everything!  Make sure there is no unwanted files such as python cache or
system files because they will be included in your template.

Synthax: torchbuilder {name of template} {source of template}

Example:
```commandline
torchbuilder compile my_template /path/to/the/project/to/compile
```

To see existing templates:
```commandline
torchbuilder ls-templates
```

To remove a template:
```commandline
torchbuilder rm-template my_template
```

## See file tree and structure of a template
To see the structure of a template, there is two ways:
1. Go in the templates' folder and open the ```template_format.txt``` file.  The path should be: ```~/torchbuilder/Templates/{name}/template_format.txt```
2. Use the command:
```commandline
torchbuilder show-template <name>
```
where name is the template name.
Example:
```commandline
torchbuilder show-template default
```
