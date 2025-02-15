import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///stock.db'
    #solo para redeployar
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.klfeqyqhpglowmigmmpw:8lnNmvbiaCNfey0i@aws-0-sa-east-1.pooler.supabase.com:6543/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
