import os
import joblib
import sys
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Local imports
from dataset import get_dataset
from feature_extraction import clean_text, extract_tfidf_features

def evaluate_model(y_true, y_pred, model_name):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    print(f"\n======================================")
    print(f"    {model_name} Evaluation")
    print(f"======================================")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    return acc

def train():
    print("Preparing Dataset for ML Training...")
    df = get_dataset()
    
    print("Cleaning text samples...")
    df['clean_text'] = df['text'].apply(clean_text)
    
    X = df['clean_text']
    y = df['label']
    
    print("Converting text to vectors via TF-IDF...")
    X_vec, vectorizer = extract_tfidf_features(X)
    
    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)
    
    print(f"Dataset split. Training shape: {X_train.shape}, Test shape: {X_test.shape}")
    
    # 1. Logistic Regression
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    lr_acc = evaluate_model(y_test, lr_pred, "Logistic Regression")
    
    # 2. Linear SVM
    svm_model = SVC(kernel='linear', probability=True, random_state=42)
    svm_model.fit(X_train, y_train)
    svm_pred = svm_model.predict(X_test)
    svm_acc = evaluate_model(y_test, svm_pred, "Linear SVM")
    
    # 3. Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_acc = evaluate_model(y_test, rf_pred, "Random Forest")
    
    # Compare and select best
    models = {
        "Logistic Regression": (lr_model, lr_acc),
        "Linear SVM": (svm_model, svm_acc),
        "Random Forest": (rf_model, rf_acc)
    }
    
    best_name = max(models, key=lambda k: models[k][1])
    best_model, best_acc = models[best_name]
    print(f"\n======================================")
    print(f"🏆 Best Model: {best_name} (Acc: {best_acc:.4f})")
    print(f"======================================\n")
    
    # Retrain best model on full dataset for maximum robust performance
    print("Retraining winning model on full dataset...")
    best_model.fit(X_vec, y)
    
    train_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(train_dir, 'trained_model')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'best_classifier.joblib')
    vec_path = os.path.join(model_dir, 'tfidf_vectorizer.joblib')
    
    # Save using joblib for optimized larger array serializations
    joblib.dump(best_model, model_path)
    joblib.dump(vectorizer, vec_path)
        
    print(f"✅ Training complete. Joblib assets saved to {model_dir}")

if __name__ == "__main__":
    train()
