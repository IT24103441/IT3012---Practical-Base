from collections import deque
import heapq
import random


class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'  # Can be 'BFS', 'DFS', or 'UCS'

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
        came_from = {}  # state -> (parent_state, action)

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
                new_cost = current_cost + 1  # Uniform cost of 1 per step
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(frontier, (new_cost, neighbor))
                    came_from[neighbor] = (current, action)

        return []
