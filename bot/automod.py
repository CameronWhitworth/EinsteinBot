import json
import os
from typing import List, Set

class AutoMod:
    def __init__(self, ban_list_file: str = "bot/banned_words.json"):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.ban_list_file = os.path.join(script_dir, "banned_words.json")
        self.banned_words: Set[str] = self.load_ban_list()
    
    def load_ban_list(self) -> Set[str]:
        """Load banned words from JSON file."""
        if os.path.exists(self.ban_list_file):
            try:
                with open(self.ban_list_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(word.lower() for word in data.get('words', []))
            except (json.JSONDecodeError, IOError):
                return set()
        return set()
    
    def save_ban_list(self):
        """Save banned words to JSON file."""
        data = {'words': sorted(list(self.banned_words))}
        try:
            with open(self.ban_list_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving ban list: {e}")
    
    def add_word(self, word: str) -> bool:
        """Add a word to the ban list. Returns True if added, False if already exists."""
        word_lower = word.lower().strip()
        if word_lower and word_lower not in self.banned_words:
            self.banned_words.add(word_lower)
            self.save_ban_list()
            return True
        return False
    
    def remove_word(self, word: str) -> bool:
        """Remove a word from the ban list. Returns True if removed, False if not found."""
        word_lower = word.lower().strip()
        if word_lower in self.banned_words:
            self.banned_words.remove(word_lower)
            self.save_ban_list()
            return True
        return False
    
    def get_all_words(self) -> List[str]:
        """Get all banned words as a sorted list."""
        return sorted(list(self.banned_words))
    
    def check_message(self, message_content: str) -> List[str]:
        """
        Check if message contains any banned words.
        Returns list of banned words found (empty if none found).
        """
        message_lower = message_content.lower()
        found_words = []
        
        for banned_word in self.banned_words:
            if banned_word in message_lower:
                found_words.append(banned_word)
        
        return found_words
    
    def filter_message(self, message_content: str) -> str:
        """
        Filter banned words in a message, keeping first and last letter visible,
        replacing middle characters with #.
        Example: "stock" -> "s###k"
        """
        filtered_content = message_content
        message_lower = message_content.lower()
        
        # Find all occurrences of banned words and store their positions
        # Process from end to beginning to preserve indices
        replacements = []
        
        for banned_word in self.banned_words:
            start_idx = 0
            while True:
                idx = message_lower.find(banned_word, start_idx)
                if idx == -1:
                    break
                
                # Get the actual word from the original message (preserving case)
                actual_word = message_content[idx:idx + len(banned_word)]
                
                # Filter the word: keep first and last letter, replace middle with #
                if len(actual_word) <= 1:
                    filtered_word = "#"
                elif len(actual_word) == 2:
                    filtered_word = actual_word[0] + "#"
                else:
                    # Keep first letter, replace middle with #, keep last letter
                    filtered_word = actual_word[0] + "#" * (len(actual_word) - 2) + actual_word[-1]
                
                replacements.append((idx, len(actual_word), filtered_word))
                start_idx = idx + 1
        
        # Sort by index in reverse order to replace from end to beginning
        replacements.sort(key=lambda x: x[0], reverse=True)
        
        # Apply replacements
        for idx, length, replacement in replacements:
            filtered_content = filtered_content[:idx] + replacement + filtered_content[idx + length:]
        
        return filtered_content

