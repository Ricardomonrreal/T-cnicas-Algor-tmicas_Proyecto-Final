import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import time
import copy
import random
import numpy as np


class SudokuSolver:
#CONSTRUCTORES DE TODO EL SUDOKU
    def __init__(self, master):
        self.master = master
        self.master.title("Sudoku Ejercicio Final")
        self.master.geometry("900x900")
        
        self.game_board = [[0]*9 for _ in range(9)]
        self.entries = [[None]*9 for _ in range(9)]
        self.log_text = None
        self.is_solving = False
        self.grid_frames = [[None]*3 for _ in range(3)]
        self.highlighted_subgrids = set()  # Para rastrear subcuadrículas ya resaltadas
        
        self.setup_grid()
        self.setup_controls()
        self.setup_log()

    def setup_grid(self):
        main_frame = tk.Frame(self.master, borderwidth=2, relief=tk.RAISED)
        main_frame.pack(pady=20)
        
        # Crear 9 frames para las subcuadrículas
        for grid_i in range(3):
            for grid_j in range(3):
                grid_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.RAISED, bg='lightgray')
                grid_frame.grid(row=grid_i, column=grid_j, padx=3, pady=3)
                self.grid_frames[grid_i][grid_j] = grid_frame
                
                # Crear las celdas dentro de cada subcuadrícula
                for i in range(3):
                    for j in range(3):
                        entry = tk.Entry(grid_frame, width=3, font=('Arial', 18), 
                                      justify='center', relief=tk.SUNKEN)
                        entry.grid(row=i, column=j, padx=1, pady=1)
                        
                        # Calcular la posición real en el tablero completo
                        real_i = grid_i * 3 + i
                        real_j = grid_j * 3 + j
                        self.entries[real_i][real_j] = entry

    def highlight_subgrid(self, grid_i, grid_j, color='yellow'):
        """Resalta una subcuadrícula específica"""
        self.grid_frames[grid_i][grid_j].config(bg=color)
        self.master.update_idletasks()

    def reset_subgrid_highlight(self, grid_i, grid_j):
        """Resetea el color de una subcuadrícula a su estado normal"""
        self.grid_frames[grid_i][grid_j].config(bg='lightgray')
        self.master.update_idletasks()

    def highlight_row_col(self, row, col, color='mistyrose'):
        """Resalta toda la fila y columna de una celda específica"""
        # Resaltar fila
        for j in range(9):
            entry = self.entries[row][j]
            entry.config(bg=color)
        
        # Resaltar columna
        for i in range(9):
            entry = self.entries[i][col]
            entry.config(bg=color)
        
        self.master.update_idletasks()
    
    def reset_row_col_highlight(self, row, col):
        """Resetea el color de la fila y columna a su estado normal"""
        # Resetear fila
        for j in range(9):
            entry = self.entries[row][j]
            entry.config(bg='white')
        
        # Resetear columna
        for i in range(9):
            entry = self.entries[i][col]
            entry.config(bg='white')
        
        self.master.update_idletasks()

    def setup_controls(self):
        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=10)

        # Solving Method Selection
        tk.Label(control_frame, text="Método de solución:").pack(side=tk.LEFT)
        self.solve_method = tk.StringVar(value="Backtracking")
        solve_methods = [ "Cuadrícula x Cuadrícula", "Backtracking", "Memoización"]
        method_dropdown = ttk.Combobox(control_frame, 
                                    textvariable=self.solve_method, 
                                    values=solve_methods, 
                                    state="readonly", 
                                    width=15)
        method_dropdown.pack(side=tk.LEFT, padx=10)

        # Difficulty Selection
        tk.Label(control_frame, text="Dificultad:").pack(side=tk.LEFT)
        self.difficulty = tk.StringVar(value="Normal")
        difficulty_levels = ["Fácil", "Normal", "Difícil"]
        difficulty_dropdown = ttk.Combobox(control_frame, 
                                        textvariable=self.difficulty, 
                                        values=difficulty_levels, 
                                        state="readonly", 
                                        width=10)
        difficulty_dropdown.pack(side=tk.LEFT, padx=10)

        # Buttons Frame
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        # Generate Random Board Button
        generate_button = tk.Button(button_frame, text='Generar Sudoku', command=self.generate_random_board)
        generate_button.pack(side=tk.LEFT, padx=5)

        # Solve Button
        solve_button = tk.Button(button_frame, text='Resolver Sudoku', command=self.solve_sudoku)
        solve_button.pack(side=tk.LEFT, padx=5)

        # Clear Button
        clear_button = tk.Button(button_frame, text='Limpiar Sudoku', command=self.clear_board)
        clear_button.pack(side=tk.LEFT, padx=5)

    def setup_log(self):
        log_frame = tk.Frame(self.master)
        log_frame.pack(pady=10, fill=tk.X)

        log_label = tk.Label(log_frame, text="Consola de Registro:")
        log_label.pack()

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, 
                                                wrap=tk.WORD, font=('Courier', 10))
        self.log_text.pack(fill=tk.X)

    def log_message(self, message):
        if self.log_text:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.update_idletasks()

    def clear_board(self):
        self.highlighted_subgrids = set()  # Reiniciar el conjunto de subcuadrículas resaltadas
        for i in range(9):
            for j in range(9):
                self.entries[i][j].config(state='normal', bg='white')
                self.entries[i][j].delete(0, tk.END)
                self.game_board[i][j] = 0
                self.entries[i][j].config(fg='black', font=('Arial', 18))
        
        if self.log_text:
            self.log_text.delete('1.0', tk.END)
        
        self.log_message("Sudoku limpio!")

    def generate_random_board(self):
        self.clear_board()
        difficulty = self.difficulty.get()
        solved_board = self.generate_full_valid_board()
        clues = {"Fácil": 40, "Normal": 30, "Difícil": 20}
        board = [row.copy() for row in solved_board]
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        for i, j in positions[clues[difficulty]:]:
            board[i][j] = 0
        
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    self.entries[i][j].insert(0, str(board[i][j]))
                    self.entries[i][j].config(state='readonly')
        
        self.game_board = board
        self.log_message(f"Sudoku de dificultad {difficulty} generado")

    def generate_full_valid_board(self):
        board = [[0]*9 for _ in range(9)]
        self.fill_board(board)
        return board

    def fill_board(self, board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if self.is_valid_move(board, row, col, num):
                            board[row][col] = num
                            if self.fill_board(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

    def solve_sudoku(self):
        start_time = time.time()
        if self.is_solving:
            return
        self.read_board()
        
        method = self.solve_method.get()
        success = False
        
        if method == "Backtracking":
            self.is_solving = True
            self.log_message("Resolviendo paso a paso...")
            self.step_by_step_solve(0, 0)
            grid_copy = copy.deepcopy(self.game_board)
            success = self.backtracking_solve(grid_copy)
            if success:
                self.game_board = grid_copy

        elif method == "Cuadrícula x Cuadrícula":
            success = self.grid_by_grid_solve()
        
        elif method == "Memoización":
            success = self.dynamic_programming_solve()

        if success:
            self.display_solution()
            elapsed_time = time.time() - start_time
            messagebox.showinfo("Result", f"Sudoku solved using {method} in {elapsed_time:.2f} seconds.")
        else:
            messagebox.showinfo("Result", "No solution exists for this Sudoku.")

# MÉTODO DE CUADRÍCULA POR CUADRÍCULA (DIVIDE Y VENCERÁS)
    def grid_by_grid_solve(self):
        """Resuelve el Sudoku cuadrícula por cuadrícula con backtracking."""
        self.read_board()
        return self.solve_grid_recursive(0, 0)

    def solve_grid_recursive(self, grid_row, grid_col):
        """Resuelve el Sudoku recursivamente por cuadrículas 3x3."""
        # Si hemos llegado al final de las cuadrículas, el puzzle está resuelto
        if grid_row >= 9:
            return True
        
        # Calcula la siguiente cuadrícula
        next_grid_col = (grid_col + 3) % 9
        next_grid_row = grid_row + (3 if next_grid_col == 0 else 0)
        
        # Obtiene las celdas vacías en la cuadrícula actual
        empty_cells = []
        for i in range(3):
            for j in range(3):
                row, col = grid_row + i, grid_col + j
                if self.game_board[row][col] == 0:
                    empty_cells.append((row, col))
        
        # Si no hay celdas vacías en esta cuadrícula, pasa a la siguiente
        if not empty_cells:
            return self.solve_grid_recursive(next_grid_row, next_grid_col)
        
        # Intenta llenar las celdas vacías
        return self.fill_grid_cells(empty_cells, 0, grid_row, grid_col, next_grid_row, next_grid_col)
    
    def fill_grid_cells(self, empty_cells, cell_index, grid_row, grid_col, next_grid_row, next_grid_col):
        """Llena las celdas vacías de una cuadrícula con backtracking."""
        # Si hemos llenado todas las celdas vacías de esta cuadrícula, 
        # pasamos a la siguiente
        if cell_index >= len(empty_cells):
            return self.solve_grid_recursive(next_grid_row, next_grid_col)
        
        row, col = empty_cells[cell_index]
        
        # Prueba números del 1 al 9
        for num in range(1, 10):
            if self.is_valid_move(self.game_board, row, col, num):
                # Coloca el número y muestra en la interfaz
                self.game_board[row][col] = num
                self.update_entry(row, col, num, "blue")
                self.master.update_idletasks()
                self.master.after(200)  # Pausa visual
                
                # Intenta llenar la siguiente celda
                if self.fill_grid_cells(empty_cells, cell_index + 1, 
                                    grid_row, grid_col, 
                                    next_grid_row, next_grid_col):
                    return True
                
                # Si no funciona, retrocede
                self.game_board[row][col] = 0
                self.update_entry(row, col, "", "black")
                self.master.update_idletasks()
                self.master.after(200)  # Pausa visual
        
        return False

# MÉTODO DE BACKTRACKING (PROGRAMACIÓN DINÁMICA)
    def backtracking_solve(self, board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid_move(board, row, col, num):
                            board[row][col] = num

                            if self.backtracking_solve(board):
                                return True

                            board[row][col] = 0

                    return False
        return True
    
    def step_by_step_solve(self, row, col):
        if row == 9:
            self.is_solving = False
            self.display_solution()
            return True
        
        next_row, next_col = (row, col + 1) if col < 8 else (row + 1, 0)
        if self.game_board[row][col] != 0:
            return self.step_by_step_solve(next_row, next_col)

        for num in range(1, 10):
            if self.is_valid_move(self.game_board, row, col, num):
                self.game_board[row][col] = num
                self.update_entry(row, col, num, "blue")
                self.master.update_idletasks()  # Refresca la interfaz gráfica
                self.master.after(300)  # Pausa de 200 ms entre pasos

                if self.step_by_step_solve(next_row, next_col):
                    return True

                self.game_board[row][col] = 0
                self.update_entry(row, col, "", "black")

        return False

# MÉTODO DE MEMOIZACIÓN (PROGRAMACIÓN DINÁMICA)
    def dynamic_programming_solve(self):
        """Resuelve el Sudoku usando programación dinámica con visualización mejorada."""
        N = 9
        self.memo = [[[False for _ in range(10)] for _ in range(N)] for _ in range(N)]
        self.highlighted_subgrids = set()  # Reiniciar el conjunto de subcuadrículas resaltadas
        
        # Inicializar la memoización y marcar subcuadrículas con números iniciales
        self.log_message("\n=== INICIO DEL PROCESO DE MEMOIZACIÓN ===")
        
        # Marcar subcuadrículas iniciales
        for grid_i in range(3):
            for grid_j in range(3):
                has_numbers = False
                for i in range(3):
                    for j in range(3):
                        real_i = grid_i * 3 + i
                        real_j = grid_j * 3 + j
                        if self.game_board[real_i][real_j] != 0:
                            has_numbers = True
                            num = self.game_board[real_i][real_j]
                            self.memo[real_i][real_j][num] = True
                            self.log_message(f"Celda [{real_i+1},{real_j+1}]: Número inicial {num}")
                
                if has_numbers:
                    self.highlight_subgrid(grid_i, grid_j, 'lightgreen')
                    self.master.after(300)
        
        # Almacenar el historial de movimientos para un mejor backtracking
        self.move_history = []
        result = self.solve_dp_recursive(depth=0)
        return result
                
    def solve_dp_recursive(self, depth=0):
        """Función recursiva principal con manejo inteligente de retrocesos."""
        indent = "  " * depth

        # Primero verificamos si el tablero está completamente lleno (sin ceros)
        is_complete = True
        for i in range(9):
            for j in range(9):
                if self.game_board[i][j] == 0:
                    is_complete = False
                    break
            if not is_complete:
                break

        if is_complete:
            self.log_message(f"{indent}✓ Solución encontrada!")
            return True

        cell = self.get_next_cell_dp()
        if not cell:
            return False

        row, col = cell
        grid_i, grid_j = row // 3, col // 3
        grid_key = (grid_i, grid_j)

        self.highlight_subgrid(grid_i, grid_j, 'yellow')
        self.highlight_row_col(row, col, 'mistyrose')
        self.master.update_idletasks()
        self.master.after(500)

        self.reset_row_col_highlight(row, col)
        self.highlighted_subgrids.add(grid_key)

        possibilities = self.get_possibilities(row, col)
        self.log_message(f"\n{indent}Analizando celda [{row+1},{col+1}] en subcuadrícula [{grid_i+1},{grid_j+1}]")
        self.log_message(f"{indent}Posibilidades: {possibilities}")

        if not possibilities:
            self.log_message(f"{indent}✗ Sin posibilidades válidas para [{row+1},{col+1}], retrocediendo")
            return False

        for num in possibilities:
            self.game_board[row][col] = num
            self.memo[row][col][num] = True
            self.move_history.append((row, col, num))
            
            self.log_message(f"{indent}→ Probando {num} en [{row+1},{col+1}]")
            self.update_entry(row, col, num, "blue")
            self.master.update_idletasks()
            self.master.after(300)

            if self.solve_dp_recursive(depth + 1):
                # Verificar que no haya ceros antes de aceptar la solución
                has_zeros = any(self.game_board[i][j] == 0 
                            for i in range(9) 
                            for j in range(9))
                if not has_zeros:
                    self.highlight_subgrid(grid_i, grid_j, 'lightgreen')
                    return True

            # Si llegamos aquí, necesitamos deshacer el movimiento actual
            if self.move_history:  # Verificamos que la lista no esté vacía
                self.move_history.pop()
            self.game_board[row][col] = 0
            self.memo[row][col][num] = False
            self.update_entry(row, col, "", "black")
            self.log_message(f"{indent}← Valor {num} en [{row+1},{col+1}] no lleva a solución completa")
            self.master.update_idletasks()
            self.master.after(200)

        if grid_key in self.highlighted_subgrids:
            self.reset_subgrid_highlight(grid_i, grid_j)
            self.highlighted_subgrids.remove(grid_key)
        
        self.log_message(f"{indent}✗ Ninguna posibilidad en [{row+1},{col+1}] lleva a solución completa")
        return False

    def get_next_cell_dp(self):
        """Encuentra la siguiente celda vacía con el menor número de posibilidades."""
        min_possibilities = float('inf')
        next_cell = None
        
        for i in range(9):
            for j in range(9):
                if self.game_board[i][j] == 0:
                    possibilities = self.get_possibilities(i, j)
                    count = len(possibilities)
                    if count > 0 and count < min_possibilities:
                        min_possibilities = count
                        next_cell = (i, j)
        
        return next_cell

    def get_possibilities(self, row, col):
        """Obtiene todas las posibilidades válidas para una celda."""
        return [num for num in range(1, 10)
                if not self.memo[row][col][num] and
                self.is_valid_move(self.game_board, row, col, num)]

# FUNCIONES GENERALES
    def update_entry(self, row, col, value, color):
        """Actualiza una celda en la interfaz gráfica."""
        entry = self.entries[row][col]
        entry.config(state='normal')
        entry.delete(0, tk.END)
        if value:
            entry.insert(0, str(value))
        entry.config(fg=color)
        entry.update_idletasks()
    
    def read_board(self):
        for i in range(9):
            for j in range(9):
                entry_value = self.entries[i][j].get()
                self.game_board[i][j] = int(entry_value) if entry_value.isdigit() else 0

    def display_solution(self):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].config(state='normal')
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(self.game_board[i][j]))
                self.entries[i][j].config(fg='blue', font=('Arial', 18, 'bold'), state='readonly')

    def is_valid_move(self, board, row, col, num):
        for x in range(9):
            if board[row][x] == num and x != col:
                return False
        for x in range(9):
            if board[x][col] == num and x != row:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num and (start_row + i, start_col + j) != (row, col):
                    return False
        return True

def main():
    root = tk.Tk()
    app = SudokuSolver(root)
    root.mainloop()

main()