import math
from collections import deque
import heapq
import random
 
 
class SearchAgent:
 
    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'  # Can be 'BFS', 'DFS', 'UCS', or 'AStar'
 
    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:

            agent_pos = tuple(percept['agent_pos'])
            all_food = percept['all_food']
 
            if not all_food:
                return 'Stay'
             
            target_food = min(
                all_food,
                key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1])
            )
 
            grid_size = percept['grid_size']
            walls = set(percept['walls'])
 
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, target_food, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, target_food, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, target_food, grid_size, walls)

            else:
                self.plan = []
 
        if self.plan:
            return self.plan.pop(0)
        return 'Stay'
 
    def get_neighbors(self, current, grid_size, walls):
 
        x, y = current
        width, height = grid_size
        neighbors = []
 
        potential_moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]
 
        for action, (nx, ny) in potential_moves:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                neighbors.append(((nx, ny), action))
 
        return neighbors
 
    def reconstruct_path(self, came_from, current):
        actions = []
        while current in came_from:
            prev_node, action = came_from[current]
            actions.insert(0, action)
            current = prev_node
        return actions
 
    def bfs_search(self, start, goal, grid_size, walls):
        frontier = deque([start])
        reached = {start}
        came_from = {}  
 
        if start == goal:
            return []
 
        while frontier:
            current = frontier.popleft()
 
            if current == goal:
                return self.reconstruct_path(came_from, current)
 
            for neighbor, action in self.get_neighbors(current, grid_size, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    came_from[neighbor] = (current, action)
                    frontier.append(neighbor)
 
        return []
 
    def dfs_search(self, start, goal, grid_size, walls):
        frontier = [start]
        reached = {start}
        came_from = {}
 
        if start == goal:
            return []
 
        while frontier:
            current = frontier.pop()
 
            if current == goal:
                return self.reconstruct_path(came_from, current)
 
            for neighbor, action in self.get_neighbors(current, grid_size, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    came_from[neighbor] = (current, action)
                    frontier.append(neighbor)
 
        return []
 
    def ucs_search(self, start, goal, grid_size, walls):
        frontier = [(0, start)]
        came_from = {}
        cost_so_far = {start: 0}
 
        if start == goal:
            return []
 
        while frontier:
            current_cost, current = heapq.heappop(frontier)
 
            if current == goal:
                return self.reconstruct_path(came_from, current)
 
            for neighbor, action in self.get_neighbors(current, grid_size, walls):
                new_cost = current_cost + 1  
 
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(frontier, (new_cost, neighbor))
                    came_from[neighbor] = (current, action)
 
        return []
 
    def manhattan_distance(self, pos, goal):
        """h(n) = |x1 - x2| + |y1 - y2|"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
 
    def euclidean_distance(self, pos, goal):
        """h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)"""
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)
 
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """
        A* search using f(n) = g(n) + h(n).
        Frontier tuples are formatted as: (f_cost, g_cost, current_pos, path_taken)
        """
        if heuristic_type == 'manhattan':
            h_func = self.manhattan_distance
        elif heuristic_type == 'euclidean':
            h_func = self.euclidean_distance
        else:
            h_func = self.manhattan_distance
 
        if start_pos == goal_pos:
            return []
 
        frontier = []
        reached_states = set()
 
        start_g = 0
        start_h = h_func(start_pos, goal_pos)
        start_f = start_g + start_h
 
        heapq.heappush(frontier, (start_f, start_g, start_pos, []))
 
        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)
 
            if current_pos == goal_pos:
                return path_taken
 
            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)
 
            for neighbor, action in self.get_neighbors(current_pos, grid_size, walls):
                if neighbor not in reached_states:
                    g_new = g_cost + 1
                    h_new = h_func(neighbor, goal_pos)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, g_new, neighbor, path_taken + [action]))
 
        return []
 
if __name__ == '__main__':
    agent = SearchAgent()
 
    start = (0, 0)
    goal = (3, 4)
 
    manhattan_result = agent.manhattan_distance(start, goal)
    euclidean_result = agent.euclidean_distance(start, goal)
 
    print(f"Manhattan distance from {start} to {goal}: {manhattan_result}")
    print(f"Euclidean distance from {start} to {goal}: {euclidean_result}")
 
    assert manhattan_result == 7, "Manhattan distance check failed!"
    assert euclidean_result == 5.0, "Euclidean distance check failed!"
    print("Testing checkpoint passed.")
