import os
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, roc_auc_score
import joblib


# Create a new folder where we will save the model
if not os.path.exists('models'):
    os.makedirs('models')

# Create dataframe for our training data
df = pd.read_csv('./hd_training_dataset.csv')

# Display basic information about the dataset
# print("Dataset Information:")
# print(df.info())
# print(f"\nHeart Cases: {df['heart_disease'].sum()}")

# Split the dataset into features and target variable
features_cols = ['age', 'weight', 'bloodSugar', 'bloodPressure', 'smoker', 'chronic_disease', 'diabetic', 'alcoholic']
X = df[features_cols].values  # Values of the features - independent variables
Y = df['heart_disease'].values #Values of the target variable

# Split the dataset into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)

# Print the shapes of the training and testing sets
# print(f"\nTraining set shape: {X_train.shape}, {Y_train.shape}")
# print(f"\nValidation set shape: {X_test.shape}, {Y_test.shape}")

# Train model
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, Y_train)

# Make predictions on the test set
y_predictions = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Calculate other metrics if needed
accuracy = accuracy_score(Y_test, y_predictions)
precision = precision_score(Y_test, y_predictions)
sesitivity = recall_score(Y_test, y_predictions)
cm = confusion_matrix(Y_test, y_predictions)
tn, fp, fn, tp = cm.ravel()
specificity_score = tn / (tn + fp) if (tn + fp) > 0 else 0
roc_auc = roc_auc_score(Y_test, y_pred_proba)

##Print the evaluation metrics
print(f"\nAccuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall (Sensitivity): {sesitivity:.2f}")
print(f"Specificity: {specificity_score:.2f}")
print(f"ROC AUC: {roc_auc:.2f}")

# Create and save confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['No Heart Disease', 'Heart Disease'], 
            yticklabels=['No Heart Disease', 'Heart Disease'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.savefig('models/confusion_matrix.png')
plt.show()

# Create and save ROC curve

fpr, tpr, thresholds = roc_curve(Y_test, y_pred_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', label='ROC Curve (area = {:.2f})'.format(roc_auc))
plt.plot([0, 1], [0, 1], color='red', linestyle='--')
plt.xlabel('False Positive Rate')   
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.savefig('models/roc_curve.png')
plt.show()


# Feature Importance
feature_importance = pd.DataFrame({
    'Feature': features_cols,
    'Importance': model.coef_[0]
}).sort_values(by='Importance', ascending=False)
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance)
plt.title('Feature Importance')
plt.savefig('models/feature_importance.png')
plt.show()

# Save all results in a text file
with open('models/model_results.txt', 'w') as f:
    f.write(f"Accuracy: {accuracy:.2f}\n")
    f.write(f"Precision: {precision:.2f}\n")
    f.write(f"Recall (Sensitivity): {sesitivity:.2f}\n")
    f.write(f"Specificity: {specificity_score:.2f}\n")
    f.write(f"ROC AUC: {roc_auc:.2f}\n")
    f.write("\nConfusion Matrix:\n")
    f.write(str(cm))
    f.write("\nFeature Importance:\n")
    f.write(feature_importance.to_string(index=False))

# Save the trained model

model_filename = 'models/heart_disease_model.pkl'
joblib.dump(model, model_filename)

##Save Features for later use
pd.Series(features_cols).to_csv('models/features.csv', index=False, header=['feature'])

print(f"\nModel saved to {model_filename}")
print("Training complete and results saved.")
print(f"\nTarget accuracy: {accuracy:.2f} - Model saved successfully in 'models' directory.")