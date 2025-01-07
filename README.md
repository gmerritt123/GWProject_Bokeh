# Bokeh Applications for the Groundwater Project

[The Groundwater Project's](https://gw-project.org/) mission is to make groundwater understandable by providing freely available educational materials related to the field of hydrogeology. As part of that effort, a number of educators/volunteers seek to develop interactive web applications to illustrate key concepts in hydrogeology. [Bokeh](https://bokeh.org) has been identified as an ideal library for this development.

This repository aims to...

1) Serve as the central repository of all bokeh-based applications to be embedded on the Groundwater Project Website
   
2) Provide standalone html output of each application (for standalone usage or embedding within other websites/applications)
   Htmls within each subfolder are free/available to be used as teaching materials (download and open in any web browser), OR embed the html within your existing applications (please give credit/reference to us!)

3) Serve as a "base" for customization of existing applications and development of new ones
   Repo can be forked/branched for custom development/modification to suit your needs. Again please give credit/reference to us!

4) Provide a centralized location for core utility functions (both python and javascript) for leveraging across all applications
   See Bokeh_Util.py and Bokeh_Util.js for respective python/js functions that can be used to expedite application development. 

## Getting started with additional development:

You'll need:

- A github account
- git installed locally
- Python 3.12 with bokeh >= 3.4 and all its dependencies (numpy, pandas etc.)
- An Integrated Development Environment of your choosing (recommend [Spyder](https://www.spyder-ide.org/) )

Clone (or fork) this repository:

`git clone https://github.com/gmerritt123/GWProject_Bokeh`

- Identify an application/tool to develop/modify --> See GWInux's applications for some great ideas/examples [here](https://github.com/gw-inux/Jupyter-Notebooks)
- File a [GH Issue](https://github.com/gmerritt123/GWProject_Bokeh/issues) flagging it as an application you're working on --> use the "Enhancement" label and assign yourself as the assignee
- Create a branch of your local repository:

`git branch nameOfNewApp` if modifying existing one `git branch improveXApp`

- Create/modify in a new folder within the repository
  

