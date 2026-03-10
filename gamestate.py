class GameState:
    def __init__(self, grid_width, grid_height):
        self.loop_count = 1
        self.level = 1
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.heatmap = [[0 for _ in range(grid_height)] for _ in range(grid_width)]
        
    def update_heatmap(self, visited_nodes):
        for node in visited_nodes:
            if 0 <= node.x < self.grid_width and 0 <= node.y < self.grid_height:
                self.heatmap[node.x][node.y] += 1
        
    def reset_loop(self, visited_nodes, success=False):
        self.update_heatmap(visited_nodes)
        self.loop_count += 1
        if success:
            self.level += 1
        return self.heatmap
