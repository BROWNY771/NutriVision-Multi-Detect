import kagglehub
import os
from ultralytics import YOLO
from collections import Counter

LOCAL_MODEL_PATH = "best.pt"
model = None

def initialize_model():
    global model
    try:
        path = kagglehub.dataset_download("noalianore/food-ingred-dataset")
        model_path = os.path.join(path, "Undersampled_cleaned_dataset", "best.pt")
        
        if not os.path.exists(model_path):
            model_path = LOCAL_MODEL_PATH 
            
        if os.path.exists(model_path):
            model = YOLO(model_path)
            print(f"Modèle chargé avec succès : {model_path}")
        else:
            print("ERREUR : Aucun fichier 'best.pt' trouvé localement ou sur Kaggle.")
    except Exception as e:
        print(f"Erreur d'initialisation YOLO : {e}")

initialize_model()

def detect_multi_food(image_path):
    if model is None:
        print("Erreur : Le modèle YOLO n'est pas chargé.")
        return []

    try:
        results = model.predict(image_path, conf=0.25, save=False, verbose=False)
        raw_names = []
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                name = r.names[cls_id]
                raw_names.append(name)
        
        counts = Counter(raw_names)
        return [{"name": name, "count": count} for name, count in counts.items()]
    except Exception as e:
        print(f"Erreur lors de la détection : {e}")
        return []