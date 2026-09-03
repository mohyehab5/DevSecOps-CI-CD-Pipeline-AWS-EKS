import tkinter as tk
from tkinter import Canvas, messagebox

class ChessBoard:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess")
        self.canvas = Canvas(master, width=600, height=600)  # Smaller board
        self.canvas.pack()
        self.board = self.create_board()
        self.pieces = self.create_pieces()
        self.selected_piece = None
        self.turn = "white"
        self.valid_moves = []
        self.draw_pieces()

    def create_board(self):
        board = []
        colors = ["#DDB88C", "#A66D4F"]
        for i in range(8):
            row = []
            for j in range(8):
                color = colors[(i+j) % 2]
                rect = self.canvas.create_rectangle(j*75, i*75, j*75 + 75, i*75 + 75, fill=color, tags="square")  # Smaller squares
                row.append(rect)
            board.append(row)
        return board

    def create_pieces(self):
        pieces = {
            "white": ["R", "N", "B", "Q", "K", "B", "N", "R"] + ["P"]*8,
            "black": ["r", "n", "b", "q", "k", "b", "n", "r"] + ["p"]*8
        }
        piece_objects = []
        for color, piece_row in pieces.items():
            row = 0 if color == "black" else 7
            pawn_row = 1 if color == "black" else 6
            for i in range(8):
                piece_objects.append((piece_row[i], row, i, color))
                piece_objects.append((piece_row[8], pawn_row, i, color))
        return piece_objects

    def draw_pieces(self):
        self.canvas.delete("piece")
        for piece, row, col, color in self.pieces:
            x = col * 75 + 37.5
            y = row * 75 + 37.5
            text_color = "white" if color == "black" else "black"
            self.canvas.create_text(x, y, text=piece, font=("Helvetica", 36), fill=text_color, tags="piece")

    def draw_highlight(self):
        self.canvas.delete("highlight")
        for x, y in self.valid_moves:
            self.canvas.create_rectangle(x*75, y*75, x*75 + 75, y*75 + 75, outline="red", width=3, tags="highlight")

    def on_click(self, event):
        x, y = event.x // 75, event.y // 75
        piece = self.get_piece_at(x, y)
        if self.selected_piece:
            if (x, y) in self.valid_moves:
                self.move_piece(self.selected_piece, x, y)
            self.selected_piece = None
            self.valid_moves = []
        elif piece and piece[3] == self.turn:
            self.selected_piece = (piece, x, y)
            self.valid_moves = self.get_valid_moves(piece, x, y)
        self.draw_highlight()

    def get_piece_at(self, x, y):
        for piece in self.pieces:
            if piece[1] == y and piece[2] == x:
                return piece
        return None

    def move_piece(self, selected_piece, x, y):
        piece, old_x, old_y, color = selected_piece[0]
        self.pieces = [(p, r, c, col) if (p, r, c, col) != selected_piece[0] else (piece, y, x, color) for (p, r, c, col) in self.pieces]
        self.draw_pieces()
        self.turn = "black" if self.turn == "white" else "white"

    def get_valid_moves(self, piece, old_x, old_y):
        valid_moves = []
        if piece.lower() == 'p':  # Pawn
            direction = 1 if piece.islower() else -1
            valid_moves.append((old_x, old_y + direction))
        elif piece.lower() == 'r':  # Rook
            for i in range(8):
                if i != old_y:
                    valid_moves.append((old_x, i))
                if i != old_x:
                    valid_moves.append((i, old_y))
        elif piece.lower() == 'n':  # Knight
            moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
            for dx, dy in moves:
                valid_moves.append((old_x + dx, old_y + dy))
        elif piece.lower() == 'b':  # Bishop
            for i in range(1, 8):
                valid_moves.append((old_x + i, old_y + i))
                valid_moves.append((old_x - i, old_y - i))
                valid_moves.append((old_x + i, old_y - i))
                valid_moves.append((old_x - i, old_y + i))
        elif piece.lower() == 'q':  # Queen
            for i in range(8):
                if i != old_y:
                    valid_moves.append((old_x, i))
                if i != old_x:
                    valid_moves.append((i, old_y))
            for i in range(1, 8):
                valid_moves.append((old_x + i, old_y + i))
                valid_moves.append((old_x - i, old_y - i))
                valid_moves.append((old_x + i, old_y - i))
                valid_moves.append((old_x - i, old_y + i))
        elif piece.lower() == 'k':  # King
            moves = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
            for dx, dy in moves:
                valid_moves.append((old_x + dx, old_y + dy))

        # Filter out moves that are out of bounds
        valid_moves = [(x, y) for x, y in valid_moves if 0 <= x < 8 and 0 <= y < 8]
        return valid_moves

    def mainloop(self):
        self.canvas.bind("<Button-1>", self.on_click)
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessBoard(root)
    game.mainloop()
