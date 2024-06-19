import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def predict(model, data, device, batch_size=32, THRESHOLD=0.5):
    model.eval()
    data_tensor = torch.tensor(data).float()
    dataset = TensorDataset(data_tensor)
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    
    all_outputs = []
    with torch.no_grad():
        for batch in data_loader:
            inputs = batch[0].to(device)
            logits = model(inputs)
            outputs = torch.sigmoid(logits)
            all_outputs.extend(outputs.cpu().numpy())
    
    all_outputs = np.array(all_outputs)
    predictions = all_outputs > THRESHOLD
    return predictions

def evaluate(model, test_loader, device, batch_level=False):
    model.eval()
    X_test = []
    Y_test = []
    metrics_list = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            if batch_level:
                batch_metrics = compute_batch_metrics(model, inputs, labels, device)
                metrics_list.append(batch_metrics)
            X_test.append(inputs.cpu().numpy())
            Y_test.append(labels.cpu().numpy())
    
    if batch_level:
        return metrics_list

    X_test = np.concatenate(X_test)
    Y_test = np.concatenate(Y_test)
    y_pred = predict(model, X_test, device)
    metrics = compute_metrics(Y_test, y_pred)
    
    return metrics

def compute_metrics(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    roc_auc = None
    if len(np.unique(y_true)) > 1:  
        roc_auc = roc_auc_score(y_true, y_pred)
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
    }
    return metrics

def compute_batch_metrics(model, inputs, labels, device):
    inputs, labels = inputs.to(device), labels.to(device)
    logits = model(inputs)
    outputs = torch.sigmoid(logits).detach()  
    predictions = outputs.cpu().numpy() > 0.5
    labels = labels.cpu().numpy()

    metrics = compute_metrics(labels, predictions)
    return metrics