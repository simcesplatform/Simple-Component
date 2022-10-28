# -*- coding: utf-8 -*-
# Copyright 2021 Tampere University and VTT Technical Research Centre of Finland
# This software was developed as a part of the ProCemPlus project: https://www.senecc.fi/projects/procemplus
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Ville Heikkilä <ville.heikkila@tuni.fi>

"""
Module containing a template for a simulation platform component,
"""

import asyncio
from typing import Any, cast, Set, Union

from tools.components import AbstractSimulationComponent
from tools.exceptions.messages import MessageError
from tools.messages import BaseMessage
from tools.tools import FullLogger, load_environmental_variables, log_exception

# import all the required messages from installed libraries
from simple_component.simple_message import SimpleMessage

# initialize logging object for the module
LOGGER = FullLogger(__name__)

# set the names of the used environment variables to Python variables
SIMPLE_VALUE = "SIMPLE_VALUE"
INPUT_COMPONENTS = "INPUT_COMPONENTS"
OUTPUT_DELAY = "OUTPUT_DELAY"

SIMPLE_TOPIC = "SIMPLE_TOPIC"

# time interval in seconds on how often to check whether the component is still running
TIMEOUT = 1.0


class SimpleComponent(AbstractSimulationComponent):
    """
    Description for the SimpleComponent.
    # TODO: add proper description specific for this component.
    """

    # The constructor for the component class.
    # This example shows three parameters given to the component at the constructor
    # These should be adjusted to fit the actual component in development.
    def __init__(
            self,
            simple_value: float,
            input_components: Set[str],
            output_delay: float):
        """
        Description for the constructor including descriptions for the parameters.
        TODO: add proper description specific for this component.

        - number_value (float): value to add to the output message SimpleValue attribute
        - input_components (Set[str]): set of the components names that provides input
        """

        # Initialize the AbstractSimulationComponent using the values from the environmental variables.
        # This will initialize various variables including the message client for message bus access.
        super().__init__()

        # Set the object variables for the extra parameters.
        self._simple_value = simple_value
        self._input_components = input_components
        self._output_delay = output_delay

        # Add checks for the parameters if necessary
        # and set initialization error if there is a problem with the parameters.
        # if <some_check_for_the_parameters>:
        #     # add appropriate error message
        #     self.initialization_error = "There was a problem with the parameters"
        #     LOGGER.error(self.initialization_error)

        # variables to keep track of the components that have provided input within the current epoch
        # and to keep track of the current sum of the input values
        self._current_number_sum = 0.0
        self._current_input_components = set()

        # Load environmental variables for those parameters that were not given to the constructor.
        # In this template the used topics are set in this way with given default values as an example.
        environment = load_environmental_variables(
            (SIMPLE_TOPIC, str, "SimpleTopic")
        )
        self._simple_topic_base = cast(str, environment[SIMPLE_TOPIC])
        self._simple_topic_output = ".".join([self._simple_topic_base, self.component_name])

        # The easiest way to ensure that the component will listen to all necessary topics
        # is to set the self._other_topics variable with the list of the topics to listen to.
        # Note, that the "SimState" and "Epoch" topic listeners are added automatically by the parent class.
        self._other_topics = [
            ".".join([self._simple_topic_base, other_component_name])
            for other_component_name in self._input_components
        ]

        # The base class contains several variables that can be used in the child class.
        # The variable list below is not an exhaustive list but contains the most useful variables.

        # Variables that should only be READ in the child class:
        # - self.simulation_id               the simulation id
        # - self.component_name              the component name
        # - self._simulation_state           either "running" or "stopped"
        # - self._latest_epoch               epoch number for the current epoch
        # - self._completed_epoch            epoch number for the latest epoch that has been completed
        # - self._latest_epoch_message       the latest epoch message as EpochMessage object

        # Variable for the triggering message ids where all relevant message ids should be appended.
        # The list is automatically cleared at the start of each epoch.
        # - self._triggering_message_ids

        # MessageGenerator object that can be used to generate the message objects:
        # - self._message_generator

        # RabbitmqClient object for communicating with the message bus:
        # - self._rabbitmq_client

    def clear_epoch_variables(self) -> None:
        """Clears all the variables that are used to store information about the received input within the
           current epoch. This method is called automatically after receiving an epoch message for a new epoch.

           NOTE: this method should be overwritten in any child class that uses epoch specific variables
        """
        self._current_number_sum = 0.0
        self._current_input_components = set()

    async def process_epoch(self) -> bool:
        """
        Process the epoch and do all the required calculations.
        Assumes that all the required information for processing the epoch is available.

        Returns False, if processing the current epoch was not yet possible.
        Otherwise, returns True, which indicates that the epoch processing was fully completed.
        This also indicated that the component is ready to send a Status Ready message to the Simulation Manager.

        NOTE: this method should be overwritten in any child class.
        TODO: add proper description specific for this component.
        """

        # set the number value used in the output message
        if self._current_input_components:
            self._current_number_sum = round(self._current_number_sum + self._simple_value, 3)
        else:
            self._current_number_sum = round(self._simple_value + self._latest_epoch / 1000, 3)

        # send the output message
        await asyncio.sleep(self._output_delay)
        await self._send_simple_message()

        # return True to indicate that the component is finished with the current epoch
        return True

    async def all_messages_received_for_epoch(self) -> bool:
        """
        Returns True, if all the messages required to start calculations for the current epoch have been received.
        Checks only that all the required information is available.
        Does not check any other conditions like the simulation state.

        NOTE: this method should be overwritten in any child class that needs more
        information than just the Epoch message.
        TODO: add proper description specific for this component.
        """
        return self._input_components == self._current_input_components

    async def general_message_handler(self, message_object: Union[BaseMessage, Any],
                                      message_routing_key: str) -> None:
        """
        Handles the incoming messages. message_routing_key is the topic for the message.
        Assumes that the messages are not of type SimulationStateMessage or EpochMessage.

        NOTE: this method should be overwritten in any child class that
        listens to messages other than SimState or Epoch messages.
        TODO: add proper description specific for this component.
        """
        if isinstance(message_object, SimpleMessage):
            # added extra cast to allow Pylance to recognize that message_object is an instance of SimpleMessage
            message_object = cast(SimpleMessage, message_object)
            # ignore simple messages from components that have not been registered as input components
            if message_object.source_process_id not in self._input_components:
                LOGGER.debug(f"Ignoring SimpleMessage from {message_object.source_process_id}")

            # only take into account the first simple message from each component
            elif message_object.source_process_id in self._current_input_components:
                LOGGER.info(f"Ignoring new SimpleMessage from {message_object.source_process_id}")

            else:
                self._current_input_components.add(message_object.source_process_id)
                self._current_number_sum = round(self._current_number_sum + message_object.simple_value, 3)
                LOGGER.debug(f"Received SimpleMessage from {message_object.source_process_id}")

                self._triggering_message_ids.append(message_object.message_id)
                if not await self.start_epoch():
                    LOGGER.debug(f"Waiting for other input messages before processing epoch {self._latest_epoch}")

        else:
            LOGGER.debug("Received unknown message from {message_routing_key}: {message_object}")

    async def _send_simple_message(self):
        """
        Sends a SimpleMessage using the self._current_number_sum as the value for attribute SimpleValue.
        """
        try:
            simple_message = self._message_generator.get_message(
                SimpleMessage,
                EpochNumber=self._latest_epoch,
                TriggeringMessageIds=self._triggering_message_ids,
                SimpleValue=self._current_number_sum
            )

            await self._rabbitmq_client.send_message(
                topic_name=self._simple_topic_output,
                message_bytes=simple_message.bytes()
            )

        except (ValueError, TypeError, MessageError) as message_error:
            # When there is an exception while creating the message, it is in most cases a serious error.
            log_exception(message_error)
            await self.send_error_message("Internal error when creating result message.")


def create_component() -> SimpleComponent:
    """
    Creates and returns a SimpleComponent based on the environment variables.

    TODO: add proper description specific for this component.
    """

    # Read the parameters for the component from the environment variables.
    environment_variables = load_environmental_variables(
        (SIMPLE_VALUE, float, 1.0),   # the value to be added for SimpleValue attribute
        (INPUT_COMPONENTS, str, ""),  # the comma-separated list of component names that provide input
        (OUTPUT_DELAY, float, 0.0)    # delay in seconds before sending the result message for the epoch
    )

    # The cast function here is only used to help Python linters like pyright to recognize the proper type.
    # They are not necessary and can be omitted.
    simple_value = cast(float, environment_variables[SIMPLE_VALUE])
    # put the input components to a set, only consider component with non-empty names
    input_components = {
        input_component
        for input_component in cast(str, environment_variables[INPUT_COMPONENTS]).split(",")
        if input_component
    }
    output_delay = cast(float, environment_variables[OUTPUT_DELAY])

    # Create and return a new SimpleComponent object using the values from the environment variables
    return SimpleComponent(
        simple_value=simple_value,
        input_components=input_components,
        output_delay=output_delay
    )


async def start_component():
    """
    Creates and starts a SimpleComponent component.
    """
    # A general exception handler that should catch any unhandled error that would otherwise crash the program.
    # Having this might be especially useful when testing components in large simulations and some component(s)
    # crash without giving any output.
    #
    # Note, that any exceptions thrown in async functions will not be caught here.
    # Instead they should get logged as warnings but otherwise should not crash the component.
    try:
        simple_component = create_component()

        # The component will only start listening to the message bus once the start() method has been called.
        await simple_component.start()

        # Wait in the loop until the component has stopped itself.
        while not simple_component.is_stopped:
            await asyncio.sleep(TIMEOUT)

    except BaseException as error:  # pylint: disable=broad-except
        log_exception(error)
        LOGGER.info("Component will now exit.")


if __name__ == "__main__":
    asyncio.run(start_component())
