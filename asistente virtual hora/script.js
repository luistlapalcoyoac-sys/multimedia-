function iniciar_reconocimiento() {
  const caja_entrada = document.getElementById('zona-texto-entrada');
  const caja_salida = document.getElementById('zona-texto-salida');

  // Inicialización de la API nativa de reconocimiento de voz
  const MotorReconocimiento = window.SpeechRecognition || window.webkitSpeechRecognition;
  const reconocedor = new MotorReconocimiento();
  
  // Configuración regional para asegurar correcta interpretación del acento
  reconocedor.lang = "es-MX";
  reconocedor.start();
  
  caja_entrada.innerHTML = "Escuchando...";

  reconocedor.onresult = function(evento) {
    // Normalización de la cadena capturada a minúsculas
    const texto_detectado = evento.results[0][0].transcript.toLowerCase().trim();
    console.log("Comando detectado: ", texto_detectado);
    caja_entrada.innerHTML = "Tú: " + texto_detectado;

    // Lógica de evaluación de intenciones del usuario
    if (texto_detectado.includes("hora")) {
      const momento_actual = new Date();
      
      // Formateo del objeto Date a una cadena de tiempo legible (12 horas)
      const parametros_formato = { hour: 'numeric', minute: 'numeric', hour12: true };
      const hora_legible = momento_actual.toLocaleTimeString('es-MX', parametros_formato);
      const respuesta_sistema = "La hora actual es " + hora_legible + ".";
      
      caja_salida.innerHTML = respuesta_sistema;
      sintetizar_voz(respuesta_sistema);

    } else if (texto_detectado.includes("hola") || texto_detectado.includes("saludos")) {
      const saludo = "¡Hola! ¿En qué puedo ayudarte?";
      caja_salida.innerHTML = saludo;
      sintetizar_voz(saludo);
      
    } else {
      const msj_error = "Comando no reconocido. Por favor, intenta de nuevo.";
      caja_salida.innerHTML = msj_error;
      sintetizar_voz(msj_error);
    }
  }
}

// Módulo encargado de la vocalización de las respuestas
function sintetizar_voz(mensaje) {
  if ('speechSynthesis' in window) {
    const locucion = new SpeechSynthesisUtterance(mensaje);
    locucion.lang = 'es-MX'; // Configuración del acento de la voz
    
    window.speechSynthesis.speak(locucion);
  } else {
    console.warn("La API de síntesis de voz no está soportada en este entorno.");
  }
}
