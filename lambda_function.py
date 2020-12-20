# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

import af

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hey, Saathi - Your travel assistant here! How may I help you?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class LocateMeIntentHandler(AbstractRequestHandler):
    """Handler for Locate Me Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LocateMeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = af.get_location()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class AboutPlaceIntentHandler(AbstractRequestHandler):
    """Handler for About Place Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AboutPlaceIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = af.get_resolved_value(handler_input.request_envelope.request, "city")
        if query is None:
            query = af.get_location()
        
        speak_output = af.get_city_info(query)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class RoadInfoIntentHandler(AbstractRequestHandler):
    """Handler for Road Info Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RoadInfoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = af.get_resolved_value(handler_input.request_envelope.request, "area")
        if query is None:
            query = af.get_geocode(query)
        
        speak_output = af.get_road_info(query)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class PlaceWeatherIntentHandler(AbstractRequestHandler):
    """Handler for Place Weather Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PlaceWeatherIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        place_query = af.get_resolved_value(handler_input.request_envelope.request, "place")
        session_query = af.get_resolved_value(handler_input.request_envelope.request, "session")
        
        if place_query is None:
            place_query = af.get_location()

        if session_query is None:
            session_query = 'now'
            
        
        speak_output = af.get_weather(place_query, session_query)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SearchNearbyIntentHandler(AbstractRequestHandler):
    """Handler for Search Nearby Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SearchNearbyIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        locality_query = af.get_resolved_value(handler_input.request_envelope.request, "locality")
        entity_query = af.get_resolved_value(handler_input.request_envelope.request, "entity")
        
        locality_query = af.get_geocode(locality_query)
        if locality_query is None:
            return af.default_response()
        else:
            speak_output = af.get_nearby_entities(locality_query, entity_query)
            return (handler_input.response_builder
                    .speak(speak_output)
                    .response)


class TimeSearchIntentHandler(AbstractRequestHandler):
    """Handler for Time Search Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TimeSearchIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        city_query = af.get_resolved_value(handler_input.request_envelope.request, "town")
        duration_query = af.get_resolved_value(handler_input.request_envelope.request, "duration")
        bank_query = af.get_resolved_value(handler_input.request_envelope.request, "bank")
        hosp_query = af.get_resolved_value(handler_input.request_envelope.request, "hospital")
        prkg_query = af.get_resolved_value(handler_input.request_envelope.request, "parking")
        shop_query = af.get_resolved_value(handler_input.request_envelope.request, "shop")
        mvtr_query = af.get_resolved_value(handler_input.request_envelope.request, "theater")
        atrx_query = af.get_resolved_value(handler_input.request_envelope.request, "attraction")
        hotl_query = af.get_resolved_value(handler_input.request_envelope.request, "hotel")
        
        ent_query = []
        if bank_query is not None:
            ent_query.append('BanksAndCreditUnions')
        if hosp_query is not None:
            ent_query.append('Hospitals')
        if prkg_query is not None:
            ent_query.append('Parking')
        if shop_query is not None:
            ent_query.append('Shop')
        if mvtr_query is not None:
            ent_query.append('MovieTheaters')
        if atrx_query is not None:
            ent_query.append('SeeDo')
        if hotl_query is not None:
            ent_query.append('HotelsAndMotels,EatDrink')
        
        if len(ent_query):
            ent_query = ','.join(map(str,ent_query))
        else:
            ent_query = None
        
        if duration_query is None:
            return af.default_response()
        
        else:
            if city_query is None:
                city_query = af.get_geocode(city_query)
            speak_output = af.get_entities(ent_query, city_query, duration_query)
            return (handler_input.response_builder
                .speak(speak_output)
                .response)


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Ask for info about a place, weather there, or say recommend a tourist place or locate me."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Ok, see you! Happy travel."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Thank you! Happy travel."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return (ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        _ = handler_input.attributes_manager.request_attributes["_"]
        
        speech = "I can't help you with that. If you say tell me about this place, I can help you learn about it. What can I help you with?"
        handler_input.response_builder.speak(_(speech)).ask(_(speech))

        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )



sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(LocateMeIntentHandler())
sb.add_request_handler(AboutPlaceIntentHandler())
sb.add_request_handler(RoadInfoIntentHandler())
sb.add_request_handler(PlaceWeatherIntentHandler())
sb.add_request_handler(SearchNearbyIntentHandler())
sb.add_request_handler(TimeSearchIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
