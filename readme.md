# TD Family Injector
## Version 1.011
### Author: Arnaud Cassone © Artcraft Visuals
A TouchDesigner operator family injector tool that helps manage and inject custom operator families into TouchDesigner projects.
It adds operators directly into the Op Menu for easy access in a new "custom" section with predefined name and color.

Originally designed by Tekt for Raytk and modified by DotSimulate for Lops then adapted for general use by me.

## features:
- Inject custom operator families into TouchDesigner projects
- Add operators to the Op Menu under a "custom" section
- Define family name and color for easy identification
- Organize operators into categories using annotate containers
- Simple installation and uninstallation process


## Usage:
- Clone the repository in your prefered folder
- Drag and drop the TOX files in your TD project. (it will move it to the root of your project)
- Enter the family name and color in the parameters
- Put your custom operators in the "custom_operators" container inside the Operator Network
- All Operators must be inside the Main Operators annotate container.
- Each subcategory must be inside a Category annotate container.
- Click "Family Install" to add the operators to the Op Menu
- Access the components from the Op Menu under the given name.

## notes
- Ensure that all operator names are unique within their family.
- Test the installation in a separate TouchDesigner project before deploying it in a production environment.
- Multiple families can be installed by drag and dropping the Family Injector TOX and changing the family name and color.

## Parameters
| Parameter | Type | Description |
|----------------------|------|---------------------------------|
|Install|Toggle||
|Verbose|Toggle||
|Createstubs|Pulse||
|Replacestubs|Pulse||
|Updateall|Pulse||
|Family|Str||
|Colorr|RGB||
|Colorg|RGB||
|Colorb|RGB||
|Index|Int||