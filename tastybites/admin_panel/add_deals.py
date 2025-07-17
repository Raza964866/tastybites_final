#!/usr/bin/env python3
"""
Script to add sample deals items to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tastybites.backend.app import app
from tastybites.backend.models import db, MenuItem

def add_deals():
    with app.app_context():
        # Check if deals already exist
        existing_deals = MenuItem.query.filter_by(category='Deals').first()
        if existing_deals:
            print("Deals already exist in the database!")
            return
        
        # Sample deals items
        deals_items = [
            {
                'name': 'Combo Deal - Burger & Fries',
                'description': 'Get a delicious burger with crispy fries at a special discounted price!',
                'price': 8.99,
                'category': 'Deals',
                'image': 'combo-deal.jpg'
            },
            {
                'name': 'Pizza Special - Large 2 Toppings',
                'description': 'Large pizza with your choice of 2 toppings for an unbeatable price!',
                'price': 15.99,
                'category': 'Deals',
                'image': 'pizza-special.jpg'
            },
            {
                'name': 'Family Feast',
                'description': 'Perfect for sharing! 2 burgers, 2 sides, 2 drinks and dessert.',
                'price': 24.99,
                'category': 'Deals',
                'image': 'family-feast.jpg'
            },
            {
                'name': 'Weekend Special',
                'description': 'Weekend only! Get any main course with a drink and dessert.',
                'price': 12.99,
                'category': 'Deals',
                'image': 'weekend-special.jpg'
            },
            {
                'name': 'Lunch Deal',
                'description': 'Perfect for lunch! Any salad with a drink and bread roll.',
                'price': 7.99,
                'category': 'Deals',
                'image': 'lunch-deal.jpg'
            }
        ]
        
        print("Adding deals items to the database...")
        
        for deal_data in deals_items:
            # Check if the item already exists
            existing_item = MenuItem.query.filter_by(name=deal_data['name']).first()
            if not existing_item:
                deal_item = MenuItem(
                    name=deal_data['name'],
                    description=deal_data['description'],
                    price=deal_data['price'],
                    category=deal_data['category'],
                    image=deal_data['image'],
                    is_available=True
                )
                db.session.add(deal_item)
                print(f"Added: {deal_data['name']}")
            else:
                print(f"Skipped: {deal_data['name']} (already exists)")
        
        try:
            db.session.commit()
            print("Successfully added deals items to the database!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding deals items: {e}")

if __name__ == "__main__":
    add_deals()
