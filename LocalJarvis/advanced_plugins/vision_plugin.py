"""
Plugin de Visão Computacional Avançado
Funções: reconhecimento de objetos, detecção de faces, classificação de imagens, processamento de vídeo
"""

import cv2
import numpy as np
import os
import base64
import io
from PIL import Image
import logging
from typing import List, Dict, Tuple, Optional, Any
import requests
import tempfile

logger = logging.getLogger(__name__)

class VisionPlugin:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.temp_dir = "temp/vision"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Configurações
        self.use_opencv = self.config.get('use_opencv', True)
        self.use_face_detection = self.config.get('use_face_detection', True)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.5)
        
        # Carrega modelos se disponíveis
        self._load_models()
        
        logger.info("VisionPlugin inicializado")

    def _load_models(self):
        """Carrega modelos de visão computacional."""
        self.face_cascade = None
        self.object_detector = None
        
        try:
            # Carrega classificador de faces do OpenCV
            if self.use_face_detection:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if os.path.exists(cascade_path):
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    logger.info("Modelo de detecção de faces carregado")
                else:
                    logger.warning("Arquivo de cascata de faces não encontrado")
            
            # Tenta carregar modelo YOLO (se disponível)
            self._try_load_yolo()
            
        except Exception as e:
            logger.warning(f"Erro ao carregar modelos: {e}")

    def _try_load_yolo(self):
        """Tenta carregar modelo YOLO para detecção de objetos."""
        try:
            # Caminhos para arquivos YOLO (você precisará baixar estes arquivos)
            yolo_weights = "models/yolov3.weights"
            yolo_config = "models/yolov3.cfg"
            yolo_classes = "models/coco.names"
            
            if all(os.path.exists(f) for f in [yolo_weights, yolo_config, yolo_classes]):
                self.yolo_net = cv2.dnn.readNet(yolo_weights, yolo_config)
                with open(yolo_classes, 'r') as f:
                    self.yolo_classes = [line.strip() for line in f.readlines()]
                logger.info("Modelo YOLO carregado com sucesso")
            else:
                logger.info("Arquivos YOLO não encontrados, usando detecção básica")
                
        except Exception as e:
            logger.warning(f"Erro ao carregar YOLO: {e}")

    def process(self, text: str) -> Optional[str]:
        """Processa comandos de visão computacional."""
        text_lower = text.lower().strip()
        
        # Comandos de detecção
        if any(word in text_lower for word in ['reconhece', 'detectar', 'identifica']):
            if 'objeto' in text_lower or 'coisa' in text_lower:
                return self._handle_object_detection(text)
            elif 'face' in text_lower or 'rosto' in text_lower or 'pessoa' in text_lower:
                return self._handle_face_detection(text)
            else:
                return self._handle_general_detection(text)
        
        # Comandos de análise
        elif any(word in text_lower for word in ['analisa', 'classifica', 'descreve']):
            return self._handle_image_analysis(text)
        
        # Comandos de câmera
        elif any(word in text_lower for word in ['câmera', 'camera', 'foto', 'captura']):
            return self._handle_camera_command(text)
        
        # Comandos de vídeo
        elif any(word in text_lower for word in ['vídeo', 'video', 'stream']):
            return self._handle_video_command(text)
        
        return None

    def _handle_object_detection(self, text: str) -> str:
        """Lida com detecção de objetos."""
        if 'câmera' in text.lower() or 'tempo real' in text.lower():
            return self._detect_objects_camera()
        else:
            return "🔍 Para detectar objetos, use: 'detectar objetos na câmera' ou envie uma imagem."

    def _handle_face_detection(self, text: str) -> str:
        """Lida com detecção de faces."""
        if 'câmera' in text.lower():
            return self._detect_faces_camera()
        else:
            return "👤 Para detectar faces, use: 'detectar faces na câmera' ou envie uma imagem."

    def _handle_general_detection(self, text: str) -> str:
        """Detecção geral."""
        return "👁️ Posso detectar: objetos, faces, pessoas. Especifique o que deseja detectar."

    def _handle_image_analysis(self, text: str) -> str:
        """Analisa características de imagens."""
        return "🖼️ Análise de imagem disponível. Envie uma imagem para análise detalhada."

    def _handle_camera_command(self, text: str) -> str:
        """Comandos relacionados à câmera."""
        if 'abrir' in text.lower() or 'ligar' in text.lower():
            return self._open_camera()
        elif 'foto' in text.lower() or 'captura' in text.lower():
            return self._take_photo()
        else:
            return "📷 Comandos de câmera: 'abrir câmera', 'tirar foto', 'detectar objetos na câmera'"

    def _handle_video_command(self, text: str) -> str:
        """Comandos de processamento de vídeo."""
        return "🎥 Processamento de vídeo em desenvolvimento. Em breve você poderá processar vídeos!"

    def _detect_objects_camera(self) -> str:
        """Detecta objetos usando a câmera."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Não foi possível acessar a câmera."
            
            # Captura um frame
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return "❌ Erro ao capturar imagem da câmera."
            
            # Detecta objetos
            objects = self._detect_objects_in_frame(frame)
            cap.release()
            
            if objects:
                object_list = ", ".join(objects)
                return f"🔍 Objetos detectados: {object_list}"
            else:
                return "🔍 Nenhum objeto reconhecido na imagem."
                
        except Exception as e:
            logger.error(f"Erro na detecção de objetos: {e}")
            return f"❌ Erro ao acessar câmera: {str(e)}"

    def _detect_faces_camera(self) -> str:
        """Detecta faces usando a câmera."""
        try:
            if not self.face_cascade:
                return "❌ Modelo de detecção de faces não disponível."
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Não foi possível acessar a câmera."
            
            # Captura um frame
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return "❌ Erro ao capturar imagem da câmera."
            
            # Converte para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detecta faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            cap.release()
            
            num_faces = len(faces)
            if num_faces > 0:
                return f"👤 {num_faces} face(s) detectada(s) na câmera!"
            else:
                return "👤 Nenhuma face detectada na câmera."
                
        except Exception as e:
            logger.error(f"Erro na detecção de faces: {e}")
            return f"❌ Erro ao detectar faces: {str(e)}"

    def _open_camera(self) -> str:
        """Abre visualização da câmera."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Não foi possível acessar a câmera."
            
            # Mostra câmera por alguns segundos
            start_time = cv2.getTickCount()
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Adiciona texto informativo
                cv2.putText(frame, "Pressione 'q' para sair", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Jarvis Camera', frame)
                
                # Sai se 'q' for pressionado ou após 10 segundos
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                current_time = cv2.getTickCount()
                if (current_time - start_time) / cv2.getTickFrequency() > 10:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            return "📷 Câmera fechada."
            
        except Exception as e:
            logger.error(f"Erro ao abrir câmera: {e}")
            return f"❌ Erro ao abrir câmera: {str(e)}"

    def _take_photo(self) -> str:
        """Tira uma foto e salva."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Não foi possível acessar a câmera."
            
            # Captura foto
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return "❌ Erro ao capturar foto."
            
            # Salva foto
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.temp_dir}/photo_{timestamp}.jpg"
            
            cv2.imwrite(filename, frame)
            cap.release()
            
            return f"📸 Foto salva em: {filename}"
            
        except Exception as e:
            logger.error(f"Erro ao tirar foto: {e}")
            return f"❌ Erro ao tirar foto: {str(e)}"

    def _detect_objects_in_frame(self, frame: np.ndarray) -> List[str]:
        """Detecta objetos em um frame usando métodos disponíveis."""
        detected_objects = []
        
        try:
            # Se tiver YOLO, usa YOLO
            if hasattr(self, 'yolo_net') and self.yolo_net is not None:
                detected_objects = self._yolo_detection(frame)
            else:
                # Usa detecção básica baseada em contornos e características
                detected_objects = self._basic_object_detection(frame)
                
        except Exception as e:
            logger.error(f"Erro na detecção de objetos: {e}")
        
        return detected_objects

    def _yolo_detection(self, frame: np.ndarray) -> List[str]:
        """Detecção usando YOLO."""
        try:
            height, width, channels = frame.shape
            
            # Prepara input para YOLO
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            self.yolo_net.setInput(blob)
            outputs = self.yolo_net.forward()
            
            # Processa outputs
            objects = []
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > self.confidence_threshold:
                        objects.append(self.yolo_classes[class_id])
            
            return list(set(objects))  # Remove duplicatas
            
        except Exception as e:
            logger.error(f"Erro na detecção YOLO: {e}")
            return []

    def _basic_object_detection(self, frame: np.ndarray) -> List[str]:
        """Detecção básica usando OpenCV."""
        try:
            detected = []
            
            # Converte para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detecta bordas
            edges = cv2.Canny(gray, 50, 150)
            
            # Encontra contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Análise básica baseada no número e tamanho dos contornos
            large_contours = [c for c in contours if cv2.contourArea(c) > 1000]
            
            if len(large_contours) > 10:
                detected.append("múltiplos objetos")
            elif len(large_contours) > 5:
                detected.append("alguns objetos")
            elif len(large_contours) > 0:
                detected.append("objeto")
            
            # Detecta formas básicas
            for contour in large_contours[:5]:  # Analisa até 5 contornos
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.7:
                        detected.append("objeto circular")
                    else:
                        detected.append("objeto angular")
            
            return detected if detected else ["formas não identificadas"]
            
        except Exception as e:
            logger.error(f"Erro na detecção básica: {e}")
            return []

    def recognize_objects(self, image_data: Any) -> str:
        """Reconhece objetos em uma imagem."""
        try:
            # Processa diferentes tipos de entrada
            if isinstance(image_data, str):
                # Assumindo que é um caminho de arquivo
                if os.path.exists(image_data):
                    frame = cv2.imread(image_data)
                else:
                    return "❌ Arquivo de imagem não encontrado."
            elif isinstance(image_data, np.ndarray):
                frame = image_data
            else:
                return "❌ Formato de imagem não suportado."
            
            objects = self._detect_objects_in_frame(frame)
            
            if objects:
                return f"🔍 Objetos reconhecidos: {', '.join(objects)}"
            else:
                return "🔍 Nenhum objeto reconhecido na imagem."
                
        except Exception as e:
            logger.error(f"Erro no reconhecimento: {e}")
            return f"❌ Erro no reconhecimento: {str(e)}"

    def detect_faces(self, image_data: Any) -> str:
        """Detecta faces em uma imagem."""
        try:
            if not self.face_cascade:
                return "❌ Modelo de detecção de faces não disponível."
            
            # Similar ao recognize_objects, mas focado em faces
            if isinstance(image_data, str) and os.path.exists(image_data):
                frame = cv2.imread(image_data)
            elif isinstance(image_data, np.ndarray):
                frame = image_data
            else:
                return "❌ Formato de imagem não suportado."
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return f"👤 {len(faces)} face(s) detectada(s) na imagem."
            
        except Exception as e:
            logger.error(f"Erro na detecção de faces: {e}")
            return f"❌ Erro na detecção: {str(e)}"

    def classify_image(self, image_data: Any) -> str:
        """Classifica uma imagem (implementação básica)."""
        try:
            # Análise básica de características da imagem
            if isinstance(image_data, str) and os.path.exists(image_data):
                frame = cv2.imread(image_data)
            elif isinstance(image_data, np.ndarray):
                frame = image_data
            else:
                return "❌ Formato de imagem não suportado."
            
            # Análise de cor predominante
            mean_color = np.mean(frame, axis=(0, 1))
            
            # Análise de brilho
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Classificação básica
            if brightness < 50:
                light_class = "escura"
            elif brightness > 200:
                light_class = "clara"
            else:
                light_class = "média luminosidade"
            
            # Cor predominante
            b, g, r = mean_color
            if r > g and r > b:
                color_class = "avermelhada"
            elif g > r and g > b:
                color_class = "esverdeada"
            elif b > r and b > g:
                color_class = "azulada"
            else:
                color_class = "neutra"
            
            return f"🖼️ Imagem classificada como: {light_class}, tonalidade {color_class}"
            
        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            return f"❌ Erro na classificação: {str(e)}"

    def process_video(self, video_source: Any) -> str:
        """Processa vídeo em tempo real (implementação básica)."""
        try:
            if isinstance(video_source, int) or video_source is None:
                # Usa webcam
                cap = cv2.VideoCapture(0)
            else:
                # Usa arquivo de vídeo
                cap = cv2.VideoCapture(video_source)
            
            if not cap.isOpened():
                return "❌ Não foi possível abrir a fonte de vídeo."
            
            frame_count = 0
            detected_objects = set()
            
            # Processa alguns frames
            while frame_count < 30:  # Processa 30 frames
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 10 == 0:  # Analisa a cada 10 frames
                    objects = self._detect_objects_in_frame(frame)
                    detected_objects.update(objects)
                
                frame_count += 1
            
            cap.release()
            
            if detected_objects:
                return f"🎥 Processamento de vídeo concluído. Objetos detectados: {', '.join(detected_objects)}"
            else:
                return "🎥 Processamento de vídeo concluído. Nenhum objeto identificado."
            
        except Exception as e:
            logger.error(f"Erro no processamento de vídeo: {e}")
            return f"❌ Erro no processamento: {str(e)}"

    def can_handle(self, text: str) -> bool:
        """Detecta se o texto pede funcionalidades de visão."""
        vision_keywords = [
            "reconhece", "detectar", "classifica", "vídeo", "visão",
            "câmera", "foto", "imagem", "face", "objeto", "analisa"
        ]
        return any(keyword in text.lower() for keyword in vision_keywords)

    def handle(self, text: str) -> str:
        """Método de compatibilidade com sistema antigo."""
        return self.process(text) or "👁️ Comando de visão não reconhecido."

    def on_event(self, event: Dict[str, Any]):
        """Integração com sistema de eventos do núcleo."""
        logger.info(f"VisionPlugin recebeu evento: {event.get('input', 'unknown')}")
