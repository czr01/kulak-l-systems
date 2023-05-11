# L-Systems

**Python application for processing and rendering L-Systems.**

## Installation

```console
# clone the repo
$ git clone https://github.com/czr01/kulak-l-systems.git

# change the working directory
$ cd kulak-l-systems

# install the requirements
$ python3 -m pip install -r requirements.txt
```

## Usage

```console
python3 lsystems [--export <filename>]
```

## L-System Configuration

The configuration of an L-System is described in a JSON file and follows strict guidelines. 

### Example

Example of the L-System configuration describing the Koch Curve.

```
{
    "variables" : ["F"],
    "constants" : ["+","-"],
    "axiom" : "F",
    "rules" : {
        "F" : "F+F-F-F+F"
    },
    "translations" : {
        "F" : "draw 20",
        "+" : "angle 90",
        "-" : "angle -90"
    }
}
```

### Data Types

- **variables**: list of strings
- **constants**: list of strings
- **axiom**: string
- **rules**: dictionary with string:string key-value pairs or string:list(list(float, string)) key-value pairs.
- **translations**: dictionary with string:string key-value pairs
- **width** *(optional)*: integer

### Contraints

- Variables must not be empty.
- Variables and constants must have no overlapping symbols.
- Axiom must include at least one variable.
- Axiom must have no undefined symbols.
- Every variable must have one corresponding rule.
- Every rule expansion string must have no undefined symbols.
- Every symbol must have one corresponding translation.
- Every translation must be supported.
- Width must be positive integer.

### Supported Translations

- ```forward <amount>```: Move forward by given amount without drawing a line.
- ```draw <amount>```: Draw a line of given amount long.
- ```angle <amount>```: Turn given amount of degrees to the left.
- ```color <color>```: Change the color to the given color.
- ```push```: Push the current drawing state (position, angle, color) on the stack.
- ```pop```: Replace the current drawing state with the one on top of the stack.
- ```nop```: Do nothing.

### Additional Notes

- The ```color``` translation supports color names (red, orange, ...) as well as RGB-values (```color 112 255 13```) and hexadecimal color values (```color #daca00```).
- The ```width``` attribute is optional. If left undefined in the L-System configuration file, it defaults to 1.
- The ```demo/``` folder includes multiple popular L-Systems for experimentation.

## Docker Notes

If docker is installed you can build an image and run this as a container.

```
docker build -t mylsystems-image .
```

Once the image is built, the app can be run by running the following:

```
docker run -p 5000:5000 mylsystems-image
```
