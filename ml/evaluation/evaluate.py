# This is a placeholder for custom evaluation logic.
# The main evaluation happens inside train.py and dumps to JSON.
# In a production setup, this script would generate plots and detailed reports.

import json

def load_metrics():
    with open('/Users/zillekibriya/Desktop/SmartBusStop/scratch/model_results.json', 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    metrics = load_metrics()
    print("Evaluation Metrics:")
    print(json.dumps(metrics, indent=2))
