# Generic GUI for firmware programming

A generic utility for building firmware images and programming them onto microcontrollers.

The tool provides the user with a way to:
* Clone and update a repository
* Checkout a tag, branch or commit from the repository
* Specify scripts for building and programming
* Specify build options and letting a user select and/or fill-in the options

# Installation

- Clone the repository
- Cd into the repository
- python3 -m venv venv
- source venv/bin/activate
- pip3 install -r requirements.txt
- Update settings.json (directly or by editing and running jsonbuilder.py)
- ./run
