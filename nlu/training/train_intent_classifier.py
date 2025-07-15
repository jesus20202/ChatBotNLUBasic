import spacy
import json
import random
from pathlib import Path
from spacy.training import Example
from spacy.util import minibatch, compounding
from sklearn.model_selection import train_test_split
import numpy as np

MODEL_PATH = "nlu/spacy_model/modelo_intenciones"
TRAIN_DATA_PATH = "nlu/training/training_data.json"
BASE_MODEL = "es_core_news_md"

class ImprovedIntentTrainer:
    def __init__(self):
        self.nlp = spacy.load(BASE_MODEL)
        self.training_data = self.load_training_data()
        self.textcat = self._setup_textcat()
        
    def load_training_data(self):
        with open(TRAIN_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        examples = []
        for intent, texts in data["intents"].items():
            for text in texts:
                # Aseguramos que todas las otras intenciones tengan 0.0
                cats = {intent: 1.0}
                examples.append((text, {"cats": cats}))
        
        return examples
    
    def _setup_textcat(self):
        # Limpiamos pipes previos
        if "textcat" in self.nlp.pipe_names:
            self.nlp.remove_pipe("textcat")
        if "textcat_multilabel" in self.nlp.pipe_names:
            self.nlp.remove_pipe("textcat_multilabel")
        
        # Para clasificación de intenciones exclusivas, usa "textcat"
        textcat = self.nlp.add_pipe("textcat", last=True)
        
        # Añadimos todas las labels
        intents = {intent for _, ann in self.training_data for intent in ann["cats"].keys()}
        for intent in intents:
            textcat.add_label(intent)
        
        return textcat
    
    def prepare_examples(self, data):
        examples = []
        all_intents = {intent for _, ann in self.training_data for intent in ann["cats"].keys()}
        
        for text, ann in data:
            # Aseguramos que todas las intenciones estén presentes
            cats = {intent: 0.0 for intent in all_intents}
            cats.update(ann["cats"])
            
            examples.append(Example.from_dict(
                self.nlp.make_doc(text), 
                {"cats": cats}
            ))
        
        return examples
    
    def train_model_with_early_stopping(self, train_data, val_data, max_iterations=100, patience=5):
        train_examples = self.prepare_examples(train_data)
        val_examples = self.prepare_examples(val_data)
        
        # Inicializamos
        self.nlp.initialize(lambda: train_examples)
        optimizer = self.nlp.resume_training()
        
        best_accuracy = 0
        patience_counter = 0
        best_model_state = None
        
        print("🚀 Iniciando entrenamiento con Early Stopping...")
        
        for i in range(max_iterations):
            # Entrenamiento con dropout progresivo
            random.shuffle(train_examples)
            losses = {}
            
            # Dropout que decrece con el tiempo
            dropout_rate = max(0.1, 0.5 - (i * 0.01))
            
            batches = minibatch(train_examples, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                self.nlp.update(batch, drop=dropout_rate, losses=losses, sgd=optimizer)
            
            # Evaluación en validación
            val_accuracy = self.evaluate_silent(val_examples)
            
            print(f"Epoch {i+1:2d}/{max_iterations} | "
                  f"Loss: {losses.get('textcat', 0):.4f} | "
                  f"Val Acc: {val_accuracy:.2%} | "
                  f"Dropout: {dropout_rate:.2f}")
            
            # Early stopping logic
            if val_accuracy > best_accuracy:
                best_accuracy = val_accuracy
                patience_counter = 0
                # Guardamos el estado del mejor modelo
                best_model_state = self.nlp.to_bytes()
                print(f"📈 Nuevo mejor modelo! Accuracy: {best_accuracy:.2%}")
            else:
                patience_counter += 1
                
            if patience_counter >= patience:
                print(f"⏹️  Early stopping activado. Mejor accuracy: {best_accuracy:.2%}")
                break
        
        # Restauramos el mejor modelo
        if best_model_state:
            self.nlp.from_bytes(best_model_state)
            print("🔄 Modelo restaurado al mejor estado")
        
        return best_accuracy
    
    def evaluate_silent(self, examples):
        """Evaluación silenciosa para early stopping"""
        correct, total = 0, 0
        for ex in examples:
            doc = self.nlp(ex.text)
            pred = max(doc.cats, key=doc.cats.get)
            gold = max(ex.reference.cats, key=ex.reference.cats.get)
            if pred == gold:
                correct += 1
            total += 1
        return correct / total if total else 0
    
    def evaluate_detailed(self, val_data):
        """Evaluación detallada con métricas por clase"""
        examples = self.prepare_examples(val_data)
        
        # Métricas por clase
        class_stats = {}
        all_intents = {intent for _, ann in self.training_data for intent in ann["cats"].keys()}
        
        for intent in all_intents:
            class_stats[intent] = {"tp": 0, "fp": 0, "fn": 0}
        
        total_correct = 0
        total_examples = len(examples)
        
        for ex in examples:
            doc = self.nlp(ex.text)
            pred = max(doc.cats, key=doc.cats.get)
            gold = max(ex.reference.cats, key=ex.reference.cats.get)
            
            if pred == gold:
                total_correct += 1
                class_stats[pred]["tp"] += 1
            else:
                class_stats[pred]["fp"] += 1
                class_stats[gold]["fn"] += 1
        
        # Calculamos métricas
        overall_accuracy = total_correct / total_examples
        
        print(f"\n📊 EVALUACIÓN DETALLADA")
        print(f"Precisión general: {overall_accuracy:.2%}")
        print(f"{'Intención':<20} {'Precisión':<10} {'Recall':<10} {'F1-Score':<10}")
        print("-" * 60)
        
        for intent in all_intents:
            tp = class_stats[intent]["tp"]
            fp = class_stats[intent]["fp"]
            fn = class_stats[intent]["fn"]
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"{intent:<20} {precision:<10.2%} {recall:<10.2%} {f1:<10.2%}")
        
        return overall_accuracy
    
    def augment_data(self, data, augmentation_factor=1.5):
        """Augmentación simple de datos"""
        augmented = data.copy()
        
        for text, ann in data:
            # Variaciones simples
            variations = [
                text.lower(),
                text.upper(),
                text.capitalize(),
                text.replace("?", ""),
                text.replace("!", ""),
                text + "?",
                text + ".",
            ]
            
            for var in variations:
                if var != text and len(var.strip()) > 3:
                    augmented.append((var, ann))
                    if len(augmented) >= len(data) * augmentation_factor:
                        break
            
            if len(augmented) >= len(data) * augmentation_factor:
                break
        
        return augmented
    
    def save_model(self):
        output_dir = Path(MODEL_PATH)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.nlp.to_disk(output_dir)
        print(f"✅ Modelo guardado en: {output_dir}")
    
    def test_predictions(self, test_texts):
        """Prueba el modelo con textos de ejemplo"""
        print("\n🧪 PRUEBAS DEL MODELO")
        print("-" * 40)
        
        for text in test_texts:
            doc = self.nlp(text)
            
            # Ordenamos por confianza
            sorted_cats = sorted(doc.cats.items(), key=lambda x: x[1], reverse=True)
            
            print(f"\nTexto: '{text}'")
            print(f"Predicción: {sorted_cats[0][0]} ({sorted_cats[0][1]:.2%})")
            
            # Mostramos top 3 predicciones
            print("Top 3 predicciones:")
            for intent, score in sorted_cats[:3]:
                print(f"  {intent}: {score:.2%}")


def main():
    trainer = ImprovedIntentTrainer()
    
    # Preparamos datos
    all_data = trainer.training_data
    print(f"📊 Total de ejemplos: {len(all_data)}")
    
    # Augmentación de datos (opcional)
    use_augmentation = True
    if use_augmentation:
        all_data = trainer.augment_data(all_data, augmentation_factor=1.3)
        print(f"📊 Ejemplos después de augmentación: {len(all_data)}")
    
    # División de datos con estratificación corregida
    # Extraemos las etiquetas para estratificar
    labels = []
    for _, ann in all_data:
        # Obtenemos la intención con valor 1.0
        intent = [intent for intent, value in ann["cats"].items() if value == 1.0][0]
        labels.append(intent)
    
    train_data, val_data = train_test_split(
        all_data, 
        test_size=0.2, 
        random_state=42,
        stratify=labels  # Estratificación con etiquetas simples
    )
    
    print(f"🎯 Datos de entrenamiento: {len(train_data)}")
    print(f"🎯 Datos de validación: {len(val_data)}")
    
    # Entrenamiento con early stopping
    best_accuracy = trainer.train_model_with_early_stopping(
        train_data, 
        val_data, 
        max_iterations=50, 
        patience=8
    )
    
    # Evaluación detallada
    print("\n🔍 EVALUACIÓN FINAL")
    trainer.evaluate_detailed(val_data)
    
    # Guardamos el modelo
    trainer.save_model()
    
    # Pruebas opcionales
    test_texts = [
        "Hola, ¿cómo estás?",
        "¿Cuál es el precio de este producto?",
        "Quiero cancelar mi pedido",
        "Gracias por la ayuda"
    ]
    
    trainer.test_predictions(test_texts)


if __name__ == "__main__":
    main()