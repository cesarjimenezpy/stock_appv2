import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///stock.db'
    #solo para redeployar
    SQLALCHEMY_DATABASE_URI = 'postgresql://neondb_owner:npg_g7J9PuqMaEYs@ep-noisy-snow-acje39qt-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
