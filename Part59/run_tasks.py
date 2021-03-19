import schedule
from data_prep import save_file

schedule.every(1).minutes.do(save_file)

if __name__ == "__main__":
    save_file()
    while True:
        schedule.run_pending()