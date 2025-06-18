from py_search.base import Problem, Node, AnnotatedProblem
from py_search.informed import best_first_search
import time
import math

# Simple Brazil cities map for testing
brazil_cities = {
    'São Paulo': (-23.55, -46.63),
    'Rio de Janeiro': (-22.91, -43.21),
    'Belo Horizonte': (-19.92, -43.93),
    'Brasília': (-15.79, -47.88),
    'Salvador': (-12.97, -38.48),
    'Fortaleza': (-3.73, -38.53),
    'Manaus': (-3.12, -60.02),
    'Porto Alegre': (-30.03, -51.23),
    'Curitiba': (-25.43, -49.27),
    'Recife': (-8.05, -34.90),
    'Belém': (-1.46, -48.50)
}

# Road connections (simplified for testing)
roads = {
    'São Paulo': [('Rio de Janeiro', 430), ('Belo Horizonte', 580), ('Curitiba', 410), ('Brasília', 1020)],
    'Rio de Janeiro': [('São Paulo', 430), ('Belo Horizonte', 440), ('Brasília', 1170), ('Salvador', 1630)],
    'Belo Horizonte': [('São Paulo', 580), ('Rio de Janeiro', 440), ('Brasília', 730), ('Salvador', 1370)],
    'Brasília': [('São Paulo', 1020), ('Rio de Janeiro', 1170), ('Belo Horizonte', 730), ('Salvador', 1440), ('Fortaleza', 2200), ('Manaus', 3450)],
    'Salvador': [('Rio de Janeiro', 1630), ('Belo Horizonte', 1370), ('Brasília', 1440), ('Recife', 840), ('Fortaleza', 1200)],
    'Fortaleza': [('Salvador', 1200), ('Brasília', 2200), ('Recife', 810), ('Belém', 1400)],
    'Manaus': [('Brasília', 3450), ('Belém', 1300)],
    'Porto Alegre': [('São Paulo', 1130), ('Curitiba', 710)],
    'Curitiba': [('São Paulo', 410), ('Porto Alegre', 710)],
    'Recife': [('Salvador', 840), ('Fortaleza', 810)],
    'Belém': [('Manaus', 1300), ('Fortaleza', 1400)]
}

def calculate_distance(city1, city2):
    # Simple euclidean distance for heuristic
    lat1, lon1 = brazil_cities[city1]
    lat2, lon2 = brazil_cities[city2]
    return math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111  # rough km conversion

class RouteProblem(Problem):
    def __init__(self, start, goal):
        super().__init__(start, goal)
    
    def successors(self, node):
        current = node.state
        result = []
        if current in roads:
            for city, distance in roads[current]:
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
    print("=" * 40)
    
    # Test different routes with A*
    test_routes = [
        ("São Paulo", "Belém"),
        ("Rio de Janeiro", "Manaus"),
        ("Curitiba", "Salvador"),
        ("Porto Alegre", "Fortaleza"),
        ("Belo Horizonte", "Recife")
    ]
    
    all_results = []
    
    for start, goal in test_routes:
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