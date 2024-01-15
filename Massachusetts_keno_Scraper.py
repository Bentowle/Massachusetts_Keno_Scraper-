import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, scrolledtext

def scrape_keno_results():
    url = 'https://www.kenomaster.com/results/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results_table = soup.find('table', {'class': 'table-bordered'})

        if results_table:
            numbers_count = {}
            winning_numbers_list = []
            for row in results_table.find_all('tr')[1:]:
                columns = row.find_all('td')
                game_number = columns[0].text.strip()
                winning_numbers = columns[1].text.strip()

                # Count occurrences of each number
                for number in winning_numbers.split('-'):
                    numbers_count[number] = numbers_count.get(number, 0) + 1

                # Add winning numbers to the list (comma-separated)
                winning_numbers_list.append(winning_numbers.replace('-', ','))

            return numbers_count, winning_numbers_list
        else:
            return ["Results table not found on the page."]
    else:
        return [f"Failed to retrieve the page. Status code: {response.status_code}"]

class KenoResultsApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Keno Results")

        # Top-left text widget for frequency of each number
        self.top_left_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=30, height=15)
        self.top_left_text.grid(row=0, column=0, padx=10, pady=10)

        # Top-right text widget for Winning Numbers for All Games
        self.top_right_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=15)
        self.top_right_text.grid(row=0, column=1, padx=10, pady=10, columnspan=2)

        # Bottom-left text widget for Last 20 Repeats
        self.bottom_left_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=15)
        self.bottom_left_text.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        # Bottom-right text widget for Hot Numbers
        self.bottom_right_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=30, height=15)
        self.bottom_right_text.grid(row=1, column=2, padx=10, pady=10)

        self.fetch_button = tk.Button(master, text="Fetch Results", command=self.fetch_results)
        self.fetch_button.grid(row=2, column=0, pady=10, columnspan=3)

    def fetch_results(self):
        numbers_count, winning_numbers_list = scrape_keno_results()

        # Clear previous results
        self.top_left_text.delete(1.0, tk.END)
        self.top_right_text.delete(1.0, tk.END)
        self.bottom_left_text.delete(1.0, tk.END)
        self.bottom_right_text.delete(1.0, tk.END)

        # Display frequency of each number on the top-left
        self.top_left_text.insert(tk.END, "Numbers and Their Frequencies (Most to Least):\n")
        for number, count in sorted(numbers_count.items(), key=lambda x: x[1], reverse=True):
            self.top_left_text.insert(tk.END, "{}: {} times\n".format(number, count))

        # Display winning numbers with commas in the top-right
        self.top_right_text.insert(tk.END, "Winning Numbers for All Games:\n")
        for winning_numbers in winning_numbers_list:
            self.top_right_text.insert(tk.END, "{}\n".format(winning_numbers))

        # Display the last 20 numbers that repeated
        self.bottom_left_text.insert(tk.END, "Last 20 Repeats:\n")
        for number, count in sorted(numbers_count.items(), key=lambda x: x[1], reverse=True)[:20]:
            self.bottom_left_text.insert(tk.END, "{}: {} times\n".format(number, count))

        # Display the current hot number in the bottom-right text widget
        hot_number = max(numbers_count, key=numbers_count.get)
        self.bottom_right_text.insert(tk.END, "Current Hot Number: {}\n".format(hot_number))

        # Display the 19 numbers that came out in games with the hot_number the most
        self.bottom_right_text.insert(tk.END, "\nNumbers that came out in games with {} the most:\n".format(hot_number))
        games_with_hot_number = [game for game in winning_numbers_list if hot_number in game.split(',')]
        numbers_in_games_with_hot_number = [num for game in games_with_hot_number for num in game.split(',') if num != hot_number]
        numbers_count_in_games_with_hot_number = {num: numbers_in_games_with_hot_number.count(num) for num in set(numbers_in_games_with_hot_number)}
        
        for number, count in sorted(numbers_count_in_games_with_hot_number.items(), key=lambda x: x[1], reverse=True)[:19]:
            self.bottom_right_text.insert(tk.END, "{}: {} times\n".format(number, count))

def main():
    root = tk.Tk()
    app = KenoResultsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
