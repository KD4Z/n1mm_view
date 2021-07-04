#!/usr/bin/python3

"""
This script allows you to view ONE of the graphs relatively quickly, mostly for debugging the graph generators.
"""

import logging
import pygame
import sqlite3
import sys
import time

import config
import dataaccess
import graphics

__author__ = 'Jeffrey B. Otterson, N1KDO'
__copyright__ = 'Copyright 2016, 2017, 2019 Jeffrey B. Otterson'
__license__ = 'Simplified BSD'

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=config.LOG_LEVEL)
logging.Formatter.converter = time.gmtime


def main():
    logging.info('dashboard startup')
    try:
        screen, size = graphics.init_display()
    except Exception as e:
        logging.exception('Could not initialize display.', exc_info=e)
        sys.exit(1)

    display_size = (size[0], size[1])

    logging.debug('display setup')

    qso_operators = []
    qso_stations = []
    qso_band_modes = []
    operator_qso_rates = []
    qsos_per_hour = []
    qsos_by_section = {}

    logging.debug('load data')
    db = None
    cursor = None
    try:
        logging.debug('connecting to database')
        db = sqlite3.connect(config.DATABASE_FILENAME)
        cursor = db.cursor()
        logging.debug('database connected')

        # get timestamp from the last record in the database
        last_qso_time, message = dataaccess.get_last_qso(cursor)

        # load qso_operators
        qso_operators = dataaccess.get_operators_by_qsos(cursor)

        # load qso_stations -- maybe useless chartjunk
        qso_stations = dataaccess.get_station_qsos(cursor)

        # get something else.
        qso_band_modes = dataaccess.get_qso_band_modes(cursor)

        # load QSOs per Hour by Operator
        operator_qso_rates = dataaccess.get_qsos_per_hour_per_operator(cursor, last_qso_time)

        # load QSO rates per Hour by Band
        qsos_per_hour, qsos_per_band = dataaccess.get_qsos_per_hour_per_band(cursor)

        # load QSOs by Section
        qsos_by_section = dataaccess.get_qsos_by_section(cursor)

        logging.debug('load data done')
    except sqlite3.OperationalError as error:
        logging.exception(error)
        sys.exit(1)
    finally:
        if db is not None:
            logging.debug('Closing DB')
            cursor.close()
            db.close()
            db = None

    try:
        # image_data, image_size = graphics.qso_summary_table(size, qso_band_modes)
        # image_data, image_size = graphics.qso_rates_table(size, operator_qso_rates)
        # image_data, image_size = graphics.qso_operators_graph(size, qso_operators)
        # image_data, image_size = graphics.qso_operators_table(size, qso_operators)
        # image_data, image_size = graphics.qso_stations_graph(size, qso_stations)
        # image_data, image_size = graphics.qso_bands_graph(size, qso_band_modes)
        # image_data, image_size = graphics.qso_modes_graph(size, qso_band_modes)
        # image_data, image_size = graphics.qso_rates_chart(size, qsos_per_hour)
        image_data, image_size = graphics.draw_map(size, qsos_by_section)
        #  gc.collect()

        image = pygame.image.frombuffer(image_data, image_size, 'RGB')
        graphics.show_graph(screen, size, image)
        pygame.display.flip()

        # wait for a Q key press
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == ord('q'):
                        logging.debug('Q key pressed')
                        run = False
                    else:
                        logging.debug('event key=%d', event.key)

    except Exception as e:
        logging.exception("Exception in main:", exc_info=e)

    pygame.display.quit()
    logging.info('one_chart exit')


if __name__ == '__main__':
    main()
