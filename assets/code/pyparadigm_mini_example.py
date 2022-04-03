import pyparadigm as pp
import pygame as pg
import pandas as pd

import time
import datetime

gray = 0x969696
black = 0
white = 0xFFFFFF


def display_text(text, bg_color):
    pp.display(pp.compose(pp.empty_surface(bg_color))(
        pp.Text(text, pp.Font(size=60), color=pp.rgba(white))
    ))


def run_experiment():
    el = pp.EventListener()
    keys_mappings = {pg.K_q: "q", pg.K_n: "n"}
    result_key = None
    results = []
    while result_key != "q":
        display_text("press any key to start", gray)
        el.wait_for_unicode_char()
        display_text("press [ q ] to exit\npress [ n ] to continue", black)
        start_time = time.time()
        code = el.wait_for_keys(*keys_mappings)
        result_key = keys_mappings[code]
        rt = time.time() - start_time
        print(f"You pressed the {result_key} key on {rt:.3} seconds")
        results.append((result_key, rt))
    return results


def main():
    pp.init((300, 300), display_pos=(200, 200))
    results = run_experiment()
    outfile = 'experiment_' + str(datetime.date.today()) + '.csv'
    pd.DataFrame(results, columns=["Key", "Time"]).to_csv(outfile)
    print("Experiment saved as:", outfile)


if __name__ == "__main__":
    main()
