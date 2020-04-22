import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json
import argparse
import numpy as np
import os 
from matplotlib.widgets import CheckButtons

def plotWorker(worker_file, worker_id, plt):
    """
    plot worker timeline with trace file (worker_file)
    """
    # Parse trace file and load it to a dataframe.
    with open(worker_file) as f:
        data = json.load(f)
    timeunit = data['displayTimeUnit']
    events = data['traceEvents']
    index = 0
    while len(events[index])!=6:
        index+=1
    df = pd.DataFrame(events[index:])
    # Extract information and obtain essential event information
    df.ts = df.ts - df.ts.iloc[0]
    operators = df[df.cat=='operator']
    operators.loc[:, 'ts'] = (operators.ts - operators.ts.iloc[0])*1000
    operator_type = operators.name.drop_duplicates().values
    for t in operator_type:
        if t[0]=="_":
            operators = operators[operators.name!=t]
        elif t[0]=="[":
            if "backward" in t:
                operators.loc[operators.name==t, ["name"]] = "backward"
            else:
                operators.loc[operators.name==t, ["name"]] = "foreward"        
    operator_type = operators.name.drop_duplicates().values
    ret = []
    # Add events to worker timeline.
    for o in operator_type:
        event = operators[operators.name==o].sort_values(by='ts')
        if o =='KVStoreDistDefaultPush':
            ret.append(plt.scatter(event.ts, [worker_id]*len(event), visible=False, label=worker_id+"_"+o[ -4:] , marker="|", color="red"))
        elif o == 'KVStoreDistDefaultStoragePull':
            ret.append(plt.scatter(event.ts, [worker_id]*len(event), visible=False,label=worker_id + "_"+ o[-4:] , marker="|", color="green"))
        elif o =='backward':
            ret.append(plt.scatter(event.ts, [worker_id]*len(event), visible=False, label=worker_id+"_"+o , marker=".", color="yellow"))
        elif o == 'foreward':
            ret.append(plt.scatter(event.ts, [worker_id]*len(event), visible=False, label=worker_id + "_"+ o , marker=".", color="blue"))
    return ret


def plotServer(server_file, plt):
    """
    plot parameter server timeline with trace file (worker_file)
    """
    with open(server_file) as f:
        data = json.load(f)
    timeunit = data['displayTimeUnit']
    events = data['traceEvents']
    index = 0
    while len(events[index])!=6:
        index+=1
    ret = []
    df = pd.DataFrame(events[index:])
    # Extract information and obtain essential event information
    df.ts = df.ts - df.ts.iloc[0]
    operators = df[df.cat=='operator']
    operators.loc[:, 'ts'] = (operators.ts - operators.ts.iloc[0])*1000
    operator_type = operators.name.drop_duplicates().values
    for t in operator_type:
        if t[0]=="_":
            operators = operators[operators.name!=t]
    operator_type = operators.name.drop_duplicates().values
    # Add events to parameter server timeline.
    for o in operator_type:
        event = operators[operators.name==o].sort_values(by='ts')
        ret.append(plt.scatter(event.ts, ["server"]*len(event), marker="|", label=o ))
    return ret

def func(label):
    """
    Define user interface function
    """
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    plt.draw()

parser = argparse.ArgumentParser(description='Plot mxnet trace')
parser.add_argument('--input', '-i', help="directory of input files")
parser.add_argument('--output', '-o', help="output of plot")
opt = parser.parse_args()

# search all trace files under input directory
files = []
for (dirpath, dirnames, filenames) in os.walk(opt.input):
    files.extend(filenames)
files = sorted(files)

# plot events from traces
fig, ax = plt.subplots()
plt.xlabel("timestamp (s)")
worker_id = 0
lines = []
for f in files:
    if "worker" in f:
        ret = plotWorker(os.path.join(opt.input, f), "worker_"+str(worker_id) ,plt=ax)
        worker_id+=1
    if "server" in f:
        ret = plotServer(os.path.join(opt.input, f), plt=ax)
    lines.extend(ret)

# add controllers
rax = plt.axes([0.05, 0.4, 0.2, 0.6])
labels = [str(line.get_label()) for line in lines]
visibility = [line.get_visible() for line in lines]
check = CheckButtons(rax, labels, visibility)
check.on_clicked(func)
plt.subplots_adjust(left=0.3)


if opt.output!=None:
    plt.savefig(opt.output)
else:
    plt.show()
