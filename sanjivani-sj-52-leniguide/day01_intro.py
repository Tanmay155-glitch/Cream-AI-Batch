#!/usr/bin/env python3
"""
day01_intro.py — LeniGuide Introduction Script
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, CSE AI & ML)
Project: SJ-52 | Product: LeniGuide
"""

project_name = "LeniGuide"
student = "Tanmay Subhash Gawali"
reg_no = "2124UMLM2016"
branch = "CSE AI & ML"
project_id = "SJ-52"
theme = "Travel & Culture"
product = "Cave-by-cave guide to Ajanta and Ellora UNESCO World Heritage Sites"
target_user = "School history teacher from Kopargaon planning a 2-day study tour"
safety_note = "Timings, fees and closures can change. Confirm on asi.nic.in before you travel."

print("=" * 60)
print(f"  {project_name} — Project Card")
print("=" * 60)
print(f"  Student:    {student}")
print(f"  Reg No:     {reg_no}")
print(f"  Branch:     {branch}")
print(f"  Project ID: {project_id}")
print(f"  Theme:      {theme}")
print(f"  Product:    {product}")
print(f"  User:       {target_user}")
print("=" * 60)

user_name = input("\nWhat is your name? ")
user_question = input("What would you like to know about Ajanta or Ellora? ")

print(f'\nHello {user_name}! You asked: "{user_question}"')
print("LeniGuide will help you plan your visit to these UNESCO heritage caves.")
print(f"\n⚠️  {safety_note}")
