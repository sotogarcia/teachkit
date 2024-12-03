# Teach Kit
Teachkit es una herramienta para la gestión de la enseñanza. Permite rastrear el proceso en cada grupo, así como generar materiales educativos a partir de diversas fuentes y empaquetarlos para su distribución eficiente. 

# Features  

Teachkit provides a comprehensive set of tools to manage teaching processes efficiently. Its functionalities are organized into two main areas: **Groups** and **Materials**. Below is a detailed overview of each area and its capabilities.  

## Groups  
The **Groups** section is designed to manage information related to teaching groups. It covers the creation, synchronization, and deletion of groups, along with tools to retrieve detailed group data.  

### Create a Group  
- Allows the creation of a new local group.  
- Requests the necessary group information during setup.  
- Automatically generates the folder and file structure required for maintenance.  

### Get Group Information  
- Displays detailed information about the group.  
- Provides various listing and reporting options for the group.  
- Allows access to specific group-related details.  

### Synchronize Group  
- Updates group details and user lists from an external source.  
- Supports interchangeable sources such as Odoo, Moodle, etc.  

### Delete a Group  
- Deletes a group locally.  
- Removes all associated information, including folders and files.  

## Materials  
The **Materials** section focuses on creating, managing, and publishing educational resources. It supports a variety of formats and ensures easy integration with external sources and platforms.  

### Create New Material  
- Creates the structure for a new educational resource.  
- Supports multiple formats, including DITA and document files (e.g., DOC, PDF).  

### Get Material Information  
- Displays detailed information about a resource.  
- Provides options for listing and organizing resources.  
- Allows access to specific details of a resource.  

### Regenerate Material  
- Produces a suitable output format from the source material (e.g., PDF from DITA).  
- Updates local resources using external sources like Odoo or Moodle.  

### Publication  
Publishing ensures that resources are properly packaged and distributed. The following features are available:  
- Places the material in local directories for organization.  
- Enables printing of the material.  
- Compresses the material into a publishable format.  
- Supports publishing to platforms such as Moodle.  


## Installation  

To install Teachkit, make sure you have Python 3.8 or higher installed on your system. Then, clone the repository and install the dependencies:  

```bash
git clone https://github.com/<your-username>/teachkit.git
cd teachkit
pip install -r requirements.txt

