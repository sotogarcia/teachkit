# Teach Kit

Teachkit es una herramienta para la gestión de la enseñanza. Permite rastrear
el proceso en cada grupo, así como generar materiales educativos a partir de
diversas fuentes y empaquetarlos para su distribución eficiente.

# Features  

Teachkit provides a comprehensive set of tools to manage teaching processes
efficiently. Its functionalities are organized into three main areas:
**Groups**, **students** and **Resources**. Below is a detailed overview of
each area and its capabilities.

## Groups  

The **Groups** section is designed to manage information related to teaching
groups. It covers the creation, synchronization, and deletion of groups, along
with tools to retrieve detailed group data.

## Students

The **Students** section is designed to manage information related to the
students enrolled in a group. It covers the creation, synchronization and
deletion of students, along with tools to retrieve detailed group data.

## Resources

The **Resources** section focuses on creating, managing, and publishing
educational resources. It supports a variety of formats and ensures easy
integration with external sources and platforms.

# Verbs

This section provides a detailed description of the available commands,
categorized based on the type of objects they operate on: group objects,
student objects, and resource objects.

## Over group objects

The following commands allow you to manage group-related data and operations
efficiently. These include listing existing groups, adding new ones, retrieving
or modifying their properties, and handling their associated folders.

- `list`    List all groups from the current or given base folder.
- `add`     Create a new folder for a group, including subfolders and an
            information file.
- `get`     Retrieve one, several, or all properties from one or more groups.
- `set`     Set property-value pairs for a group.
- `del`     Remove a group and its entire folder tree.
- `print`   Print the group's cover page.

## Over student objects

These commands help manage student-related data within a group. You can list
students, add individual records, retrieve or modify their information, and
print customized cover pages for students.

- `list`    List all students in a group.
- `add`     Create a new folder for a student and an information file.
- `get`     Retrieve one, several, or all properties of one or more students.
- `set`     Set property-value pairs for one or all students.
- `del`     Remove a student or a list of students.
- `print`   Print the cover page for one or all students.

## Over resource objects

Resource objects represent the educational resources associated with students
or groups. These commands allow you to manage topics, resources, and exercises,
as well as track or update their states.

- `list`    List all available topics, categories, and/or resources.
- `add`     Add exercises to a student's folder, a resource folder, or all
            group folders.
- `get`     Retrieve the state of an exercise for a student or all students.
- `set`     Copy exercise from group resources folder to students folder.
- `del`     Remove a resource from a student's folder or all folders.
- `print`   Print a resource statement without adding it to any folder.


group list
group add directory_or_name
group get property
group set property value
group del directory_or_name
group print

student list
student add directory_or_name
student get property
student set property value
student del directory_or_name
student print
student print directory_or_name

resource list
resource list topic
resource list topic category
resource add
resource add topic
resource add topic category
resource add topic category exercise
resource get
resource get topic
resource get topic category
resource get topic category exercise
resource set
resource set topic
resource set topic category
resource set topic category exercise
resource del directory_or_exercise
resource print
resource print directory_or_name

## Folders

```
─ Group
    ├ ~resources
    ├ .metadata
    │   ├ config
    │   ├ unenrolled
    │   │   └ ...
    │   └ logs
    ├ student_n
    │   ├ YYYY_MM_DD
    │   ├ EX001_-_Exercise name
    │   └ ...
    └ ...
```

## Config

Load configuration in the following order. The most recently loaded value takes
precedence:

1. Files in `data/config/` within the application folder
2. Files in `.metadata/config/` within the group folder
3. Values from the system environment
4. Arguments provided in the command line

## Installation  

To install Teachkit, make sure you have Python 3.8 or higher installed on your
system. Then, clone the repository and install the dependencies:

```bash
git clone https://github.com/sotogarcia/teachkit.git
cd teachkit
pip install -r requirements.txt
```

