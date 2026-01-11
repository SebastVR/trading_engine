"""
Bedrock Service: Conexión con AWS Bedrock para IA Filter
Proporciona interfaz para comunicarse con modelos de LLM en AWS Bedrock
"""

import json
import logging
from typing import Optional, List, Dict, Any
import boto3

from app.config.settings import settings


logger = logging.getLogger(__name__)


class BedrockService:
    """Servicio para interactuar con AWS Bedrock."""

    def __init__(self):
        """Inicializa cliente de Bedrock con credenciales AWS."""
        self.client = None
        self.model_id = settings.BEDROCK_MODEL
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa el cliente de Bedrock con credenciales del .env."""
        try:
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                raise ValueError(
                    "Faltan credenciales AWS: AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY"
                )

            self.client = boto3.client(
                "bedrock-runtime",
                region_name=settings.AWS_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            logger.info(
                f"✅ Bedrock client inicializado | "
                f"Model: {self.model_id} | Region: {settings.AWS_REGION_NAME}"
            )

        except Exception as e:
            logger.error(f"❌ Error inicializando Bedrock: {str(e)}")
            raise

    def query_bedrock(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Realiza una query a Bedrock y retorna la respuesta.

        Args:
            prompt: Prompt/mensaje del usuario
            temperature: Control de creatividad (0-1). Default: AI_TEMPERATURE_FILTER
            max_tokens: Máximo de tokens en respuesta. Default: AI_MAX_TOKENS
            system_prompt: Instrucción del sistema (rol/comportamiento del modelo)

        Returns:
            Respuesta de texto del modelo
        """
        if not self.client:
            raise RuntimeError("Cliente de Bedrock no inicializado")

        temperature = temperature or settings.AI_TEMPERATURE_FILTER
        max_tokens = max_tokens or settings.AI_MAX_TOKENS

        try:
            # Construir mensajes para OpenAI OSS model en Bedrock
            # Nota: El modelo openai.gpt-oss-120b-1:0 NO soporta parámetro "system"
            # Incluimos el system prompt como parte del primer mensaje
            
            messages = []
            
            # Incluir system prompt en el primer mensaje si existe
            if system_prompt:
                combined_message = f"{system_prompt}\n\n{prompt}"
            else:
                combined_message = prompt
            
            messages.append({"role": "user", "content": combined_message})

            # Preparar payload según el formato de Bedrock (OpenAI OSS)
            body = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Llamar a Bedrock
            logger.info(f"📡 Enviando a Bedrock: {self.model_id}")
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )

            # Parsear respuesta
            response_body_str = response["body"].read().decode()
            logger.info(f"� Response status code OK")
            
            response_body = json.loads(response_body_str)

            if "choices" in response_body:
                # Formato OpenAI OSS (openai.gpt-oss-120b-1:0)
                choices = response_body["choices"]
                if isinstance(choices, list) and len(choices) > 0:
                    message = choices[0].get("message", {})
                    content = message.get("content", "")
                    logger.info(f"✅ Bedrock content extracted: {content[:200]}")
                    return content
            elif "content" in response_body:
                # Formato Anthropic Claude
                content = response_body["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", "")
            elif "completion" in response_body:
                # Algunos modelos usan "completion"
                return response_body["completion"]
            else:
                # Intenta extraer texto de forma genérica
                logger.warning(f"⚠️ Formato de respuesta no reconocido: {response_body}")
                return json.dumps(response_body)

        except Exception as e:
            logger.error(f"❌ Error llamando a Bedrock: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            raise

    def validate_json_response(self, response: str) -> Dict[str, Any]:
        """
        Intenta parsear respuesta como JSON, retorna dict si es válido.
        Extrae JSON de respuestas con tags <reasoning> o similares.

        Args:
            response: Respuesta de texto de Bedrock

        Returns:
            Dict parseado o levanta excepción
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Intenta extraer JSON de tags como <reasoning>...JSON...</reasoning>
            import re
            
            # Intentar encontrar cualquier JSON object válido
            # Buscar de atrás hacia adelante para encontrar el último JSON que es probablemente el válido
            for json_match in reversed(list(re.finditer(r'\{[^{}]*\}', response, re.DOTALL))):
                try:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    logger.info(f"✅ JSON extraído de tags ({len(json_str)} chars)")
                    return result
                except json.JSONDecodeError:
                    continue
            
            logger.error(f"❌ Response no es JSON válido: {str(e)}")
            raise ValueError(
                f"Bedrock retornó respuesta inválida (no JSON): respuesta no contiene JSON válido"
            )


# Instancia global del servicio
bedrock_service = BedrockService()
