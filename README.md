# Example component

<!-- no toc -->
- [Component description](#component-description)
- [Development steps](#development-steps)
- [Running test simulation](#running-test-simulation)

## Component description

The implemented component type is named SimpleComponent.

- The component takes three parameters as input when the component starts
    - `SimpleValue`, required float value, which is used to determine the value used in the output messages.
    - `InputComponents`, optional string value, which contains a comma-separated list of the other component names that provide input for this component. All the listed components are assumed to be other simple components. The default value is empty string, i.e. no components providing input.
    - `OutputDelay`, optional float value, which tells how many seconds to delay sending the output message after receiving all required input. The default value is 0.0, i.e. no delay.
- During each epoch, the component first waits input from other simple components and then sends an output message.
    - For the input and output messages, a new message type, Simple message, is used. It contains the AbstractResultMessage attributes with an additional SimpleValue attribute that contains a float value.
    - If the `InputComponents` list is empty, the output message is immediately send after receiving a new Epoch message (with the possible delay according to `OutputDelay`). Otherwise the output message is send after receiving all the required input messages.
    - The actual value for the attribute SimpleValue in the output message is determined by the following formula:

        ```text
        if <inputComponents list is not empty>:
            SimpleValue = <sum of the SimpleValues received from all input messages> +
                          <the SimpleValue given to the component at startup>
        else:
            SimpleValue = <the SimpleValue given to the component at startup> +
                          <epoch number divided by 1000>
       ```

    - The output message is sent to topic `SimpleTopic.<component_name>`.
    - The Status ready message is sent immediately after the output message.

## Development steps

This section documents the development steps taken during the development of this example component.
Note, that there are no unit tests implemented for this example component. Also, some of the function descriptions are still incomplete.

1. Create a Git repository at GitHub under the simcesplatform organization.
    - from [https://github.com/simcesplatform](https://github.com/simcesplatform) select `"New"`
    - for a new project, select `"Initialize repository with a README"`
2. Clone the Git repository locally.
    - from the platform installation folder

        ```bash
        git clone https://github.com/simcesplatform/Simple-Component.git
        # or if you are using SSH keys with GitHub
        git clone git@github.com:simcesplatform/Simple-Component.git
        ```

        where `Simple-Component` is the name of this repository

3. Initialize the submodule for simulation-tools library to utilize the Python library `simulation-tools`.

    ```bash
    # fetch and setup the library as a submodule
    git submodule add -b master https://github.com/simcesplatform/simulation-tools.git
    git submodule init
    git submodule update --remote --recursive

    # prepare the path for the submodule (to use tools.??? instead of simulation_tools.tools.???)
    cp -r simulation-tools/init .
    mkdir -p simple_component
    printf '"""Add submodules to the python path."""\n\nimport init\n' > simple_component/__init__.py
    ```

4. Create the message class, [simple_component/simple_message.py](simple_component/simple_message.py), based on the message template from [message_template.txt](https://github.com/simcesplatform/simulation-tools/blob/master/message_template.txt).
5. Create the component code, [simple_component/simple_component.py](simple_component/simple_component.py), based on the component template from [component_template.py](https://github.com/simcesplatform/simulation-tools/blob/master/examples/component_template.py).
6. Create the Dockerfile, [Dockerfile](Dockerfile), based on the Dockerfile template from [Dockerfile-template](https://github.com/simcesplatform/platform-manager/blob/master/instructions/Dockerfile-template).
7. Include the required Python libraries file, [requirements.txt](requirements.txt), based on the template file [requirements.txt](https://github.com/simcesplatform/platform-manager/blob/master/instructions/requirements.txt).
8. Create this readme file with a descriptions about the new component and its workflow. For actual component create also a documentation page for the component.
9. Create a configuration file for a test simulation that contains the newly created component.
    - The created test simulation configuration file for this simple component, [simple_simulation.yml](simple_simulation.yml), contains four components that work similarly as the components on the documentation page [Time and synchronization with epochs](https://simcesplatform.github.io/core_time/)
10. Build and push a Docker image to the Container registry following the relevant instructions. (TODO: add the actual instructions here)
11. Test the component by running a test simulation.

## Running test simulation

TODO: add steps to follow to install the platform and to run the simple component test simulation based on the general instructions.
<!--
Follow the instruction steps from [https://wiki.eduuni.fi/display/tuniSimCES/Running+a+simulation#Runningasimulation-Preparationsforanewsimulation](https://wiki.eduuni.fi/display/tuniSimCES/Running+a+simulation#Runningasimulation-Preparationsforanewsimulation).

1. Install the simple component code

    ```bash
    git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/simple-component.git
    ```

2. Add the simple component to the `docker-compose-domain-build.yml` file in the `platform-manager/build/domain` folder. The context path is given here as a relative path from the `platform_manager/build/domain` folder.

    ```yaml
    simple-component:
        image: simple-component:0.1
        build:
            context: ../../../simple-component
            dockerfile: Dockerfile
    ```

3. Build the Docker images for the domain components including the newly added simple component by using the following command from the `platform-manager` folder.

    ```bash
    source platform_domain_setup.sh
    ```

4. Add `SimpleComponent` section to the `supported_components_domain.json`file in the `platform-manager`folder.

    ```json
    "SimpleComponent":
    {
        "Type": "dynamic",
        "Description": "Simple component",
        "DockerImage": "simple-component:0.1",
        "Attributes":
        {
            "SimpleValue":
            {
                "Environment": "SIMPLE_VALUE",
                "Optional": false
            },
            "InputComponents":
            {
                "Environment": "INPUT_COMPONENTS",
                "Optional": true,
                "Default": ""
            },
            "OutputDelay":
            {
                "Environment": "OUTPUT_DELAY",
                "Optional": true,
                "Default": 0.0
            }
        }
    }
    ```

5. Update Platform manager Docker image to include the new component type  by using the following command from the `platform-manager` folder.

    ```bash
    source platform_core_setup.sh
    ```

6. Copy the simulation configuration file to the `platform-component` folder by using the following command from the `platform-manager` folder.

    ```bash
    cp ../simple-component/simple_simulation.yml .
    ```

7. Run the test simulation by using the following commands from the `platform-manager` folder.

    ```bash
    source start_simulation.sh simple_simulation.yml
    ```
-->
