import librosa
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.metrics import classification_report, accuracy_score

def extract_features(file_path, target_sr=48000):
    signal, sr = librosa.load(file_path, sr=target_sr)
    mfccs = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40, fmax=sr/2, n_fft=2048, hop_length=512)
    mfccs_mean = np.mean(mfccs.T, axis=0)
    return mfccs_mean

def load_data(directory):
    features = []
    labels = []
    
    for label in os.listdir(directory):
        class_dir = os.path.join(directory, label)
        if os.path.isdir(class_dir):
            for file in os.listdir(class_dir):
                if file.endswith('.wav'):
                    file_path = os.path.join(class_dir, file)
                    feature = extract_features(file_path, target_sr=48000)
                    features.append(feature)
                    labels.append(label)
    
    return np.array(features), np.array(labels)

def train_model(data_directory):
    X, y = load_data(data_directory)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = svm.SVC(kernel='linear', probability=True)  # เพิ่ม probability=True
    model.fit(X_train, y_train)  
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    return model

def predict(model, file_path, threshold=0.5):
    feature = extract_features(file_path)
    probabilities = model.predict_proba([feature])[0]  # ทำนายความน่าจะเป็น
    max_prob = max(probabilities)
    
    if max_prob >= threshold:  # ตรวจสอบว่าความน่าจะเป็นเกินกว่าค่าที่กำหนดหรือไม่
        prediction = model.predict([feature])[0]
        return prediction, probabilities  # ส่งกลับคำทำนายและความน่าจะเป็น
    else:
        return None, None  # ถ้าไม่ตรงก็ไม่แสดงผล

if __name__ == "__main__":
    data_directory = 'C:/Users/natty/Desktop/New folder/SoundProject/sampleforb'  # Replace with your training data directory
    input_directory = 'C:/Users/natty/Desktop/New folder/SoundProject/input'  # Replace with your input directory
    model = train_model(data_directory)
    
    while True:
        input_file = input("Enter the audio file name (without path) to predict (or type 'exit' to quit): ")
        if input_file.lower() == "exit":
            break
        
        # สร้างเส้นทางเต็มสำหรับไฟล์ที่ป้อน
        file_path = os.path.join(input_directory, input_file + '.wav')
        
        if os.path.isfile(file_path):
            try:
                result, probabilities = predict(model, file_path)  # ทำนายคลาสของไฟล์ที่ป้อน
                if result:
                    print()
                    print("Predicted label:", result)
                    print("Probabilities:", probabilities)  # แสดงความน่าจะเป็น
                else:
                    print("No matching result found.")
            except Exception as e:
                print("An error occurred:", e)
        else:
            print("File not found. Please make sure the file exists and the name is correct.")
