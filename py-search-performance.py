import time
import json
import math
from py_search.base import Problem, Node, AnnotatedProblem
from py_search.informed import best_first_search

class BrazilRouteSearch:
    def __init__(self, data_file='brazil_cities_data.json'):
        """Initialize with data from JSON file"""
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.cities = data['cities']
        self.test_routes = data['test_routes']
        
        # Build bidirectional roads dictionary
        self.roads = {}
        for road in data['roads']:
            self._add_bidirectional_road(road['from'], road['to'], road['distance'])
    
    def _add_bidirectional_road(self, city1, city2, distance):
        """Add bidirectional road connection"""
        for city in [city1, city2]:
            if city not in self.roads:
                self.roads[city] = {}
        
        self.roads[city1][city2] = distance
        self.roads[city2][city1] = distance
    
    def heuristic(self, city1, city2):
        """Calculate Euclidean distance heuristic between cities"""
        if city1 not in self.cities or city2 not in self.cities:
            return 0
        
        c1, c2 = self.cities[city1], self.cities[city2]
        lat_diff = c2['lat'] - c1['lat']
        lng_diff = c2['lng'] - c1['lng']
        
        return math.sqrt(lat_diff**2 + lng_diff**2) * 111  # km per degree
    
    def search(self, start, goal):
        """Perform A* search and return comprehensive results"""
        problem = RouteProblem(start, goal, self.roads, self.heuristic)
        annotated_prob = AnnotatedProblem(problem)
        
        start_time = time.time()
        try:
            solution = next(best_first_search(annotated_prob))
            execution_time = (time.time() - start_time) * 1000
            
            return {
                'solution_found': True,
                'path_cost': solution.cost(),
                'path_length': len(solution.path()),
                'execution_time': execution_time,
                'nodes_expanded': annotated_prob.nodes_expanded,
                'goal_tests': annotated_prob.goal_tests,
                'path': list(solution.path())
            }
        except StopIteration:
            return {
                'solution_found': False,
                'path_cost': float('inf'),
                'path_length': 0,
                'execution_time': (time.time() - start_time) * 1000,
                'nodes_expanded': annotated_prob.nodes_expanded,
                'goal_tests': annotated_prob.goal_tests,
                'path': []
            }
    
    def run_performance_study(self):
        """Run complete performance study and display results"""
        print("Py-Search A* Performance Study")
        print("=" * 40)
        
        results = []
        for route in self.test_routes:
            start, goal = route['start'], route['goal']
            result = self.search(start, goal)
            result['route'] = f"{start} -> {goal}"
            
            self._print_individual_result(start, goal, result)
            results.append(result)
        
        self._print_summary(results)
        return results
    
    def _print_individual_result(self, start, goal, result):
        """Print individual search result"""
        print(f"\nTesting A* search: {start} -> {goal}")
        print("=" * 50)
        
        if result['solution_found']:
            print("Solution found!")
            print(f"  Cost: {result['path_cost']} km")
            print(f"  Steps: {result['path_length']}")
            print(f"  Execution time: {result['execution_time']:.2f} ms")
            print(f"  Nodes expanded: {result['nodes_expanded']}")
            print(f"  Goal tests: {result['goal_tests']}")
            
            print("\nPath found:")
            for i, action in enumerate(result['path'], 1):
                print(f"  {i}. {action}")
        else:
            print("No solution found")
            print(f"  Execution time: {result['execution_time']:.2f} ms")
            print(f"  Nodes expanded: {result['nodes_expanded']}")
    
    def _print_summary(self, results):
        """Print performance summary table"""
        print("\n\nA* PERFORMANCE SUMMARY")
        print("=" * 78)
        print(f"{'Route':<25} {'Cost(km)':<10} {'Time(ms)':<10} {'Steps':<8} {'Nodes':<8} {'Tests':<8}")
        print("-" * 78)
        
        for result in results:
            cost = str(result['path_cost']) if result['solution_found'] else "No solution"
            print(f"{result['route']:<25} {cost:<10} {result['execution_time']:<10.2f} "
                  f"{result['path_length']:<8} {result['nodes_expanded']:<8} {result['goal_tests']:<8}")
        
        # Calculate and display averages
        successful = [r for r in results if r['solution_found']]
        if successful:
            avg_time = sum(r['execution_time'] for r in successful) / len(successful)
            avg_steps = sum(r['path_length'] for r in successful) / len(successful)
            avg_nodes = sum(r['nodes_expanded'] for r in successful) / len(successful)
            avg_tests = sum(r['goal_tests'] for r in successful) / len(successful)
            
            print(f"\nAverage performance:")
            print(f"  Execution time: {avg_time:.2f} ms")
            print(f"  Path length: {avg_steps:.1f} steps")
            print(f"  Nodes expanded: {avg_nodes:.1f}")
            print(f"  Goal tests: {avg_tests:.1f}")

class RouteProblem(Problem):
    """Route finding problem implementation"""
    def __init__(self, start, goal, roads, heuristic_func):
        super().__init__(start, goal)
        self.roads = roads
        self.heuristic_func = heuristic_func
    
    def successors(self, node):
        """Generate successor nodes"""
        if node.state not in self.roads:
            return []
        
        return [Node(city, parent=node, action=f"drive to {city}", 
                    node_cost=node.cost() + distance)
                for city, distance in self.roads[node.state].items()]
    
    def node_value(self, node):
        """Calculate f(n) = g(n) + h(n)"""
        goal_state = self.goal.state if hasattr(self.goal, 'state') else self.goal
        return node.cost() + self.heuristic_func(node.state, goal_state)
    
    def heuristic(self, node):
        """Heuristic function wrapper"""
        goal_state = self.goal.state if hasattr(self.goal, 'state') else self.goal
        return self.heuristic_func(node.state, goal_state)

if __name__ == "__main__":
    search_engine = BrazilRouteSearch()
    search_engine.run_performance_study() 