#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import db
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime
import argparse


def main(args):
    with open(args.config) as infile:
        config = json.load(infile)

    database = db.Database(args.database)

    # unique_hosts = {host.hostname for host in session.query(Host)}
    unique_hosts = database.unique_hosts()
    if not unique_hosts:
        raise ValueError('No hosts found. Are the logs in the correct format?')

    timeseries = defaultdict(list)
    x = []
    for event in database.get_events():
        x.append(event.timestamp)
        observed_hostnames = {
            hostname
            for hostname in database.get_hosts(event)
        }
        for hostname in unique_hosts:
            if hostname in observed_hostnames:
                timeseries[hostname].append(1)
            else:
                timeseries[hostname].append(0)

    df = pd.DataFrame(timeseries,
                      index=[datetime.datetime.fromtimestamp(i) for i in x])
    df = df.drop(config['hosts_to_ignore'], axis=1)
    df = df.rename(columns=config['host_rename_mapping'])

    now = datetime.datetime.now()
    beginning = now - datetime.timedelta(days=1)
    fig, axis = plt.subplots()
    df.resample('H').plot(ax=axis)
    axis.set(xlabel='Time', ylabel='Up', xlim=(beginning, now), ylim=(0, 1.1))
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    parser.add_argument('-c', '--config',
                        required=False,
                        default='config.json')
    main(parser.parse_args())
