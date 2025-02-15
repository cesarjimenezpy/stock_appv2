import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///stock.db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:8lnNmvbiaCNfey0i@db.klfeqyqhpglowmigmmpw.supabase.co:5432/postgres'
    #postgresql://postgres:[YOUR-PASSWORD]@db.klfeqyqhpglowmigmmpw.supabase.co:5432/postgres
    SQLALCHEMY_TRACK_MODIFICATIONS = False
