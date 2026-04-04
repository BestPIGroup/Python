import psutil
import json
import csv
import time
from datetime import datetime

with open("Python/banco.json", "r", encoding="utf-8") as file:
    dados = json.load(file)

