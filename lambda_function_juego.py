# -*- coding: utf-8 -*-

# This is a CODA ADL Watching TV Skill, built using
# the implementation of handler classes approach in skill builder.
import logging
from random import randint

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.dialog_state import DialogState
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from ask_sdk_model.dialog import (
    ElicitSlotDirective, DelegateDirective)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FRASES_HECHAS = {
    'SECUENCIA_INCORRECTA': 'necesitas proporcionar una secuencia con esta forma x-x-x donde x es un número',
    'NOMBRE_SKILL': 'CODA',
    'MENSAJE_BIENVENIDA' : ['hola, ¿vas a ver la tele?',
    						'hola, creo que vas a ver la televisión un rato, ¿verdad?',
    						'¿qué tal? ¿Ves la tele un rato?'],
    'PUEDO_AYUDARTE' : [' ¿Vas a ver una película, una serie, un documental o las noticias?',
                        ' ¿Te apetece ver una película, una serie, un documental o las noticias?',
                        ' ¿Una película, una serie, un documental o las noticias?']
        
}
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response        
        logger.info("En LaunchRequestHandler")
        
        speech_text = FRASES_HECHAS['MENSAJE_BIENVENIDA'][randint( 0, len(FRASES_HECHAS['MENSAJE_BIENVENIDA'])-1 )]
        ayuda = FRASES_HECHAS['PUEDO_AYUDARTE'][randint( 0, len(FRASES_HECHAS['PUEDO_AYUDARTE'])-1 )]
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("CODA ADL Watching TV", speech_text)).ask(ayuda).set_should_end_session(
            False)
        return handler_input.response_builder.response

class AyudaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AyudaIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = (
            "Voy a decir algunos números. Escucha con atención y cuando yo haya terminado, "
            "repítalo inmediatamente. Puedes jugar al minijuego secuencia de números, número al reves, "
            "letras y palabras o familia de palabras. Si necesitas saber cómo se juega, ¡pregúntame!"
        )

        handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response

class GameModerator:
    def __init__(self):
        self.current_sequence = None
        self.current_group = 1
        self.score = 0

    def start_new_game(self):
        self.current_sequence = self.generate_random_sequence(3)
        self.current_group = 1
        self.score = 0

    def generate_random_sequence(self,num_elements):
        random_integers = [str(randint(0, 9)) for _ in range(num_elements)]
        sequence = "-".join(random_integers)
        return sequence
    
    def current_sequence_num(self):
        # Most likely minimum num is gonna be 3
        if self.current_sequence:
            return len(self.current_sequence.split('-'))
        return 0
    def validate_user_repetition(self, user_response):
        if user_response == self.current_sequence:
            if len(self.score) < len(self.current_sequence):
                # Even tho , it always gonna have a larger length 
                # because each time we add a number to the sequence starting from sequence number = 3
                self.score = len(self.current_sequence)
            return True
        return False

    def switch_to_group_2(self):
        self.current_group = 2

    def switch_to_next_series(self):
        self.current_group = 1
        self.current_sequence = self.generate_random_sequence(
            self.current_sequence_num()
        )
        
    def validate_sequence(self, sequence):
        seq_split = sequence.split('-')
        for x in seq_split:
            if not x or not x.isdigit():
                return False
        return True
    def get_current_group(self):
        return self.current_group

moderator = GameModerator()

class EmpezarJuegoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("EmpezarJuegoIntent")(handler_input)

    def handle(self, handler_input):
        moderator.start_new_game()
        speech_text = f"¡Genial! Empezamos: {moderator.current_sequence}"
        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class RepeatingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("RepitiendoIntent")(handler_input) \
            and handler_input.request_envelope.request.dialog_state !=  DialogState.COMPLETED 
             
    def handle(self, handler_input):
        sequence = None
        if (handler_input.request_envelope.request.intent.slots["NumSequenceType"] \
            and handler_input.request_envelope.request.intent.slots["NumSequenceType"].value ):
            sequence = handler_input.request_envelope.request.intent.slots["NumSequenceType"].value

        if not sequence or not moderator.validate_sequence(sequence):
            speech_text = FRASES_HECHAS['SECUENCIA_INCORRECTA']
        if moderator.validate_user_repetition(sequence):
            speech_text = "Correcto ahora : " + moderator.switch_to_next_series()
        else:
            if moderator.get_current_group == 2:
                speech_text = "juegos perdidos"
            else:
                next_sequence = moderator.switch_to_group_2()
                speech_text = f"secuencia incorrecta ahora grupo 2: {next_sequence}"

        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response


class EndGameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("EndGameIntent")(handler_input)
    def handle(self,handler_input):
        pass
    
class CODAADLWatchingTVNewsOrReportIntentHandler(AbstractRequestHandler):
    """Handler for CODA ADL WatchingTV Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CODA_ADL_WatchingTV_queves")(handler_input) \
        and handler_input.request_envelope.request.dialog_state !=  DialogState.COMPLETED \
        and   handler_input.request_envelope.request.intent.slots["SI_NO"].value!='no' \
        and   handler_input.request_envelope.request.intent.slots["TV_program"].value  \
        and   (handler_input.request_envelope.request.intent.slots["TV_program"].resolutions.resolutions_per_authority[0].values[0].value.id=='news'
     ,num_elements          or handler_input.request_envelope.request.intent.slots["TV_program"].resolutions.resolutions_per_authority[0].values[0].value.id=='tv_report')
    def handle(self, handler_input):
        print('news or report handler')
        intentRequest=handler_input.request_envelope.request.intent
        if (not intentRequest.slots["SI_NO"].value):
            intentRequest.slots["SI_NO"].value='si'
        return handler_input.response_builder.add_directive(DelegateDirective(intentRequest)).response


class CODAADLWatchingTVMovieIntentHandler(AbstractRequestHandler):
    """Handler for CODA ADL WatchingTV Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CODA_ADL_WatchingTV_queves")(handler_input) \
        and handler_input.request_envelope.request.dialog_state !=  DialogState.COMPLETED \
        and   handler_input.request_envelope.request.intent.slots["SI_NO"].value!='no' \
        and   handler_input.request_envelope.request.intent.slots["TV_program"].value  \
        and   handler_input.request_envelope.request.intent.slots["TV_program"].resolutions.resolutions_per_authority[0].values[0].value.id=='movie'  \
        and   not handler_input.request_envelope.request.intent.slots["TV_movie_name"].value
    def handle(self, handler_input):
        print('movie handler')
        intentRequest=handler_input.request_envelope.request.intent
        if (not intentRequest.slots["SI_NO"].value):
            intentRequest.slots["SI_NO"].value='si'
        handler_input.response_builder.add_directive(ElicitSlotDirective(updated_intent=intentRequest,slot_to_elicit = "TV_movie_name")).speak("¿Cómo se llama la película que vas a ver?").ask("¿Cómo se llama la película que vas a ver?")
        return handler_input.response_builder.response


class CODAADLWatchingTVSerieIntentHandler(AbstractRequestHandler):
    """Handler for CODA ADL WatchingTV Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CODA_ADL_WatchingTV_queves")(handler_input) \
        and handler_input.request_envelope.request.dialog_state !=  DialogState.COMPLETED \
        and   handler_input.request_envelope.request.intent.slots["SI_NO"].value!='no' \
        and   handler_input.request_envelope.request.intent.slots["TV_program"].value  \
        and   handler_input.request_envelope.request.intent.slots["TV_program"].resolutions.resolutions_per_authority[0].values[0].value.id=='tv_serie' \
        and   not handler_input.request_envelope.request.intent.slots["TV_serie_name"].value
    def handle(self, handler_input):
        print('report handler')
        intentRequest=handler_input.request_envelope.request.intent
        if (not intentRequest.slots["SI_NO"].value):
            intentRequest.slots["SI_NO"].value='si'
        handler_input.response_builder.add_directive(ElicitSlotDirective(updated_intent=intentRequest,slot_to_elicit = "TV_serie_name")).speak("¿Cómo se llama la serie que vas a ver?").ask("¿Cómo se llama la serie que vas a ver?")
        return handler_input.response_builder.response

class CODAADLWatchingTVIntentHandler(AbstractRequestHandler):
    """Handler for CODA ADL WatchingTV Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CODA_ADL_WatchingTV_queves")(handler_input) 
    def handle(self, handler_input):
        intentRequest=handler_input.request_envelope.request.intent
        print('default handler')
        handler_input.response_builder.add_directive(DelegateDirective())
        return handler_input.response_builder.response

class CODAADLWatchingTVEndIntentHandler(AbstractRequestHandler):
    """Handler for CODA ADL WatchingTV Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CODA_ADL_WatchingTV_queves")(handler_input) \
        and (handler_input.request_envelope.request.dialog_state ==  DialogState.COMPLETED \
        or (handler_input.request_envelope.request.dialog_state !=  DialogState.COMPLETED \
        and handler_input.request_envelope.request.intent.slots["SI_NO"].value=='no'))
    
    def handle(self, handler_input):
        print("COMPLETADO")
        if (handler_input.request_envelope.request.intent.slots["SI_NO"].value=='si'):
            if (handler_input.request_envelope.request.intent.slots["TV_serie_name"].value):
                visto=handler_input.request_envelope.request.intent.slots["TV_serie_name"].value
            elif (handler_input.request_envelope.request.intent.slots["TV_movie_name"].value):
                visto=handler_input.request_envelope.request.intent.slots["TV_movie_name"].value
            else:
                visto=handler_input.request_envelope.request.intent.slots["TV_program"].resolutions \
                .resolutions_per_authority[0].values[0].value.name
            speech_text = "Espero que hayas disfrutado de "+ visto
        else:
            speech_text = 'Mejor leer un libro ¡Hasta luego!'
         
        handler_input.response_builder.speak(speech_text).set_card(SimpleCard("CODA ADL Watching TV", speech_text)) \
        .set_should_end_session(True)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Prueba a preguntar qué hay en la tele"

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard(
                "CODA ADL Watching TV help", speech_text))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "¡Adios!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("CODA ADL Watching TV bye", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The CODA skill can't help you with that.  "
            "You can say hello!!")
        reprompt = "You can say hello!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("En Session end")
        speech_text = "¡Adios!"
            
        reprompt = "Hasta luego"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        logger.info("En error")
        speech = "Vaya, parece que hubo un problema, lo siento. Prueba a decir coda tele"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CODAADLWatchingTVEndIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(CODAADLWatchingTVMovieIntentHandler())
sb.add_request_handler(CODAADLWatchingTVSerieIntentHandler())
sb.add_request_handler(CODAADLWatchingTVNewsOrReportIntentHandler())
sb.add_request_handler(CODAADLWatchingTVIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())



lambda_handler = sb.lambda_handler()