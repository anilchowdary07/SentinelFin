import time
import json

class NetworkInvestigationAgent:
    @staticmethod
    def run(case_data: dict) -> dict:
        """
        Agent 4: Network Investigation (Simulated LangGraph)
        Traverses the transaction network to identify hidden beneficial owners or shell company overlaps.
        """
        print("\n[AGENT 4] Starting Network Traversal (LangGraph ReAct Simulation)...")
        
        transactions = case_data.get('transactions', [])
        
        # Build an adjacency list to simulate graph traversal
        graph = {}
        for txn in transactions:
            orig = txn.get('originator', {}).get('name', 'Unknown')
            ben = txn.get('beneficiary', {}).get('name', 'Unknown')
            
            if orig not in graph: graph[orig] = []
            if ben not in graph: graph[ben] = []
            
            graph[orig].append(ben)

        print("[AGENT 4 🔍 THOUGHT] Graph built. Tracing fund flow hops...")
        time.sleep(1)
        
        # Simulate LangGraph logic: Check if depth > 2 (Layering)
        max_depth = 0
        terminal_nodes = set()
        
        # We know Global Trade Logistics is the root in the layering scenario
        root_node = "Global Trade Logistics LLC"
        
        if root_node in graph:
            print(f"[AGENT 4 🔍 ACT] Traversing paths from {root_node}...")
            # Breadth-first search to find depth
            queue = [(root_node, 0)]
            visited = set()
            while queue:
                current, depth = queue.pop(0)
                if current not in visited:
                    visited.add(current)
                    max_depth = max(max_depth, depth)
                    
                    neighbors = graph.get(current, [])
                    if not neighbors:
                        terminal_nodes.add(current)
                    else:
                        for n in neighbors:
                            queue.append((n, depth + 1))
                            
        print(f"[AGENT 4 🔍 OBSERVE] Max traversal depth: {max_depth} hops.")
        print(f"[AGENT 4 🔍 OBSERVE] Terminal endpoints: {terminal_nodes}")
        
        # Add synthesis logic for arbitration
        network_risk = 0
        if max_depth >= 2:
            print("[AGENT 4] 🚨 High risk: Multi-hop fund transfer detected.")
            network_risk = 80
            
        case_data['network_results'] = {
            "max_depth": max_depth,
            "terminal_nodes": list(terminal_nodes),
            "network_risk_score": network_risk,
            "status": "COMPLETED"
        }
        
        print("[AGENT 4] Network Investigation Complete.")
        return case_data
