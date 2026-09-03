import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("X-O Game")

        # Initialize the board
        self.board = [" "] * 9
        self.current_player = "X"
        
        # Create buttons for the Tic-Tac-Toe grid
        self.buttons = [tk.Button(master, text=" ", font='Helvetica 20 bold', height=3, width=6,
                                  command=lambda i=i: self.on_click(i)) for i in range(9)]
        
        # Grid the buttons
        for i in range(9):
            row = i // 3
            col = i % 3
            self.buttons[i].grid(row=row, column=col)
        
    def on_click(self, index):
        if self.board[index] == " ":
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)

            winner, winning_combo = self.check_winner()
            if winner:
                self.draw_winning_line(winning_combo)
                messagebox.showinfo("Tic-Tac-Toe", f"Player {winner} wins!")
                self.reset_board()
            elif " " not in self.board:
                messagebox.showinfo("Tic-Tac-Toe", "It's a draw!")
                self.reset_board()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

    def check_winner(self):
        winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8),
                                (0, 4, 8), (2, 4, 6)]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != " ":
                return self.board[combo[0]], combo
        return None, None

    def draw_winning_line(self, combo):
        for index in combo:
            self.buttons[index].config(bg="green")  # Change background color of winning buttons

    def reset_board(self):
        self.board = [" "] * 9
        for button in self.buttons:
            button.config(text=" ", bg="SystemButtonFace")  # Reset button text and color

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()