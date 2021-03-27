# doccreator
This tool is a documentation generator. It is currently not complete. I plan on expanding it by adding more types of documentation, so please feel free to add a new feature and submit a merge request. The main point of this project is to generate good looking documentation in markdown by programmatically specifying information, either through the creation of custom objects, or through JSON. Each tool in the project should have a main class that represents a piece of documentation (for example, a section on a web server path), and include custom classes that represent various different parts of that section (for example, parameters). Each of these objects should have a method to convert their data into JSON format, so that they entire piece of documentation can be saved as a JSON file, or loaded from a JSON file. Please start a discussion if you have any questions about what makes a tool fit for this project.

# Current Tools
## Webserver Path
This tool generates documentation for a path (either GET or POST) on a webserver. 
