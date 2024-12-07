import tkinter as tk
from tkinter import ttk
import math
from collections import Counter
import customtkinter as ctk
from pathlib import Path

STARTING_WORDS = {
    'stare': 5.92, 'crane': 5.89, 'trace': 5.88, 
    'adieu': 5.85, 'audio': 5.83
}

LETTER_FREQUENCIES = {
    'e': 0.13, 'a': 0.12, 'r': 0.11, 'i': 0.10,
    'o': 0.09, 't': 0.09, 'n': 0.08, 's': 0.08,
    'l': 0.07, 'c': 0.06, 'u': 0.06, 'd': 0.05
}

class WordleSolverGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Wordle diddy Solver")
        self.root.geometry("600x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.load_words()
        self.current_words = self.words.copy()
        self.current_row = 0
        self.all_yellow_positions = {}
        self.all_correct_positions = {}
        self.all_wrong_letters = set()
        self.entropy_cache = {}
        self.used_words = set()
        
        self.setup_gui()
        self.suggest_best_word()

    def load_words(self):
        file_path = Path(__file__).parent / "allowed_words.txt"
        with open(file_path, 'r') as file:
            self.words = [word.strip().lower() for word in file.readlines()]

    
    def setup_gui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        title = ctk.CTkLabel(main_frame, text="Wordle Skibididdy Solver", 
                            font=("Helvetica", 24, "bold"))
        title.pack(pady=20)
        
        self.input_frame = ctk.CTkFrame(main_frame)
        self.input_frame.pack(pady=20)
        
        self.letter_entries = []
        for i in range(5):
            entry = ctk.CTkEntry(self.input_frame, width=50, height=50,
                               font=("Courier", 24, "bold"),
                               justify='center')
            entry.grid(row=0, column=i, padx=5)
            entry.bind('<KeyPress>', lambda e, pos=i: self.handle_key_press(e, pos))
            self.letter_entries.append(entry)
        
        self.grid_frame = ctk.CTkFrame(main_frame)
        self.grid_frame.pack(pady=20)
        
        self.letter_labels = []
        for row in range(6):
            row_labels = []
            for col in range(5):
                label = ctk.CTkLabel(self.grid_frame, text="", width=50, height=50,
                                   font=("Courier", 24, "bold"),
                                   fg_color="gray30", corner_radius=8)
                label.grid(row=row, column=col, padx=5, pady=5)
                row_labels.append(label)
            self.letter_labels.append(row_labels)
        
        self.reset_btn = ctk.CTkButton(main_frame, text="New Game", 
                                     command=self.reset_game,
                                     font=("Helvetica", 16))
        self.reset_btn.pack(pady=10)
        
        self.suggestion_label = ctk.CTkLabel(main_frame, text="", 
                                           font=("Helvetica", 16))
        self.suggestion_label.pack(pady=10)
        
        self.count_label = ctk.CTkLabel(main_frame, text="", 
                                       font=("Helvetica", 16))
        self.count_label.pack(pady=10)
        
        self.remaining_words_label = ctk.CTkTextbox(main_frame, width=400, height=100,
                                                   font=("Helvetica", 14))
        self.remaining_words_label.pack(pady=10)
        
        instructions = """
        Type x/y/g to mark each letter:
        g = green (correct position)
        y = yellow (wrong position)
        x = gray (not in word)
        """
        ctk.CTkLabel(main_frame, text=instructions, 
                    font=("Helvetica", 14)).pack(pady=20)

    def suggest_best_word(self):
        valid_words = self.filter_words(self.words)
        
        if not valid_words:
            self.suggestion_label.configure(text="No possible words remaining")
            return
            
        word_scores = {}
        for word in valid_words[:min(200, len(valid_words))]:
            word_scores[word] = self.calculate_entropy(word, valid_words)
            unique_letters = len(set(word))
            word_scores[word] += unique_letters * 0.5
            common_letters = 'etaoinshrdlu'
            common_letter_count = sum(1 for letter in word if letter in common_letters)
            word_scores[word] += common_letter_count * 0.3
            
        best_word = max(word_scores.items(), key=lambda x: x[1])[0]
        
        self.suggestion_label.configure(text=f"Suggested word: {best_word}")
        for i, letter in enumerate(best_word):
            self.letter_entries[i].delete(0, tk.END)
            self.letter_entries[i].insert(0, letter.upper())
        self.letter_entries[0].focus()

    def handle_key_press(self, event, position):
        if event.char.lower() in ['x', 'y', 'g']:
            entry = self.letter_entries[position]
            current_letter = entry.get()
            print(f"Position {position}: Letter {current_letter} marked as {event.char.lower()}")
            
            if event.char.lower() == 'x':
                entry.configure(fg_color="gray30")
            elif event.char.lower() == 'y':
                entry.configure(fg_color="gold")
            elif event.char.lower() == 'g':
                entry.configure(fg_color="green")
            
            if position < 4:
                self.letter_entries[position + 1].focus()
            else:
                print("Processing complete word...")
                self.process_current_input()
            
            return "break"

    def process_current_input(self):
        word = ''.join(entry.get() for entry in self.letter_entries)
        pattern = ''
        for entry in self.letter_entries:
            if entry.cget('fg_color') == "gray30":
                pattern += 'x'
            elif entry.cget('fg_color') == "gold":
                pattern += 'y'
            else:
                pattern += 'g'
        
        print(f"Processing word: {word}")
        print(f"Detected pattern: {pattern}")
        
        # Update skib history grid
        for i in range(5):
            self.letter_labels[self.current_row][i].configure(
                text=self.letter_entries[i].get(),
                fg_color=self.letter_entries[i].cget('fg_color')
            )
        
        yellow_positions_this_guess = {}
        
        for i, (letter, result) in enumerate(zip(word, pattern)):
            if result == 'g':
                self.all_correct_positions[i] = letter
                self.all_wrong_letters.discard(letter)
            elif result == 'y':
                if letter not in yellow_positions_this_guess:
                    yellow_positions_this_guess[letter] = {i}
                else:
                    yellow_positions_this_guess[letter].add(i)
                self.all_wrong_letters.discard(letter)
            else:
                if (letter not in yellow_positions_this_guess and
                    letter not in self.all_correct_positions.values()):
                    self.all_wrong_letters.add(letter)
        
        self.all_yellow_positions.update(yellow_positions_this_guess)
        
        print(f"After processing:")
        print(f"Correct positions: {self.all_correct_positions}")
        print(f"Yellow positions: {self.all_yellow_positions}")
        print(f"Wrong letters: {self.all_wrong_letters}")
        
        self.current_words = self.filter_words(self.current_words)
        print(f"Remaining words: {len(self.current_words)}")
        
        self.remaining_words_label.delete('1.0', tk.END)
        self.remaining_words_label.insert('1.0', ', '.join(self.current_words[:20]))
        
        self.current_row += 1
        self.count_label.configure(text=f"Possible words: {len(self.current_words)}")
        
        for entry in self.letter_entries:
            entry.delete(0, tk.END)
            entry.configure(fg_color="gray30")
        
        self.suggest_best_word()

    def reset_game(self):
        self.current_words = self.words.copy()
        self.current_row = 0
        self.all_yellow_positions = {}
        self.all_correct_positions = {}
        self.all_wrong_letters = set()
        
        for row in self.letter_labels:
            for label in row:
                label.configure(text="", fg_color="gray30")
        
        for entry in self.letter_entries:
            entry.delete(0, tk.END)
            entry.configure(fg_color="gray30")
        
        self.remaining_words_label.delete('1.0', tk.END)
        self.suggest_best_word()
                
    def filter_words(self, words):
        candidates = set(words)
        
        # Filter for correct positions first
        if self.all_correct_positions:
            candidates = {word for word in candidates
                        if all(word[pos].lower() == letter.lower()
                            for pos, letter in self.all_correct_positions.items())}
        
        # Filter for yellow letters
        for letter, positions in self.all_yellow_positions.items():
            letter_lower = letter.lower()
            candidates = {word for word in candidates
                        if letter_lower in word.lower() and
                        not any(word[pos].lower() == letter_lower for pos in positions)}
        
        # Count correct letter occurrences
        letter_counts = {}
        for letter in self.all_correct_positions.values():
            letter_lower = letter.lower()
            letter_counts[letter_lower] = letter_counts.get(letter_lower, 0) + 1
        
        # Filter wrong letters with frequency check
        filtered = []
        for word in candidates:
            valid = True
            word_counts = {}
            
            # Count letters in word
            for letter in word.lower():
                word_counts[letter] = word_counts.get(letter, 0) + 1
            
            # Check if word has more occurrences than allowed
            for letter in self.all_wrong_letters:
                letter_lower = letter.lower()
                correct_count = letter_counts.get(letter_lower, 0)
                if word_counts.get(letter_lower, 0) > correct_count:
                    valid = False
                    break
            
            if valid:
                filtered.append(word)
        
        print(f"Found {len(filtered)} possible words")
        if filtered:
            print(f"Examples: {filtered[:5]}")
        return filtered


    def calculate_entropy(self, word, possible_words):
        if word in self.entropy_cache:
            return self.entropy_cache[word]
            
        patterns = {}
        total = len(possible_words)
        
        for possible in possible_words:
            pattern = self.get_pattern(word, possible)
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        entropy = -sum((count/total) * math.log2(count/total) 
                    for count in patterns.values())
        
        self.entropy_cache[word] = entropy
        return entropy

    def get_pattern(self, guess, answer):
        pattern = []
        for i, (g, a) in enumerate(zip(guess, answer)):
            if g == a:
                pattern.append('g')
            elif g in answer:
                pattern.append('y')
            else:
                pattern.append('x')
        return ''.join(pattern)
    

    def suggest_best_word(self):
        if not self.current_words:
            self.suggestion_label.configure(text="No possible words remaining")
            return
            
        if len(self.current_words) <= 2:
            best_word = self.current_words[0]
        else:
            if not self.used_words and self.current_words == self.words:
                best_word = max(STARTING_WORDS.items(), key=lambda x: x[1])[0]
            else:
                # Prioritize words that test unused letters
                unused_letters = set('abcdefghijklmnopqrstuvwxyz') - self.all_wrong_letters - set(self.all_correct_positions.values())
                
                sample_size = min(100, len(self.current_words))
                word_scores = {}
                
                for word in self.current_words[:sample_size]:
                    # Base entropy score
                    entropy_score = self.calculate_entropy(word, self.current_words)
                    
                    # Bonus for testing new letters
                    unique_unused = len(set(word) & unused_letters)
                    unused_bonus = unique_unused * 0.5
                    
                    # Bonus for common letters in remaining positions - maybe im schizo but i swear these come up more
                    unknown_positions = set(range(5)) - set(self.all_correct_positions.keys())
                    position_score = sum(0.3 for i in unknown_positions if word[i] in 'etaoinshrdl')
                    
                    word_scores[word] = entropy_score + unused_bonus + position_score
                
                best_word = max(word_scores.items(), key=lambda x: x[1])[0]
        
        self.used_words.add(best_word)
        self.suggestion_label.configure(text=f"Suggested word: {best_word}")
        for i, letter in enumerate(best_word):
            self.letter_entries[i].delete(0, tk.END)
            self.letter_entries[i].insert(0, letter.upper())
        self.letter_entries[0].focus()

def main():
    app = WordleSolverGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
