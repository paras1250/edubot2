#!/usr/bin/env python3
"""
Add sample quiz questions to the database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.quote import Quiz

def add_sample_quizzes():
    """Add sample quiz questions to the database"""
    
    sample_quizzes = [
        {
            'question': 'What does "HTML" stand for?',
            'option_a': 'Hyper Text Markup Language',
            'option_b': 'High Tech Modern Language',
            'option_c': 'Home Tool Markup Language',
            'option_d': 'Hyperlink and Text Markup Language',
            'correct_answer': 'A',
            'explanation': 'HTML stands for Hyper Text Markup Language, which is the standard markup language for creating web pages.',
            'subject': 'Web Development',
            'difficulty': 'easy',
            'category': 'computer_science',
            'points': 1
        },
        {
            'question': 'Which programming language is known as the "language of the web"?',
            'option_a': 'Python',
            'option_b': 'JavaScript',
            'option_c': 'Java',
            'option_d': 'C++',
            'correct_answer': 'B',
            'explanation': 'JavaScript is widely known as the "language of the web" because it runs in web browsers and enables interactive web pages.',
            'subject': 'Programming',
            'difficulty': 'easy',
            'category': 'computer_science',
            'points': 1
        },
        {
            'question': 'What is the result of 2^3 (2 to the power of 3)?',
            'option_a': '6',
            'option_b': '8',
            'option_c': '9',
            'option_d': '16',
            'correct_answer': 'B',
            'explanation': '2^3 = 2 × 2 × 2 = 8',
            'subject': 'Basic Mathematics',
            'difficulty': 'easy',
            'category': 'mathematics',
            'points': 1
        },
        {
            'question': 'Which of the following is a prime number?',
            'option_a': '15',
            'option_b': '21',
            'option_c': '17',
            'option_d': '25',
            'correct_answer': 'C',
            'explanation': '17 is a prime number because it can only be divided by 1 and itself without a remainder.',
            'subject': 'Number Theory',
            'difficulty': 'medium',
            'category': 'mathematics',
            'points': 2
        },
        {
            'question': 'What is the chemical symbol for water?',
            'option_a': 'H2O',
            'option_b': 'CO2',
            'option_c': 'NaCl',
            'option_d': 'CH4',
            'correct_answer': 'A',
            'explanation': 'Water is composed of two hydrogen atoms and one oxygen atom, hence H2O.',
            'subject': 'Chemistry',
            'difficulty': 'easy',
            'category': 'science',
            'points': 1
        },
        {
            'question': 'Which planet is known as the "Red Planet"?',
            'option_a': 'Venus',
            'option_b': 'Mars',
            'option_c': 'Jupiter',
            'option_d': 'Saturn',
            'correct_answer': 'B',
            'explanation': 'Mars is called the "Red Planet" because of its reddish appearance due to iron oxide on its surface.',
            'subject': 'Astronomy',
            'difficulty': 'easy',
            'category': 'science',
            'points': 1
        },
        {
            'question': 'Who wrote the famous novel "Pride and Prejudice"?',
            'option_a': 'Charlotte Brontë',
            'option_b': 'Jane Austen',
            'option_c': 'Emily Dickinson',
            'option_d': 'Virginia Woolf',
            'correct_answer': 'B',
            'explanation': 'Jane Austen wrote "Pride and Prejudice," published in 1813.',
            'subject': 'English Literature',
            'difficulty': 'medium',
            'category': 'literature',
            'points': 2
        },
        {
            'question': 'In which year did World War II end?',
            'option_a': '1944',
            'option_b': '1945',
            'option_c': '1946',
            'option_d': '1947',
            'correct_answer': 'B',
            'explanation': 'World War II ended in 1945 with the surrender of Japan in September.',
            'subject': 'World History',
            'difficulty': 'medium',
            'category': 'history',
            'points': 2
        },
        {
            'question': 'What is the time complexity of binary search?',
            'option_a': 'O(n)',
            'option_b': 'O(log n)',
            'option_c': 'O(n²)',
            'option_d': 'O(1)',
            'correct_answer': 'B',
            'explanation': 'Binary search has O(log n) time complexity because it eliminates half of the search space in each iteration.',
            'subject': 'Data Structures',
            'difficulty': 'hard',
            'category': 'computer_science',
            'points': 3
        },
        {
            'question': 'What is the capital of Australia?',
            'option_a': 'Sydney',
            'option_b': 'Melbourne',
            'option_c': 'Canberra',
            'option_d': 'Perth',
            'correct_answer': 'C',
            'explanation': 'Canberra is the capital city of Australia, not Sydney or Melbourne as many people think.',
            'subject': 'Geography',
            'difficulty': 'medium',
            'category': 'general',
            'points': 2
        }
    ]
    
    app = create_app()
    with app.app_context():
        try:
            # Clear existing quiz data (optional)
            Quiz.query.delete()
            
            # Add sample quizzes
            for quiz_data in sample_quizzes:
                quiz = Quiz(**quiz_data)
                db.session.add(quiz)
            
            db.session.commit()
            print(f"✅ Successfully added {len(sample_quizzes)} sample quiz questions!")
            
            # Display summary
            print("\n📊 Quiz Summary by Category:")
            categories = {}
            for quiz in sample_quizzes:
                cat = quiz['category']
                if cat not in categories:
                    categories[cat] = {'count': 0, 'difficulties': set()}
                categories[cat]['count'] += 1
                categories[cat]['difficulties'].add(quiz['difficulty'])
            
            for category, info in categories.items():
                difficulties = ', '.join(sorted(info['difficulties']))
                print(f"  • {category.replace('_', ' ').title()}: {info['count']} questions ({difficulties})")
            
        except Exception as e:
            print(f"❌ Error adding sample quizzes: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_sample_quizzes()
