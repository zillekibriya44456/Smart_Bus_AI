import os
import subprocess
import xml.etree.ElementTree as ET
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCENARIOS_DIR = os.path.join(BASE_DIR, 'scenarios')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

def run_command(cmd, cwd):
    print(f"Running: {' '.join(cmd)} in {cwd}")
    subprocess.run(cmd, cwd=cwd, check=True)

def generate_networks():
    # Baseline
    base_dir = os.path.join(SCENARIOS_DIR, 'baseline')
    run_command([
        'netconvert', 
        '--node-files', 'baseline.nod.xml', 
        '--edge-files', 'baseline.edg.xml', 
        '-o', 'baseline.net.xml'
    ], cwd=base_dir)
    
    # Optimized
    opt_dir = os.path.join(SCENARIOS_DIR, 'optimized')
    run_command([
        'netconvert', 
        '--node-files', 'optimized.nod.xml', 
        '--edge-files', 'optimized.edg.xml', 
        '--connection-files', 'optimized.con.xml',
        '-o', 'optimized.net.xml'
    ], cwd=opt_dir)

def run_sumo():
    # Baseline
    base_dir = os.path.join(SCENARIOS_DIR, 'baseline')
    run_command(['sumo', '-c', 'baseline.sumocfg', '--no-warnings'], cwd=base_dir)
    
    # Optimized
    opt_dir = os.path.join(SCENARIOS_DIR, 'optimized')
    run_command(['sumo', '-c', 'optimized.sumocfg', '--no-warnings'], cwd=opt_dir)

def parse_tripinfo(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    total_speed = 0.0
    total_delay = 0.0
    total_wait = 0.0
    bus_travel_time = 0.0
    bus_count = 0
    car_count = 0
    
    for trip in root.findall('tripinfo'):
        vtype = trip.get('vType')
        duration = float(trip.get('duration'))
        routeLength = float(trip.get('routeLength'))
        waitingTime = float(trip.get('waitingTime'))
        timeLoss = float(trip.get('timeLoss'))
        
        speed = (routeLength / duration) * 3.6 if duration > 0 else 0 # km/h
        
        if vtype == 'bus':
            bus_travel_time += duration
            bus_count += 1
        else:
            total_speed += speed
            total_delay += timeLoss
            total_wait += waitingTime
            car_count += 1
            
    throughput = car_count + bus_count
    avg_speed = total_speed / car_count if car_count > 0 else 0
    avg_delay = total_delay / car_count if car_count > 0 else 0
    avg_wait = total_wait / car_count if car_count > 0 else 0
    avg_bus_time = bus_travel_time / bus_count if bus_count > 0 else 0
    
    return {
        "Throughput": throughput,
        "Average_Speed_kmh": round(avg_speed, 2),
        "Average_Delay_s": round(avg_delay, 2),
        "Average_Wait_Time_s": round(avg_wait, 2),
        "Average_Bus_Travel_Time_s": round(avg_bus_time, 2)
    }

def main():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print("Generating networks...")
    generate_networks()
    
    print("Running simulations...")
    run_sumo()
    
    print("Parsing outputs...")
    baseline_metrics = parse_tripinfo(os.path.join(OUTPUTS_DIR, 'tripinfo_baseline.xml'))
    optimized_metrics = parse_tripinfo(os.path.join(OUTPUTS_DIR, 'tripinfo_optimized.xml'))
    
    report = {
        "Scenario_A_Baseline": baseline_metrics,
        "Scenario_B_Optimized": optimized_metrics,
        "Improvements": {
            "Speed_Increase_kmh": round(optimized_metrics["Average_Speed_kmh"] - baseline_metrics["Average_Speed_kmh"], 2),
            "Delay_Reduction_s": round(baseline_metrics["Average_Delay_s"] - optimized_metrics["Average_Delay_s"], 2),
            "Wait_Time_Reduction_s": round(baseline_metrics["Average_Wait_Time_s"] - optimized_metrics["Average_Wait_Time_s"], 2)
        }
    }
    
    report_path = os.path.join(RESULTS_DIR, 'comparison_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=4)
        
    print(f"Simulation complete. Report saved to {report_path}")

if __name__ == "__main__":
    main()
