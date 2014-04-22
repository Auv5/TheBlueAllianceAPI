import main
import scrapev2

def main_f():
    regional = scrapev2.download_regional(main.read_regional())

    main.to_csv(dict(regional.oprs), dict(regional.ccwms), teams)

if __name__ == '__main__':
    main_f()
