import os
import sys
import numpy as np
import tensorflow as tf
import gradio as gr
from PIL import Image

# --- Configuration ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')

print("System: Initializing Casting Defect Detection App...")

# --- 1. Model Loading ---
def load_model():
    if not os.path.exists(MODEL_DIR) or not os.listdir(MODEL_DIR):
        print(f"Error: Model not found in '{MODEL_DIR}'.")
        return None
    print(f"Loading model from: {MODEL_DIR} ...")
    try:
        model = tf.keras.models.load_model(MODEL_DIR)
        print("✅ Model loaded successfully!")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

model = load_model()

if model is None:
    sys.exit(1)

# --- 2. Prediction Function ---
def classify_image(input_image):
    if input_image is None:
        return "Error: No image provided."

    try:
        img = Image.fromarray(input_image.astype('uint8'), 'RGB')
        img = img.resize((300, 300))
        img_array = np.array(img)
        img_batch = np.expand_dims(img_array, axis=0)
        
        prediction_score = model.predict(img_batch)[0][0]
        
        if prediction_score > 0.7:
            result = f"Result: OK (Defect Free).\nConfidence: {prediction_score:.1%}"
        elif prediction_score > 0.3:
            result = f"Result: Uncertain.\nAnalysis inconclusive (Confidence: {prediction_score:.1%})"
        else:
            defect_prob = 1 - prediction_score
            result = f"Result: DEFECT FOUND.\nProbability: {defect_prob:.1%}"
            
        return result
    except Exception as e:
        return f"Error during processing: {str(e)}"

# --- 3. Gradio Interface ---
print("System: Starting Web Interface...")

iface = gr.Interface(
    fn=classify_image,
    inputs=gr.Image(label="Upload Casting Surface Image"),
    # ИЗМЕНЕНИЕ ЗДЕСЬ: lines=3 увеличивает высоту текстового поля
    outputs=gr.Text(label="Analysis Report", lines=3),
    title="Casting Defect Detection",
    description=(
        "AI-powered tool for detecting casting defects based on surface images. "
        "Upload an image to identify potential manufacturing flaws."
    ),
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()