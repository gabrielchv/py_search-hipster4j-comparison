#!/usr/bin/env python3
"""
A* Search Performance Study using py-search library
Comparing search performance across different routes in Brazil
"""

import time
import json
import math
from py_search.base import Problem, Node, AnnotatedProblem
from py_search.informed import best_first_search

# Load data from JSON file
def load_data():
    with open('brazil_cities_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Load shared data
data = load_data()
CITY_COORDINATES = data['cities']
ROADS_DATA = data['roads']
TEST_ROUTES = data['test_routes']

# Build roads dictionary from JSON data
roads = {}
for road in ROADS_DATA:
    from_city = road['from']
    to_city = road['to']
    distance = road['distance']
    
    # Add bidirectional connections
    if from_city not in roads:
        roads[from_city] = {}
    if to_city not in roads:
        roads[to_city] = {}
    
    roads[from_city][to_city] = distance
    roads[to_city][from_city] = distance

# Simple Brazil cities map for testing
brazil_cities = CITY_COORDINATES

def calculate_distance(city1, city2):
    """Calculate Euclidean distance between two cities (heuristic function)"""
    if city1 not in brazil_cities or city2 not in brazil_cities:
        return 0
    
    lat1, lng1 = brazil_cities[city1]['lat'], brazil_cities[city1]['lng']
    lat2, lng2 = brazil_cities[city2]['lat'], brazil_cities[city2]['lng']
    
    # Simplified Euclidean distance * 111 km (approximate km per degree)
    return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 111

class RouteProblem(Problem):
    def __init__(self, start, goal):
        super().__init__(start, goal)
    
    def successors(self, node):
        current = node.state
        result = []
        if current in roads:
            for city, distance in roads[current].items():
                new_node = Node(city, parent=node, action=f"drive to {city}", node_cost=node.cost() + distance)
                result.append(new_node)
        return result
    
    def node_value(self, node):
        # f(n) = g(n) + h(n) for informed search
        return node.cost() + self.heuristic(node)
    
    def heuristic(self, node):
        goal_state = self.goal.state if hasattr(self.goal, 'state') else self.goal
        return calculate_distance(node.state, goal_state)

def run_astar_test(start_city, goal_city):
    """Test A* algorithm and return metrics"""
    problem = RouteProblem(start_city, goal_city)
    annotated_prob = AnnotatedProblem(problem)
    
    print(f"\nTesting A* search: {start_city} -> {goal_city}")
    print("=" * 50)
    
    start_time = time.time()
    try:
        solution = next(best_first_search(annotated_prob))
        end_time = time.time()
        
        result = {
            'solution_found': True,
            'path_cost': solution.cost(),
            'path_length': len(solution.path()),
            'execution_time': (end_time - start_time) * 1000,  # milliseconds
            'nodes_expanded': annotated_prob.nodes_expanded,
            'goal_tests': annotated_prob.goal_tests,
            'path': [action for action in solution.path()]
        }
        
        print(f"Solution found!")
        print(f"  Cost: {result['path_cost']} km")
        print(f"  Steps: {result['path_length']}")
        print(f"  Execution time: {result['execution_time']:.2f} ms")
        print(f"  Nodes expanded: {result['nodes_expanded']}")
        print(f"  Goal tests: {result['goal_tests']}")
        
        print(f"\nPath found:")
        for i, action in enumerate(result['path'], 1):
            print(f"  {i}. {action}")
        
        return result
        
    except StopIteration:
        end_time = time.time()
        result = {
            'solution_found': False,
            'path_cost': float('inf'),
            'path_length': 0,
            'execution_time': (end_time - start_time) * 1000,
            'nodes_expanded': annotated_prob.nodes_expanded,
            'goal_tests': annotated_prob.goal_tests,
            'path': []
        }
        
        print("No solution found")
        print(f"  Execution time: {result['execution_time']:.2f} ms")
        print(f"  Nodes expanded: {result['nodes_expanded']}")
        
        return result

def main():
    print("Py-Search A* Performance Study")
    print("========================================")
    
    # Test different routes with A*
    all_results = []
    
    for route in TEST_ROUTES:
        start, goal = route['start'], route['goal']
        result = run_astar_test(start, goal)
        result['route'] = f"{start} -> {goal}"
        all_results.append(result)
    
    # Summary table
    print("\n\nA* PERFORMANCE SUMMARY")
    print("=" * 78)
    print(f"{'Route':<25} {'Cost(km)':<10} {'Time(ms)':<10} {'Steps':<8} {'Nodes':<8} {'Tests':<8}")
    print("-" * 78)
    
    for result in all_results:
        if result['solution_found']:
            cost = str(result['path_cost'])
            time_str = f"{result['execution_time']:.2f}"
            steps = str(result['path_length'])
            nodes = str(result['nodes_expanded'])
            tests = str(result['goal_tests'])
        else:
            cost = "No solution"
            time_str = f"{result['execution_time']:.2f}"
            steps = str(result['path_length'])
            nodes = str(result['nodes_expanded'])
            tests = str(result['goal_tests'])
        
        print(f"{result['route']:<25} {cost:<10} {time_str:<10} {steps:<8} {nodes:<8} {tests:<8}")
    
    # Average performance
    successful_results = [r for r in all_results if r['solution_found']]
    if successful_results:
        avg_time = sum(r['execution_time'] for r in successful_results) / len(successful_results)
        avg_steps = sum(r['path_length'] for r in successful_results) / len(successful_results)
        avg_nodes = sum(r['nodes_expanded'] for r in successful_results) / len(successful_results)
        avg_tests = sum(r['goal_tests'] for r in successful_results) / len(successful_results)
        
        print("\nAverage performance:")
        print(f"  Execution time: {avg_time:.2f} ms")
        print(f"  Path length: {avg_steps:.1f} steps")
        print(f"  Nodes expanded: {avg_nodes:.1f}")
        print(f"  Goal tests: {avg_tests:.1f}")

if __name__ == "__main__":
    main() 