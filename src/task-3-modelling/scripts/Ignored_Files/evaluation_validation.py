# Evaluation and validation for 3-month predictions
def evaluate_predictions(model, X_test, y_test, scaler):
    model.eval()
    with torch.no_grad():
        predictions = model(X_test)
    
    # Calculate metrics for each forecast step
    metrics = {}
    for step in range(3):  # 3-month horizon
        step_pred = predictions[:, step, :]
        step_true = y_test[:, step, :]
        
        metrics[f'month_{step+1}'] = {
            'mse': mean_squared_error(step_true, step_pred),
            'rmse': np.sqrt(mean_squared_error(step_true, step_pred)),
            'mae': mean_absolute_error(step_true, step_pred),
            'r2': r2_score(step_true, step_pred)
        }
    
    return predictions, metrics

# Implement rolling forecast validation
def rolling_validation(model, X, y, sequence_length=30, forecast_horizon=3, validation_steps=12):
    rolling_metrics = []
    
    for i in range(validation_steps):
        start_idx = -(sequence_length + forecast_horizon + i)
        end_idx = start_idx + sequence_length
        
        X_roll = X[start_idx:end_idx]
        y_roll = y[end_idx:end_idx + forecast_horizon]
        
        with torch.no_grad():
            pred = model(X_roll.unsqueeze(0))
        
        # Calculate error for this rolling window
        error = mean_squared_error(y_roll, pred.squeeze(0))
        rolling_metrics.append(error)
    
    return np.mean(rolling_metrics), np.std(rolling_metrics)

# Visualization for 3-month predictions
def plot_forecast_evaluation(predictions, y_test, dates):
    plt.figure(figsize=(15, 10))
    
    # Plot predictions for each month
    for i in range(3):
        plt.subplot(2, 2, i+1)
        plt.scatter(y_test[:, i, 0], predictions[:, i, 0], alpha=0.5)
        plt.plot([0, 5], [0, 5], 'r--')
        plt.xlabel(f'Actual Severity (Month {i+1})')
        plt.ylabel(f'Predicted Severity (Month {i+1})')
        plt.title(f'Month {i+1} Predictions')
    
    # Plot combined forecast trajectory
    plt.subplot(2, 2, 4)
    for i in range(min(5, len(predictions))):  # Plot first 5 sequences
        plt.plot(range(3), predictions[i, :, 0], 'b-', alpha=0.3, label='Predicted' if i==0 else '')
        plt.plot(range(3), y_test[i, :, 0], 'r-', alpha=0.3, label='Actual' if i==0 else '')
    plt.xlabel('Forecast Month')
    plt.ylabel('Severity Index')
    plt.title('Forecast Trajectories')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
