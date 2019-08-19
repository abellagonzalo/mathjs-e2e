# Mathjs Python Test Framework

This repo is an example of end-2-end test for a calculator rest service. I have focus the testing on the http layer
rather than the logic in the calculator, i.e. the operations itself. I would assume there are unit tests to cover all
the different combinations for the all the available operations. The framework would allow to easily create more tests
if it was necessary to cover those cases.

The "framework" is a pytest fixture which allows the user to call get and post methods. The base url of the service is
configurable through an environment variable 'MATHJS_BASE_URL' or variables explicitly defined in the tests. The value
in the environment variable have precedence over the explicit variables. Another option is to have a configuration file
in an easy to read format, such as json, for the same purpose. Although no code has been written for such scenario.

All code has been written in the same file for simplicity. Different Test classes and test fixtures should be written
in different files and grouped by functionality.

## How to run it

I assume the reviewer has a full python3 environment installed and Makefile. 

``` bash
make setup    # Create and activate virtualenv
make install  # Install packages with pip
make tests    # Run tests with pytest
```

