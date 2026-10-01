import os
import subprocess
import xml.etree.ElementTree as ET
import sys

def generate_traces(n_vehicles):
    print(f"Generating traces for {n_vehicles} vehicles...")
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, '..'))
    sumo_scenario_dir = os.path.join(project_root, 'src/maro_pe/simulation/sumo_scenario')
    traces_dir = os.path.join(sumo_scenario_dir, 'traces')
    os.makedirs(traces_dir, exist_ok=True)
    
    # Create sumo_N.rou.xml
    base_rou_xml = os.path.join(sumo_scenario_dir, 'sumo.rou.xml')
    tree = ET.parse(base_rou_xml)
    root = tree.getroot()
    
    for i in range(n_vehicles):
        # <vehicle id="veh_0" type="car" route="r0" depart="0.0" departSpeed="max" departPos="random"/>
        attrib = {
            'id': f'veh_{i}',
            'type': 'car',
            'route': 'r0',
            'depart': '0.0',
            'departSpeed': 'max',
            'departPos': 'random'
        }
        ET.SubElement(root, 'vehicle', attrib)
        
    out_rou_xml = os.path.join(traces_dir, f'sumo_{n_vehicles}.rou.xml')
    tree.write(out_rou_xml)
    print(f"  Created {out_rou_xml}")
    
    # Run SUMO to generate FCD
    fcd_xml = os.path.join(traces_dir, f'fcd_{n_vehicles}.xml')
    sumo_cfg = os.path.join(sumo_scenario_dir, 'sumo.sumocfg')
    
    sumo_cmd = [
        'sumo',
        '-c', sumo_cfg,
        '--route-files', out_rou_xml,
        '--fcd-output', fcd_xml,
        '--step-length', '0.1'
    ]
    subprocess.run(sumo_cmd, check=True)
    print(f"  Generated {fcd_xml}")
    
    # Run traceExporter.py to generate ns2mobility.tcl
    sumo_home = os.environ.get('SUMO_HOME', '/opt/homebrew/share/sumo')
    trace_exporter = os.path.join(sumo_home, 'tools/traceExporter.py')
    if not os.path.exists(trace_exporter):
        print(f"  ERROR: traceExporter.py not found at {trace_exporter}. Ensure SUMO_HOME is set correctly.")
        sys.exit(1)
        
    ns2_tcl = os.path.join(traces_dir, f'ns2mobility_{n_vehicles}.tcl')
    export_cmd = [
        'python3', trace_exporter,
        '--fcd-input', fcd_xml,
        '--ns2mobility-output', ns2_tcl
    ]
    subprocess.run(export_cmd, check=True)
    print(f"  Generated {ns2_tcl}")
    
if __name__ == "__main__":
    for N in [8, 16, 32]:
        generate_traces(N)
    print("All traces generated successfully.")
